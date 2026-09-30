from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import ContentItem

SECTIONS={'hero':('메인 비주얼','메인 첫 화면의 이미지·영상 슬라이드'),'intro':('홈페이지 콘텐츠','인트로 카드 영역의 이미지·영상 콘텐츠')}

@staff_member_required
def media_list(request,kind='hero'):
    if kind not in SECTIONS: return redirect('operator_dashboard:website_media',kind='hero')
    title,description=SECTIONS[kind]; q=request.GET.get('q','').strip(); items=ContentItem.objects.filter(kind=kind)
    if q: items=items.filter(Q(title__icontains=q)|Q(label__icontains=q)|Q(body__icontains=q))
    return render(request,'dashboard/website_media_list.html',locals())

@staff_member_required
def media_edit(request,kind,pk=None):
    if kind not in SECTIONS: return redirect('operator_dashboard:website_media',kind='hero')
    title,description=SECTIONS[kind]; item=get_object_or_404(ContentItem,pk=pk,kind=kind) if pk else None
    if request.method=='POST':
        obj=item or ContentItem(kind=kind)
        obj.title=request.POST.get('title','').strip(); obj.label=request.POST.get('label','').strip(); obj.body=request.POST.get('body','').strip(); obj.link=request.POST.get('link','').strip(); obj.sort_order=int(request.POST.get('sort_order') or 0)
        obj.media_type=request.POST.get('media_type','image'); obj.video_url=request.POST.get('video_url','').strip(); obj.autoplay='autoplay' in request.POST; obj.muted='muted' in request.POST; obj.loop='loop' in request.POST; obj.is_published='is_published' in request.POST
        if request.FILES.get('image'): obj.image=request.FILES['image']
        if request.FILES.get('video'): obj.video=request.FILES['video']
        obj.save(); messages.success(request,'홈페이지 미디어가 저장되어 실제 페이지에 반영됩니다.'); return redirect('operator_dashboard:website_media',kind=kind)
    return render(request,'dashboard/website_media_form.html',locals())

@staff_member_required
def media_delete(request,kind,pk):
    if request.method=='POST': get_object_or_404(ContentItem,pk=pk,kind=kind).delete(); messages.success(request,'미디어 항목이 삭제되었습니다.')
    return redirect('operator_dashboard:website_media',kind=kind)
