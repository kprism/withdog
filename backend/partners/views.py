from io import BytesIO
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET,require_POST
from openpyxl import load_workbook
from .models import Partner,PartnerCategory

@require_GET
def partner_list(request):
    qs=Partner.objects.filter(is_active=True).select_related('category')
    category=request.GET.get('category'); city=request.GET.get('city'); q=request.GET.get('q')
    if category: qs=qs.filter(category__code=category)
    if city: qs=qs.filter(city=city)
    if q: qs=qs.filter(name__icontains=q)
    data=[{'id':p.id,'name':p.name,'address':p.address,'phone':p.phone,'city':p.city,'category':p.category.code,'category_name':p.category.name,'latitude':float(p.latitude) if p.latitude is not None else None,'longitude':float(p.longitude) if p.longitude is not None else None,'is_affiliated':p.is_affiliated} for p in qs[:2000]]
    return JsonResponse({'count':qs.count(),'results':data})

@staff_member_required
@require_POST
def import_excel(request):
    f=request.FILES.get('file')
    if not f: return JsonResponse({'error':'엑셀 파일이 필요합니다.'},status=400)
    category_code=request.POST.get('category','grooming')
    category_name=request.POST.get('category_name','미용센터')
    cat,_=PartnerCategory.objects.get_or_create(code=category_code,defaults={'name':category_name})
    wb=load_workbook(BytesIO(f.read()),data_only=True)
    created=updated=skipped=0
    for ws in wb.worksheets:
        city=ws.title.rstrip('0123456789')
        for row in ws.iter_rows(min_row=4,values_only=True):
            if len(row)<3 or not row[1] or not row[2]: skipped+=1; continue
            name=str(row[1]).strip(); address=str(row[2]).strip(); phone=str(row[3]).strip() if len(row)>3 and row[3] else ''
            obj,was_created=Partner.objects.update_or_create(category=cat,name=name,address=address,defaults={'phone':phone,'city':city,'source':f.name,'is_active':True})
            created+=int(was_created); updated+=int(not was_created)
    return JsonResponse({'ok':True,'created':created,'updated':updated,'skipped':skipped})

@require_POST
def save_coordinates(request,pk):
    # 좌표 저장은 관리자/운영 API에서만 호출하도록 배포 시 인증을 강화한다.
    try: p=Partner.objects.get(pk=pk)
    except Partner.DoesNotExist: return JsonResponse({'error':'not found'},status=404)
    p.latitude=request.POST.get('latitude') or None; p.longitude=request.POST.get('longitude') or None; p.save(update_fields=['latitude','longitude','updated_at'])
    return JsonResponse({'ok':True})
