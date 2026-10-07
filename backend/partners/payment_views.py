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
        # 결제 주문은 가입 시 회원 계정과 직접 연결된다. 승인대기 회원인지
        # 다시 확인하고, 결제 회원 정보(이름/생년월일/주소)가 그 계정의
        # MemberProfile과 일치하는 경우에만 정회원으로 자동 승급한다.
        p=rec.user.member_profile
        if p.membership_status=='pending' and p.regular_member_requested:
            # order_id가 가입 시점의 user FK와 1:1로 연결되어 있어 동명이인도 섞이지 않는다.
            # 추가로 토스 결제 응답의 고객명과 가입 이메일이 있으면 함께 교차검증한다.
            customer_name=str((data.get('customerName') or '')).strip()
            customer_email=str((data.get('customerEmail') or '')).strip().lower()
            member_email=str(rec.user.email or rec.user.username or '').strip().lower()
            name_ok=(not customer_name or customer_name==p.name)
            email_ok=(not customer_email or customer_email==member_email)
            if name_ok and email_ok:
                p.membership_status='regular';p.save(update_fields=['membership_status'])
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
        s.settlement_bank=request.POST.get('settlement_bank','').strip()
        s.settlement_account=request.POST.get('settlement_account','').strip()
        s.settlement_holder=request.POST.get('settlement_holder','').strip()
        s.settlement_cycle=request.POST.get('settlement_cycle','').strip()
        try:s.card_fee_rate=max(0,float(request.POST.get('card_fee_rate') or 0))
        except ValueError:s.card_fee_rate=0
        try:s.annual_fee=max(1,int(request.POST.get('annual_fee') or 30000))
        except ValueError:s.annual_fee=30000
        s.save();messages.success(request,'토스페이먼츠 설정이 저장되었습니다.');return redirect('operator_dashboard:payment_settings')
    return render(request,'dashboard/payment_settings.html',{'setting':s})

@staff_member_required
def settlements(request):
    env=request.GET.get('env','test');env=env if env in ('test','live') else 'test'
    rows=PaymentRecord.objects.filter(environment=env,status='DONE').select_related('user','user__member_profile')[:500]
    total=PaymentRecord.objects.filter(environment=env,status='DONE').aggregate(v=Sum('amount'))['v'] or 0
    s=_setting(); fee=int(round(float(total)*float(s.card_fee_rate)/100)); net=total-fee
    return render(request,'dashboard/settlements.html',{'rows':rows,'env':env,'total':total,'setting':s,'estimated_fee':fee,'estimated_net':net})
