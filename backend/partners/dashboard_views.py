from pathlib import Path
from tempfile import NamedTemporaryFile
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count,Q
from django.shortcuts import redirect,render,get_object_or_404
from django.utils.dateparse import parse_date,parse_datetime
from openpyxl import load_workbook
from .models import Partner,PartnerCategory,PartnerBenefit,ContentItem,MemberProfile,DogRegistration,MemberBenefit,Inquiry

LABELS={'notice':'공지사항','community':'자유게시판','breed':'전 세계 견종','intro':'인트로 갤러리','popup':'팝업'}

def _import_partner_workbook(uploaded_file,category):
 created=updated=skipped=0
 with NamedTemporaryFile(suffix=Path(uploaded_file.name).suffix or '.xlsx') as tmp:
  for chunk in uploaded_file.chunks(): tmp.write(chunk)
  tmp.flush(); wb=load_workbook(tmp.name,data_only=True,read_only=True)
  for ws in wb.worksheets:
   city=ws.title.rstrip('0123456789').strip()
   for row in ws.iter_rows(min_row=4,values_only=True):
    if len(row)<3 or not row[1] or not row[2]: skipped+=1; continue
    name=str(row[1]).strip(); address=str(row[2]).strip(); phone=str(row[3]).strip() if len(row)>3 and row[3] else ''
    _,new=Partner.objects.update_or_create(category=category,name=name,address=address,defaults={'phone':phone,'city':city,'source':uploaded_file.name,'is_active':True}); created+=int(new); updated+=int(not new)
 return created,updated,skipped

@staff_member_required
def dashboard_home(request):
 total=Partner.objects.count(); active=Partner.objects.filter(is_active=True).count(); affiliated=Partner.objects.filter(is_affiliated=True).count(); no_coordinates=Partner.objects.filter(Q(latitude__isnull=True)|Q(longitude__isnull=True)).count(); categories=PartnerCategory.objects.annotate(partner_count=Count('partners')).order_by('sort_order','name'); recent=Partner.objects.select_related('category').order_by('-updated_at')[:8]
 return render(request,'dashboard/home.html',locals())

@staff_member_required
def partner_list(request):
 qs=Partner.objects.select_related('category').all(); q=request.GET.get('q','').strip(); category=request.GET.get('category','').strip(); city=request.GET.get('city','').strip()
 if q: qs=qs.filter(Q(name__icontains=q)|Q(address__icontains=q)|Q(phone__icontains=q))
 if category: qs=qs.filter(category__code=category)
 if city: qs=qs.filter(city=city)
 page=Paginator(qs,30).get_page(request.GET.get('page')); categories=PartnerCategory.objects.order_by('sort_order','name'); cities=Partner.objects.exclude(city='').values_list('city',flat=True).distinct().order_by('city')
 return render(request,'dashboard/partner_list.html',locals())

@staff_member_required
def partner_edit(request,pk=None):
 p=get_object_or_404(Partner,pk=pk) if pk else None; categories=PartnerCategory.objects.order_by('sort_order','name')
 if request.method=='POST':
  obj=p or Partner(); obj.name=request.POST.get('name','').strip(); obj.address=request.POST.get('address','').strip(); obj.phone=request.POST.get('phone','').strip(); obj.city=request.POST.get('city','').strip(); obj.category=get_object_or_404(PartnerCategory,pk=request.POST.get('category')); obj.latitude=request.POST.get('latitude') or None; obj.longitude=request.POST.get('longitude') or None; obj.is_affiliated='is_affiliated' in request.POST; obj.is_active='is_active' in request.POST; obj.save(); messages.success(request,'업체 정보가 저장되었습니다.'); return redirect('operator_dashboard:partners')
 return render(request,'dashboard/partner_form.html',locals())

@staff_member_required
def partner_delete(request,pk):
 if request.method=='POST': get_object_or_404(Partner,pk=pk).delete(); messages.success(request,'업체가 삭제되었습니다.')
 return redirect('operator_dashboard:partners')

