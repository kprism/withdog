from pathlib import Path
from tempfile import NamedTemporaryFile

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from openpyxl import load_workbook

from .models import Partner, PartnerCategory


def _import_partner_workbook(uploaded_file, category):
    created = updated = skipped = 0
    with NamedTemporaryFile(suffix=Path(uploaded_file.name).suffix or '.xlsx') as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp.flush()
        wb = load_workbook(tmp.name, data_only=True, read_only=True)
        for ws in wb.worksheets:
            city = ws.title.rstrip('0123456789').strip()
            for row in ws.iter_rows(min_row=4, values_only=True):
                if len(row) < 3 or not row[1] or not row[2]:
                    skipped += 1
                    continue
                name = str(row[1]).strip()
                address = str(row[2]).strip()
                phone = str(row[3]).strip() if len(row) > 3 and row[3] else ''
                _, is_new = Partner.objects.update_or_create(
                    category=category,
                    name=name,
                    address=address,
                    defaults={
                        'phone': phone,
                        'city': city,
                        'source': uploaded_file.name,
                        'is_active': True,
                    },
                )
                created += int(is_new)
                updated += int(not is_new)
    return created, updated, skipped


@staff_member_required

def dashboard_home(request):
    total = Partner.objects.count()
    active = Partner.objects.filter(is_active=True).count()
    affiliated = Partner.objects.filter(is_affiliated=True).count()
    no_coordinates = Partner.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True)).count()
    categories = PartnerCategory.objects.annotate(partner_count=Count('partners')).order_by('sort_order', 'name')
    recent = Partner.objects.select_related('category').order_by('-updated_at')[:8]
    return render(request, 'dashboard/home.html', {
        'total': total,
        'active': active,
        'affiliated': affiliated,
        'no_coordinates': no_coordinates,
        'categories': categories,
        'recent': recent,
    })


@staff_member_required

def partner_list(request):
    qs = Partner.objects.select_related('category').all()
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    city = request.GET.get('city', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(address__icontains=q) | Q(phone__icontains=q))
    if category:
        qs = qs.filter(category__code=category)
    if city:
        qs = qs.filter(city=city)
    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/partner_list.html', {
        'page': page,
        'q': q,
        'selected_category': category,
        'selected_city': city,
        'categories': PartnerCategory.objects.order_by('sort_order', 'name'),
        'cities': Partner.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city'),
    })


@staff_member_required

def partner_upload(request):
    categories = PartnerCategory.objects.order_by('sort_order', 'name')
    if request.method == 'POST':
        uploaded = request.FILES.get('excel_file')
        category_id = request.POST.get('category')
        new_code = request.POST.get('new_category_code', '').strip()
        new_name = request.POST.get('new_category_name', '').strip()
        if not uploaded:
            messages.error(request, '엑셀 파일을 선택해 주세요.')
            return redirect('operator_dashboard:partner_upload')
        if not uploaded.name.lower().endswith(('.xlsx', '.xlsm')):
            messages.error(request, 'xlsx 또는 xlsm 파일만 업로드할 수 있습니다.')
            return redirect('operator_dashboard:partner_upload')
        if category_id:
            category = PartnerCategory.objects.filter(pk=category_id).first()
        elif new_code and new_name:
            category, _ = PartnerCategory.objects.get_or_create(code=new_code, defaults={'name': new_name})
        else:
            category = None
        if not category:
            messages.error(request, '업체 분류를 선택하거나 새 분류를 입력해 주세요.')
            return redirect('operator_dashboard:partner_upload')
        try:
            created, updated, skipped = _import_partner_workbook(uploaded, category)
        except Exception as exc:
            messages.error(request, f'엑셀 처리 중 오류가 발생했습니다: {exc}')
            return redirect('operator_dashboard:partner_upload')
        messages.success(request, f'업로드 완료 · 신규 {created}개 · 갱신 {updated}개 · 건너뜀 {skipped}행')
        return redirect('operator_dashboard:partners')
    return render(request, 'dashboard/partner_upload.html', {'categories': categories})
