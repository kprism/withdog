from pathlib import Path
from tempfile import NamedTemporaryFile
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count,Q
from django.shortcuts import redirect,render,get_object_or_404
from django.utils.dateparse import parse_datetime
from openpyxl import load_workbook
from .models import Partner,PartnerCategory,PartnerBenefit,ContentItem

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
LABELS={'notice':'공지사항','community':'자유게시판','breed':'전 세계 견종','intro':'인트로 갤러리','popup':'팝업'}
@staff_member_required
def content_list(request,kind):
 if kind not in LABELS:return redirect('operator_dashboard:home')
 label=LABELS[kind]; q=request.GET.get('q','').strip(); items=ContentItem.objects.filter(kind=kind)
 if q:items=items.filter(Q(title__icontains=q)|Q(body__icontains=q))
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
@staff_member_required
def manage_section(request,section):
 redirects={'notices':'notice','freeboard':'community','breeds':'breed','content':'intro'}
 if section in redirects:return redirect('operator_dashboard:content_list',kind=redirects[section])
 User=get_user_model(); config={'members':('회원 관리','가입 회원 관리',User.objects.filter(is_staff=False),['username','email','date_joined','is_active']),'admins':('관리자 계정','관리자 권한 관리',User.objects.filter(is_staff=True),['username','email','last_login','is_superuser']),'partner-benefits':('제휴 혜택 관리','제휴업체별 혜택 관리',PartnerBenefit.objects.select_related('partner'),['partner','title','description','active']),'dogs':('반려견 등록 관리','반려견 등록 관리',None,[]),'benefits':('회원 혜택 관리','회원 혜택 관리',None,[]),'inquiries':('민원·문의 관리','민원과 문의 관리',None,[])}
 if section not in config:return redirect('operator_dashboard:home')
 section_title,description,qs,fields=config[section]; rows=list(qs[:100]) if qs is not None else []; ready=qs is not None
 return render(request,'dashboard/manage_section.html',locals())