@staff_member_required
def partner_upload(request):
 categories=PartnerCategory.objects.order_by('sort_order','name')
 if request.method=='POST':
  uploaded=request.FILES.get('excel_file'); category_id=request.POST.get('category'); new_code=request.POST.get('new_category_code','').strip(); new_name=request.POST.get('new_category_name','').strip()
  if not uploaded: messages.error(request,'엑셀 파일을 선택해 주세요.'); return redirect('operator_dashboard:partner_upload')
  category=PartnerCategory.objects.filter(pk=category_id).first() if category_id else None
  if not category and new_code and new_name: category,_=PartnerCategory.objects.get_or_create(code=new_code,defaults={'name':new_name})
  if not category: messages.error(request,'업체 분류를 선택하거나 새 분류를 입력해 주세요.'); return redirect('operator_dashboard:partner_upload')
  try: created,updated,skipped=_import_partner_workbook(uploaded,category)
  except Exception as exc: messages.error(request,f'엑셀 처리 오류: {exc}'); return redirect('operator_dashboard:partner_upload')
  messages.success(request,f'업로드 완료 · 신규 {created} · 갱신 {updated} · 건너뜀 {skipped}'); return redirect('operator_dashboard:partners')
 return render(request,'dashboard/partner_upload.html',locals())

@staff_member_required
def content_list(request,kind):
 if kind not in LABELS:return redirect('operator_dashboard:home')
 label=LABELS[kind]; q=request.GET.get('q','').strip(); items=ContentItem.objects.filter(kind=kind)
 if q:items=items.filter(Q(title__icontains=q)|Q(body__icontains=q)|Q(label__icontains=q))
 return render(request,'dashboard/content_list.html',locals())
@staff_member_required
def content_edit(request,kind,pk=None):
 if kind not in LABELS:return redirect('operator_dashboard:home')
 label=LABELS[kind]; item=get_object_or_404(ContentItem,pk=pk,kind=kind) if pk else None
 if request.method=='POST':
  obj=item or ContentItem(kind=kind); obj.title=request.POST.get('title','').strip(); obj.label=request.POST.get('label','').strip(); obj.body=request.POST.get('body','').strip(); obj.link=request.POST.get('link','').strip(); obj.sort_order=int(request.POST.get('sort_order') or 0); obj.is_published='is_published' in request.POST
  if request.FILES.get('image'):obj.image=request.FILES['image']
  obj.popup_start=parse_datetime(request.POST.get('popup_start','')) if request.POST.get('popup_start') else None; obj.popup_end=parse_datetime(request.POST.get('popup_end','')) if request.POST.get('popup_end') else None; obj.save(); messages.success(request,'저장되었습니다. 홈페이지에 즉시 반영됩니다.'); return redirect('operator_dashboard:content_list',kind=kind)
 popup_start=item.popup_start.strftime('%Y-%m-%dT%H:%M') if item and item.popup_start else ''; popup_end=item.popup_end.strftime('%Y-%m-%dT%H:%M') if item and item.popup_end else ''
 return render(request,'dashboard/content_form.html',locals())
@staff_member_required
def content_delete(request,kind,pk):
 if request.method=='POST':get_object_or_404(ContentItem,pk=pk,kind=kind).delete();messages.success(request,'삭제되었습니다.')
 return redirect('operator_dashboard:content_list',kind=kind)

