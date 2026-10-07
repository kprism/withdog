import base64, json, uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_POST
from .models import TossPaymentSetting, PaymentRecord, MemberProfile

def _setting(): return TossPaymentSetting.get_solo()
def _env(s): return 'live' if s.live_enabled else 'test'
def _keys(s, env):
    return (s.live_client_key,s.live_secret_key) if env=='live' else (s.test_client_key,s.test_secret_key)

def create_membership_payment(user):
    s=_setting(); env=_env(s); client,secret=_keys(s,env)
    if not client or not secret: return None,'토스페이먼츠 API 키가 아직 설정되지 않았습니다.'
    rec=PaymentRecord.objects.create(user=user,environment=env,order_id='MEMBER_'+uuid.uuid4().hex[:24],amount=s.annual_fee,order_name='경상남도 반려견 협회 정회원 연회비')
    return {'client_key':client,'order_id':rec.order_id,'amount':rec.amount,'order_name':rec.order_name,'customer_name':getattr(user.member_profile,'name','회원'),'customer_email':user.email},None

def _confirm(rec,payment_key,amount):
    s=_setting(); _,secret=_keys(s,rec.environment)
    if not secret: raise ValueError('결제 시크릿키가 설정되지 않았습니다.')
    if int(amount)!=rec.amount: raise ValueError('결제 금액이 주문 금액과 일치하지 않습니다.')
    auth=base64.b64encode((secret+':').encode()).decode()
    body=json.dumps({'paymentKey':payment_key,'orderId':rec.order_id,'amount':rec.amount}).encode()
    req=Request('https://api.tosspayments.com/v1/payments/confirm',data=body,headers={'Authorization':'Basic '+auth,'Content-Type':'application/json'},method='POST')
    try:
        with urlopen(req,timeout=15) as response: data=json.loads(response.read().decode())
    except HTTPError as e:
        try: detail=json.loads(e.read().decode()).get('message','결제 승인에 실패했습니다.')
        except Exception: detail='결제 승인에 실패했습니다.'
        raise ValueError(detail)
    rec.payment_key=data.get('paymentKey','');rec.status=data.get('status','DONE');rec.method=data.get('method','') or ''
    approved=data.get('approvedAt');rec.approved_at=parse_datetime(approved) if approved else timezone.now();rec.raw_response=data
    rec.save(update_fields=['payment_key','status','method','approved_at','raw_response','updated_at'])
    if rec.status=='DONE':
        p=rec.user.member_profile;p.membership_status='regular';p.regular_member_requested=True;p.save(update_fields=['membership_status','regular_member_requested'])
    return data

@require_GET
def payment_success(request):
    order_id=request.GET.get('orderId',''); payment_key=request.GET.get('paymentKey',''); amount=request.GET.get('amount','0')
    rec=get_object_or_404(PaymentRecord,order_id=order_id)
    try: _confirm(rec,payment_key,amount); ok=True; msg='연회비 결제가 완료되었습니다. 정회원으로 등록되었습니다.'
    except Exception as e: ok=False; msg=str(e)
    return render(request,'public/payment_result.html',{'ok':ok,'message':msg})

@require_GET
def payment_fail(request):
    return render(request,'public/payment_result.html',{'ok':False,'message':request.GET.get('message','결제가 취소되었거나 실패했습니다.')})

@staff_member_required
def payment_settings(request):
    s=_setting()
    if request.method=='POST':
        s.test_client_key=request.POST.get('test_client_key','').strip()
        secret=request.POST.get('test_secret_key','').strip()
        if secret: s.test_secret_key=secret
        s.live_client_key=request.POST.get('live_client_key','').strip()
        secret=request.POST.get('live_secret_key','').strip()
        if secret: s.live_secret_key=secret
        s.live_enabled='live_enabled' in request.POST
        try:s.annual_fee=max(1,int(request.POST.get('annual_fee') or 30000))
        except ValueError:s.annual_fee=30000
        s.save();messages.success(request,'토스페이먼츠 설정이 저장되었습니다.');return redirect('operator_dashboard:payment_settings')
    return render(request,'dashboard/payment_settings.html',{'setting':s})

@staff_member_required
def settlements(request):
    env=request.GET.get('env','test');env=env if env in ('test','live') else 'test'
    rows=PaymentRecord.objects.filter(environment=env,status='DONE').select_related('user','user__member_profile')[:500]
    total=PaymentRecord.objects.filter(environment=env,status='DONE').aggregate(v=Sum('amount'))['v'] or 0
    return render(request,'dashboard/settlements.html',{'rows':rows,'env':env,'total':total})