def _section_config(section):
 return {
  'dogs':{'title':'반려견 등록 관리','model':DogRegistration,'search':['dog_name','registration_no','breed','owner__email'],'headers':['반려견','등록번호','견종','보호자','상태','등록일'],'fields':[('owner','보호자','user'),('dog_name','반려견 이름','text'),('registration_no','동물등록번호','text'),('breed','견종','text'),('birth_date','생년월일','date'),('gender','성별','text'),('status','처리상태','dog_status')]},
  'benefits':{'title':'회원 혜택 관리','model':MemberBenefit,'search':['title','description'],'headers':['혜택명','내용','시작일','종료일','상태','순서'],'fields':[('title','혜택명','text'),('description','혜택 내용','textarea'),('valid_from','시작일','date'),('valid_to','종료일','date'),('is_active','노출','checkbox'),('sort_order','정렬순서','number')]},
  'partner-benefits':{'title':'제휴 혜택 관리','model':PartnerBenefit,'search':['partner__name','title','description'],'headers':['업체','혜택명','내용','노출'],'fields':[('partner','제휴업체','partner'),('title','혜택명','text'),('description','혜택 내용','textarea'),('active','노출','checkbox')]},
  'inquiries':{'title':'민원·문의 관리','model':Inquiry,'search':['name','phone','email','subject','body'],'headers':['신청인','연락처','이메일','제목','상태','접수일'],'fields':[('name','신청인','text'),('phone','전화번호','text'),('email','이메일','email'),('subject','제목','text'),('body','문의내용','textarea'),('status','처리상태','inquiry_status'),('admin_memo','관리자 메모','textarea')]},
 } .get(section)

def _row_values(section,obj):
 if section=='dogs': return [obj.dog_name,obj.registration_no or '-',obj.breed or '-',obj.owner.email or obj.owner.username,obj.get_status_display(),obj.created_at.strftime('%Y.%m.%d')]
 if section=='benefits': return [obj.title,obj.description[:50],obj.valid_from or '-',obj.valid_to or '-', '노출' if obj.is_active else '숨김',obj.sort_order]
 if section=='partner-benefits': return [obj.partner.name,obj.title,obj.description[:60],'노출' if obj.active else '숨김']
 if section=='inquiries': return [obj.name,obj.phone or '-',obj.email or '-',obj.subject,obj.get_status_display(),obj.created_at.strftime('%Y.%m.%d')]
 return []

@staff_member_required
def manage_section(request,section):
 redirects={'notices':'notice','freeboard':'community','breeds':'breed','content':'intro'}
 if section in redirects:return redirect('operator_dashboard:content_list',kind=redirects[section])
 if section=='members': return member_list(request)
 if section=='admins': return admin_list(request)
 cfg=_section_config(section)
 if not cfg:return redirect('operator_dashboard:home')
 q=request.GET.get('q','').strip(); qs=cfg['model'].objects.all()
 if q:
  query=Q()
  for f in cfg['search']: query|=Q(**{f+'__icontains':q})
  qs=qs.filter(query)
 rows=[{'id':o.pk,'values':_row_values(section,o)} for o in qs[:200]]
 return render(request,'dashboard/manage_section.html',{'section':section,'section_title':cfg['title'],'headers':cfg['headers'],'rows':rows,'q':q})

@staff_member_required
def section_edit(request,section,pk=None):
 cfg=_section_config(section)
 if not cfg:return redirect('operator_dashboard:home')
 obj=get_object_or_404(cfg['model'],pk=pk) if pk else None
 if request.method=='POST':
  x=obj or cfg['model']()
  for name,label,typ in cfg['fields']:
   v=request.POST.get(name,'')
   if typ=='checkbox': v=name in request.POST
   elif typ=='number': v=int(v or 0)
   elif typ=='date': v=parse_date(v) if v else None
   elif typ=='user': v=get_object_or_404(get_user_model(),pk=v)
   elif typ=='partner': v=get_object_or_404(Partner,pk=v)
   setattr(x,name,v)
  x.save(); messages.success(request,'저장되었습니다.'); return redirect('operator_dashboard:manage_section',section=section)
 users=get_user_model().objects.filter(is_staff=False,is_active=True).order_by('email'); partners=Partner.objects.filter(is_active=True).order_by('name')
 return render(request,'dashboard/section_form.html',{'section':section,'title':cfg['title'],'fields':cfg['fields'],'obj':obj,'users':users,'partners':partners})

@staff_member_required
def section_delete(request,section,pk):
 cfg=_section_config(section)
 if cfg and request.method=='POST': get_object_or_404(cfg['model'],pk=pk).delete(); messages.success(request,'삭제되었습니다.')
 return redirect('operator_dashboard:manage_section',section=section)

@staff_member_required
def member_list(request):
 User=get_user_model(); q=request.GET.get('q','').strip(); qs=User.objects.filter(is_staff=False).select_related('member_profile')
 if q: qs=qs.filter(Q(email__icontains=q)|Q(username__icontains=q)|Q(member_profile__name__icontains=q)|Q(member_profile__phone__icontains=q)|Q(member_profile__region__icontains=q))
 rows=[]
 for u in qs.order_by('-date_joined')[:300]:
  p=getattr(u,'member_profile',None); rows.append({'id':u.pk,'name':p.name if p else u.get_full_name() or '-','birth':p.birth_date if p else '-','gender':p.get_gender_display() if p and p.gender else '-','phone':p.phone if p else '-','email':u.email or u.username,'region':p.region if p else '-','address':p.address_detail if p else '-','grade':p.get_membership_status_display() if p else '일반회원','active':u.is_active,'joined':u.date_joined})
 return render(request,'dashboard/member_list.html',{'rows':rows,'q':q})

@staff_member_required
def member_edit(request,pk=None):
 User=get_user_model(); user=get_object_or_404(User,pk=pk,is_staff=False) if pk else None; profile=getattr(user,'member_profile',None) if user else None
 if request.method=='POST':
  email=request.POST.get('email','').strip(); user=user or User(username=email,email=email); user.username=email; user.email=email; user.is_active='is_active' in request.POST
  if request.POST.get('password'): user.set_password(request.POST['password'])
  elif not user.pk: user.set_unusable_password()
  user.save(); p=profile or MemberProfile(user=user); p.name=request.POST.get('name','').strip(); p.birth_date=parse_date(request.POST.get('birth_date','')) if request.POST.get('birth_date') else None; p.gender=request.POST.get('gender',''); p.phone=request.POST.get('phone','').strip(); p.region=request.POST.get('region','').strip(); p.address_detail=request.POST.get('address_detail','').strip(); p.privacy_agreed='privacy_agreed' in request.POST; p.regular_member_requested='regular_member_requested' in request.POST; p.membership_status=request.POST.get('membership_status','general'); p.save(); messages.success(request,'회원 정보가 저장되었습니다.'); return redirect('operator_dashboard:manage_section',section='members')
 return render(request,'dashboard/member_form.html',locals())

@staff_member_required
def member_withdraw(request,pk):
 if request.method=='POST':
  u=get_object_or_404(get_user_model(),pk=pk,is_staff=False); u.is_active=False; u.save(update_fields=['is_active']); p=getattr(u,'member_profile',None)
  if p: p.membership_status='withdrawn'; p.save(update_fields=['membership_status'])
  messages.success(request,'회원이 탈퇴(비활성) 처리되었습니다. 데이터는 이력 보존을 위해 유지됩니다.')
 return redirect('operator_dashboard:manage_section',section='members')

@staff_member_required
def admin_list(request):
 User=get_user_model(); q=request.GET.get('q','').strip(); qs=User.objects.filter(is_staff=True)
 if q: qs=qs.filter(Q(username__icontains=q)|Q(email__icontains=q)|Q(first_name__icontains=q))
 rows=qs.order_by('-is_superuser','username'); return render(request,'dashboard/admin_list.html',locals())
@staff_member_required
def admin_edit(request,pk=None):
 User=get_user_model(); obj=get_object_or_404(User,pk=pk,is_staff=True) if pk else None
 if request.method=='POST':
  u=obj or User(); u.username=request.POST.get('username','').strip(); u.email=request.POST.get('email','').strip(); u.first_name=request.POST.get('name','').strip(); u.is_staff=True; u.is_active='is_active' in request.POST; u.is_superuser='is_superuser' in request.POST
  if request.POST.get('password'): u.set_password(request.POST['password'])
  elif not u.pk: messages.error(request,'신규 관리자는 비밀번호가 필요합니다.'); return render(request,'dashboard/admin_form.html',locals())
  u.save(); messages.success(request,'관리자 계정이 저장되었습니다.'); return redirect('operator_dashboard:manage_section',section='admins')
 return render(request,'dashboard/admin_form.html',locals())
