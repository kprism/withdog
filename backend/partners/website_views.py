from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404, redirect, render
from .models import ContentItem, SiteSetting, IntroLayer, AboutPageSetting, AboutHistoryItem, AboutOrgItem

def _seo_context(request, title, description, path, *, image='', og_type='website', json_ld=None, robots='index,follow,max-image-preview:large'):
    import json
    from django.utils.html import strip_tags
    s=SiteSetting.get_solo()
    base=(s.canonical_url or 'https://thepetkorea.co.kr/').rstrip('/')
    desc=' '.join(strip_tags(description or '').split())[:300] or (s.meta_description or s.site_subtitle or '')
    try: favicon=request.build_absolute_uri(s.favicon.url) if s.favicon else ''
    except ValueError: favicon=''
    if image and image.startswith('/'): image=base+image
    data={'title':title[:200], 'description':desc, 'canonical':base+path, 'site_name':s.site_name,
          'image':image or s.og_image_url, 'og_type':og_type, 'robots':robots,
          'naver_verification':s.naver_site_verification, 'google_verification':s.google_site_verification,
          'favicon':favicon, 'json_ld':json.dumps(json_ld, ensure_ascii=False) if json_ld else ''}
    return data

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

def _delete_file(field):
    if field:
        field.delete(save=False)

def _hero_redirect(pk=None, anchor='hero-editor'):
    url='/dashboard/website/'
    if pk:
        url += f'?slide={pk}#{anchor}'
    elif anchor:
        url += f'#{anchor}'
    return redirect(url)


def _clamped_int(value, default, minimum, maximum):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, value))

@staff_member_required
def site_settings(request):
    setting = SiteSetting.get_solo()

    if request.method == 'POST':
        action=request.POST.get('action','header_save')

        if action in ('header_save', 'intro_brand_save'):
            setting.site_name=request.POST.get('site_name','').strip() or '경상남도 반려견 협회'
            setting.site_subtitle=request.POST.get('site_subtitle','').strip()
            setting.header_logo_size=_clamped_int(request.POST.get('header_logo_size'),setting.header_logo_size,28,120)
            setting.header_site_name_size=_clamped_int(request.POST.get('header_site_name_size'),setting.header_site_name_size,11,40)
            setting.header_site_name_weight=_clamped_int(request.POST.get('header_site_name_weight'),setting.header_site_name_weight,400,900)
            setting.header_subtitle_size=_clamped_int(request.POST.get('header_subtitle_size'),setting.header_subtitle_size,9,28)
            setting.header_subtitle_weight=_clamped_int(request.POST.get('header_subtitle_weight'),setting.header_subtitle_weight,400,900)
            setting.header_menu_font_size=_clamped_int(request.POST.get('header_menu_font_size'),setting.header_menu_font_size,11,28)
            setting.header_menu_font_weight=_clamped_int(request.POST.get('header_menu_font_weight'),setting.header_menu_font_weight,400,900)
            setting.intro_header_opacity=_clamped_int(request.POST.get('intro_header_opacity'),setting.intro_header_opacity,0,100)
            setting.intro_stage_width=_clamped_int(request.POST.get('intro_stage_width'),setting.intro_stage_width,1280,3840)
            setting.intro_stage_height=_clamped_int(request.POST.get('intro_stage_height'),setting.intro_stage_height,600,2160)
            if request.POST.get('delete_logo') == '1':
                if setting.logo:
                    _delete_file(setting.logo)
                    setting.logo=''
                if setting.logo_video:
                    _delete_file(setting.logo_video)
                    setting.logo_video=''
            if request.FILES.get('logo'):
                if setting.logo:
                    _delete_file(setting.logo)
                if setting.logo_video:
                    _delete_file(setting.logo_video)
                setting.logo=request.FILES['logo']
                setting.logo_video=''
            if request.FILES.get('logo_video'):
                if setting.logo_video:
                    _delete_file(setting.logo_video)
                if setting.logo:
                    _delete_file(setting.logo)
                setting.logo_video=request.FILES['logo_video']
                setting.logo=''
            setting.save()
            messages.success(request,'인트로 상단 브랜드와 기준 캔버스가 저장되었습니다.')
            return redirect('operator_dashboard:website_settings')

        if action == 'layer_add':
            hero=get_object_or_404(ContentItem,pk=request.POST.get('slide_id'),kind='hero')
            layer_type=request.POST.get('layer_type','text')
            if layer_type not in dict(IntroLayer.LAYER_TYPES): layer_type='text'
            current=list(hero.intro_layers.order_by('-z_index','-pk')[:1])
            next_z=(current[0].z_index + 1) if current else 2
            layer=IntroLayer.objects.create(
                hero=hero,
                name=f'Layer {hero.intro_layers.count()+2}',
                layer_type=layer_type,
                z_index=next_z,
                sort_order=next_z,
            )
            messages.success(request,f'{layer.name}가 추가되었습니다.')
            return _hero_redirect(hero.pk,'layer-editor')

        if action in ('layer_save','layer_delete'):
            layer=get_object_or_404(IntroLayer,pk=request.POST.get('layer_id'))
            hero=layer.hero
            if action == 'layer_delete':
                _delete_file(layer.image); _delete_file(layer.video); layer.delete()
                messages.success(request,'선택한 레이어가 삭제되었습니다.')
                return _hero_redirect(hero.pk,'layer-editor')

            layer.name=request.POST.get('name','').strip() or layer.name
            layer.layer_type=request.POST.get('layer_type') if request.POST.get('layer_type') in dict(IntroLayer.LAYER_TYPES) else layer.layer_type
            layer.text=request.POST.get('text','').strip()
            layer.link=request.POST.get('link','').strip()
            layer.x_px=_clamped_int(request.POST.get('x_px'),layer.x_px,-3840,3840)
            layer.y_px=_clamped_int(request.POST.get('y_px'),layer.y_px,-2160,2160)
            layer.width_px=_clamped_int(request.POST.get('width_px'),layer.width_px,10,3840)
            layer.height_px=_clamped_int(request.POST.get('height_px'),layer.height_px,10,2160)
            layer.opacity=_clamped_int(request.POST.get('opacity'),layer.opacity,0,100)
            layer.z_index=_clamped_int(request.POST.get('z_index'),layer.z_index,1,200)
            layer.font_size=_clamped_int(request.POST.get('font_size'),layer.font_size,8,240)
            layer.font_weight=_clamped_int(request.POST.get('font_weight'),layer.font_weight,100,900)
            layer.border_radius=_clamped_int(request.POST.get('border_radius'),layer.border_radius,0,300)
            layer.animation_delay_ms=_clamped_int(request.POST.get('animation_delay_ms'),layer.animation_delay_ms,0,10000)
            layer.animation_duration_ms=_clamped_int(request.POST.get('animation_duration_ms'),layer.animation_duration_ms,100,10000)
            layer.sort_order=_clamped_int(request.POST.get('sort_order'),layer.sort_order,-1000,1000)
            layer.color=(request.POST.get('color') or '#ffffff').strip()
            layer.background=(request.POST.get('background') or 'transparent').strip()
            layer.object_fit=request.POST.get('object_fit') if request.POST.get('object_fit') in dict(IntroLayer.OBJECT_FITS) else 'contain'
            layer.animation=request.POST.get('animation') if request.POST.get('animation') in dict(IntroLayer.ANIMATIONS) else 'fade-up'
            layer.is_visible='is_visible' in request.POST
            if request.FILES.get('image'):
                _delete_file(layer.image); layer.image=request.FILES['image']
            if request.FILES.get('video'):
                _delete_file(layer.video); layer.video=request.FILES['video']
            layer.save()
            messages.success(request,f'{layer.name}가 저장되었습니다.')
            return _hero_redirect(hero.pk,'layer-editor')

        if action == 'hero_add':
            max_order=ContentItem.objects.filter(kind='hero').aggregate(m=Max('sort_order'))['m'] or 0
            obj=ContentItem.objects.create(
                kind='hero', title=f'슬라이드 {max_order+1}', sort_order=max_order+1,
                media_type='image', is_published=True, autoplay=True, muted=True, loop=True,
                hero_eyebrow=setting.hero_eyebrow, hero_title=setting.hero_title,
                hero_meta1=setting.hero_meta1, hero_meta2=setting.hero_meta2,
                hero_button1_text=setting.hero_button1_text, hero_button1_link=setting.hero_button1_link,
                hero_button2_text=setting.hero_button2_text, hero_button2_link=setting.hero_button2_link,
            )
            messages.success(request,'새 슬라이드가 추가되었습니다. 미디어와 문구를 입력해 주세요.')
            return _hero_redirect(obj.pk)

        if action in ('hero_save','hero_delete','hero_media_delete'):
            obj=get_object_or_404(ContentItem,pk=request.POST.get('slide_id'),kind='hero')
            if action == 'hero_delete':
                _delete_file(obj.image); _delete_file(obj.video); obj.delete()
                messages.success(request,'슬라이드가 삭제되었습니다.')
                return _hero_redirect()

            if action == 'hero_media_delete':
                if request.POST.get('media_selected') != '1':
                    messages.warning(request,'삭제할 미디어를 먼저 선택해 주세요.')
                    return _hero_redirect(obj.pk)
                _delete_file(obj.image)
                _delete_file(obj.video)
                obj.image=''
                obj.image_url=''
                obj.video=''
                obj.video_url=''
                obj.save()
                messages.success(request,'선택한 미디어가 삭제되었습니다. 슬라이드 문구는 유지됩니다.')
                return _hero_redirect(obj.pk)

            obj.media_type=request.POST.get('media_type','image')
            obj.video_url=request.POST.get('video_url','').strip()
            obj.hero_eyebrow=request.POST.get('hero_eyebrow','').strip()
            obj.hero_title=request.POST.get('hero_title','').strip()
            obj.hero_meta1=request.POST.get('hero_meta1','').strip()
            obj.hero_meta2=request.POST.get('hero_meta2','').strip()
            obj.hero_meta1_font_size=_clamped_int(request.POST.get('hero_meta1_font_size'),obj.hero_meta1_font_size,10,40)
            obj.hero_meta2_font_size=_clamped_int(request.POST.get('hero_meta2_font_size'),obj.hero_meta2_font_size,10,40)
            obj.hero_button1_text=request.POST.get('hero_button1_text','').strip()
            obj.hero_button1_link=request.POST.get('hero_button1_link','').strip()
            obj.hero_button2_text=request.POST.get('hero_button2_text','').strip()
            obj.hero_button2_link=request.POST.get('hero_button2_link','').strip()
            try: obj.sort_order=int(request.POST.get('sort_order') or obj.sort_order or 0)
            except ValueError: pass
            obj.is_published='is_published' in request.POST
            obj.autoplay=True; obj.muted=True; obj.loop=True

            if request.FILES.get('image'):
                _delete_file(obj.image); _delete_file(obj.video)
                obj.image=request.FILES['image']; obj.image_url=''; obj.video=''; obj.video_url=''; obj.media_type='image'
            if request.FILES.get('video'):
                _delete_file(obj.video); _delete_file(obj.image)
                obj.video=request.FILES['video']; obj.image=''; obj.image_url=''; obj.video_url=''; obj.media_type='video_file'
            if obj.media_type == 'video_url':
                _delete_file(obj.image); _delete_file(obj.video)
                obj.image=''; obj.image_url=''; obj.video=''
            obj.title=f'슬라이드 {obj.sort_order or obj.pk}'
            obj.save()
            messages.success(request,'슬라이드가 저장되어 홈페이지에 반영되었습니다.')
            return _hero_redirect(obj.pk)

    hero_items=list(
        ContentItem.objects.filter(kind='hero').prefetch_related('intro_layers').order_by('sort_order','pk')
    )
    selected_id=request.GET.get('slide')
    selected_pk=int(selected_id) if selected_id and selected_id.isdigit() else (hero_items[0].pk if hero_items else None)
    return render(
        request,
        'dashboard/website_settings.html',
        {
            'setting':setting,
            'hero_items':hero_items,
            'selected_pk':selected_pk,
            'layer_types':IntroLayer.LAYER_TYPES,
            'layer_animations':IntroLayer.ANIMATIONS,
            'layer_object_fits':IntroLayer.OBJECT_FITS,
        },
    )



@staff_member_required
def seo_site_settings(request):
    import re
    s=SiteSetting.get_solo()
    def verification_value(value):
        value=(value or '').strip()
        match=re.search(r'''content=["']([^"']+)["']''', value, re.I)
        return match.group(1).strip() if match else value
    if request.method=='POST':
        s.site_name=request.POST.get('site_name','').strip() or s.site_name
        s.canonical_url=request.POST.get('canonical_url','').strip() or 'https://thepetkorea.co.kr/'
        s.meta_description=request.POST.get('meta_description','').strip()
        s.meta_keywords=request.POST.get('meta_keywords','').strip()
        s.naver_site_verification=verification_value(request.POST.get('naver_site_verification',''))
        s.google_site_verification=verification_value(request.POST.get('google_site_verification',''))
        s.og_title=request.POST.get('og_title','').strip()
        s.og_description=request.POST.get('og_description','').strip()
        s.og_image_url=request.POST.get('og_image_url','').strip()
        if request.POST.get('delete_favicon')=='1' and s.favicon:
            _delete_file(s.favicon); s.favicon=''
        if request.FILES.get('favicon'):
            if s.favicon: _delete_file(s.favicon)
            s.favicon=request.FILES['favicon']
        s.save()
        messages.success(request,'사이트 설정과 검색엔진 SEO 정보가 저장되었습니다.')
        return redirect('operator_dashboard:seo_site_settings')
    origin=(s.canonical_url or 'https://thepetkorea.co.kr/').rstrip('/')
    return render(request,'dashboard/seo_site_settings.html',{'s':s,'origin':origin})


# === ABOUT PAGE EDITOR ===
def _replace_media(obj, prefix, request):
    media_type=request.POST.get(prefix+'_media_type','image')
    setattr(obj,prefix+'_media_type',media_type)
    image=getattr(obj,prefix+'_image'); video=getattr(obj,prefix+'_video')
    if request.POST.get(prefix+'_media_delete')=='1':
        _delete_file(image); _delete_file(video); setattr(obj,prefix+'_image',''); setattr(obj,prefix+'_video',''); setattr(obj,prefix+'_video_url','')
    if request.FILES.get(prefix+'_image'):
        _delete_file(image); _delete_file(video); setattr(obj,prefix+'_image',request.FILES[prefix+'_image']); setattr(obj,prefix+'_video',''); setattr(obj,prefix+'_video_url',''); setattr(obj,prefix+'_media_type','image')
    if request.FILES.get(prefix+'_video'):
        _delete_file(video); _delete_file(image); setattr(obj,prefix+'_video',request.FILES[prefix+'_video']); setattr(obj,prefix+'_image',''); setattr(obj,prefix+'_video_url',''); setattr(obj,prefix+'_media_type','video_file')
    if media_type=='video_url':
        setattr(obj,prefix+'_video_url',request.POST.get(prefix+'_video_url','').strip())

@staff_member_required
def about_editor(request):
    from django.http import JsonResponse
    s=AboutPageSetting.get_solo()

    def done(message):
        messages.success(request,message)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok':True,'message':message})
        return redirect('operator_dashboard:about_editor')

    if request.method=='POST':
        action=request.POST.get('action','')

        if action=='history_add':
            AboutHistoryItem.objects.create(date='연도/날짜',text='내용을 입력하세요',sort_order=(AboutHistoryItem.objects.aggregate(m=Max('sort_order'))['m'] or 0)+1)
            return redirect('operator_dashboard:about_editor')
        if action=='org_add':
            AboutOrgItem.objects.create(role='직책',count=1,sort_order=(AboutOrgItem.objects.aggregate(m=Max('sort_order'))['m'] or 0)+1)
            return redirect('operator_dashboard:about_editor')
        if action=='history_delete':
            AboutHistoryItem.objects.filter(pk=request.POST.get('item_id')).delete()
            return redirect('operator_dashboard:about_editor')
        if action=='org_delete':
            AboutOrgItem.objects.filter(pk=request.POST.get('item_id')).delete()
            return redirect('operator_dashboard:about_editor')

        if action=='save_1':
            # ABOUT_MEDIA_DISPLAY_SAVE_FINAL
            try:s.title_radius=max(0,min(100,int(request.POST.get('title_radius') or 10)))
            except (TypeError,ValueError):pass
            for f in ['title_eyebrow','title_heading','title_tagline','title_contact_text','title_contact_info']:
                setattr(s,f,request.POST.get(f,'').strip())
            _replace_media(s,'title',request); s.save()
            return done('① 타이틀 영역이 바로 반영되었습니다.')

        if action=='save_2':
            try:s.gap_title_greeting=max(0,min(300,int(request.POST.get('gap_title_greeting') or 0)))
            except ValueError:pass
            s.save(); return done('② 타이틀과 인사말 간격이 바로 반영되었습니다.')

        if action=='save_3':
            try:s.greeting_radius=max(0,min(100,int(request.POST.get('greeting_radius') or 10)))
            except (TypeError,ValueError):pass
            s.greeting_media_fit=request.POST.get('greeting_media_fit') if request.POST.get('greeting_media_fit') in ('contain','cover') else 'contain'

            s.greeting_badge_text=request.POST.get('greeting_badge_text','').strip() or '대표자 심규진'

            try:
                s.greeting_badge_left=max(-300,min(500,int(request.POST.get('greeting_badge_left') or 25)))
            except (TypeError,ValueError):
                pass

            try:
                s.greeting_badge_bottom=max(-200,min(300,int(request.POST.get('greeting_badge_bottom') or -20)))
            except (TypeError,ValueError):
                pass

            try:
                s.greeting_badge_radius=max(0,min(100,int(request.POST.get('greeting_badge_radius') or 28)))
            except (TypeError,ValueError):
                pass

            for f in ['greeting_eyebrow','greeting_title','greeting_body','greeting_signature','greeting_subtitle']:
                setattr(s,f,request.POST.get(f,'').strip())
            _replace_media(s,'greeting',request); s.save()
            return done('③ 인사말이 바로 반영되었습니다.')

        if action=='save_4':
            try:s.gap_greeting_mission=max(0,min(300,int(request.POST.get('gap_greeting_mission') or 0)))
            except ValueError:pass
            s.save(); return done('④ 인사말과 설립목적 간격이 바로 반영되었습니다.')

        if action=='save_5':
            for f in ['mission_eyebrow','mission_title','mission_desc']:
                setattr(s,f,request.POST.get(f,'').strip())
            vals=[]
            for i in range(1,5):
                vals.append({'icon':request.POST.get(f'value_icon_{i}',''),'title':request.POST.get(f'value_title_{i}',''),'text':request.POST.get(f'value_text_{i}','')})
            s.values_json=vals; s.save()
            return done('⑤ 설립목적과 핵심가치가 바로 반영되었습니다.')

        if action=='save_6':
            try:s.history_radius=max(0,min(100,int(request.POST.get('history_radius') or 10)))
            except (TypeError,ValueError):pass
            s.history_media_fit=request.POST.get('history_media_fit') if request.POST.get('history_media_fit') in ('contain','cover') else 'contain'
            s.history_title=request.POST.get('history_title','').strip(); _replace_media(s,'history',request); s.save()
            for h in AboutHistoryItem.objects.all():
                h.date=request.POST.get(f'history_date_{h.pk}',h.date); h.text=request.POST.get(f'history_text_{h.pk}',h.text)
                try:h.sort_order=int(request.POST.get(f'history_order_{h.pk}',h.sort_order))
                except ValueError:pass
                h.save()
            return done('⑥ 연혁이 바로 반영되었습니다.')

        if action=='save_7':
            try:s.org_radius=max(0,min(100,int(request.POST.get('org_radius') or 10)))
            except (TypeError,ValueError):pass
            s.org_media_fit=request.POST.get('org_media_fit') if request.POST.get('org_media_fit') in ('contain','cover') else 'contain'
            s.org_title=request.POST.get('org_title','').strip(); _replace_media(s,'org',request); s.save()
            for o in AboutOrgItem.objects.all():
                o.role=request.POST.get(f'org_role_{o.pk}',o.role)
                try:o.count=max(0,int(request.POST.get(f'org_count_{o.pk}',o.count))); o.sort_order=int(request.POST.get(f'org_order_{o.pk}',o.sort_order))
                except ValueError:pass
                o.save()
            return done('⑦ 조직구성이 바로 반영되었습니다.')

        if action=='save_8':
            for f in ['member_card_image','partner_sticker_image']:
                if request.POST.get('delete_'+f)=='1' and getattr(s,f): _delete_file(getattr(s,f)); setattr(s,f,'')
                if request.FILES.get(f):
                    if getattr(s,f): _delete_file(getattr(s,f))
                    setattr(s,f,request.FILES[f])
            s.save(); return done('⑧ 회원증과 제휴업체 스티커가 바로 반영되었습니다.')

    if not AboutHistoryItem.objects.exists():
        for i,(d,t) in enumerate([('2022.06','경상남도 반려견 협회 규약(정관) 제정 및 협회 설립'),('2022.06','고유번호증 발급 (고유번호 539-80-02508)'),('2023','제휴 동물병원 확대 및 반려견 등록 지원사업 개시'),('2024','반려견 교육·훈련 프로그램 정례화'),('2025','경남 전역 반려견 공원·시설 정보 안내 서비스 확대'),('2026','온라인 회원관리 시스템 구축 및 홈페이지 전면 개편')],1): AboutHistoryItem.objects.create(date=d,text=t,sort_order=i)
    if not AboutOrgItem.objects.exists():
        for i,(r,c) in enumerate([('회장',1),('부회장',1),('총무',1),('감사',1),('이사',3),('사무장',1),('국장',4)],1): AboutOrgItem.objects.create(role=r,count=c,sort_order=i)
    return render(request,'dashboard/about_editor.html',{'s':s,'history':AboutHistoryItem.objects.all(),'org':AboutOrgItem.objects.all(),'values':s.values_json})

def about_data(request):
    from django.http import JsonResponse
    s=AboutPageSetting.get_solo()
    def url(field):
        try:return field.url if field else ''
        except:return ''
    data={f:getattr(s,f) for f in ['title_eyebrow','title_heading','title_tagline','title_contact_text','title_contact_info','gap_title_greeting','greeting_eyebrow','greeting_title','greeting_body','greeting_signature','greeting_subtitle','gap_greeting_mission','mission_eyebrow','mission_title','mission_desc','history_title','org_title']}
    # ABOUT_MEDIA_DISPLAY_DATA_FINAL
    data['title_radius']=s.title_radius;data['greeting_radius']=s.greeting_radius;data['history_radius']=s.history_radius;data['org_radius']=s.org_radius
    data['greeting_media_fit']=s.greeting_media_fit;data['history_media_fit']=s.history_media_fit;data['org_media_fit']=s.org_media_fit
    data['values']=s.values_json; data['history']=[{'date':x.date,'text':x.text} for x in AboutHistoryItem.objects.all()]; data['org']=[{'role':x.role,'count':x.count} for x in AboutOrgItem.objects.all()]
    for p in ['title','greeting','history','org']:
        data[p+'_media_type']=getattr(s,p+'_media_type'); data[p+'_image']=url(getattr(s,p+'_image')); data[p+'_video']=url(getattr(s,p+'_video')); data[p+'_video_url']=getattr(s,p+'_video_url')
    data['greeting_badge_text']=s.greeting_badge_text
    data['greeting_badge_left']=s.greeting_badge_left
    data['greeting_badge_bottom']=s.greeting_badge_bottom
    data['greeting_badge_radius']=s.greeting_badge_radius
    data['member_card_image']=url(s.member_card_image); data['partner_sticker_image']=url(s.partner_sticker_image)
    return JsonResponse(data)


# ============================================================
# PUBLIC WORLD BREEDS DATABASE
# ============================================================

from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import DogBreed


def public_breed_list(request):
    """
    전 세계 견종 DB 공개 목록.

    - 한글명/영문명 검색
    - FCI 그룹 필터
    - 공개 견종만 표시
    """

    q = (request.GET.get('q') or '').strip()
    group = (request.GET.get('group') or '').strip()

    breeds = DogBreed.objects.filter(
        is_published=True
    )

    if q:
        breeds = breeds.filter(
            Q(name_ko__icontains=q) |
            Q(name_en__icontains=q) |
            Q(origin__icontains=q) |
            Q(fci_group_name__icontains=q)
        )

    selected_group = None

    if group.isdigit():
        selected_group = int(group)

        if 1 <= selected_group <= 10:
            breeds = breeds.filter(
                fci_group=selected_group
            )
        else:
            selected_group = None

    breeds = breeds.order_by(
        'sort_order',
        'name_ko',
        'pk',
    )

    group_counts = {}

    for row in (
        DogBreed.objects
        .filter(is_published=True)
        .values_list('fci_group', flat=True)
    ):
        if row:
            group_counts[row] = (
                group_counts.get(row, 0) + 1
            )

    groups = []

    for number in range(1, 11):
        groups.append({
            'number': number,
            'count': group_counts.get(number, 0),
        })

    context = {
        'breeds': breeds,
        'q': q,
        'selected_group': selected_group,
        'groups': groups,
        'total_count': breeds.count(),
        'seo': _seo_context(request, '전 세계 견종 | 경상남도 반려견 협회', 'FCI 분류와 원산지, 역사, 외형, 성격 등 전 세계 견종 정보를 확인하세요.', '/breeds/', robots=('noindex,follow' if q or group else 'index,follow,max-image-preview:large')),
    }

    return render(
        request,
        'public/breed_list.html',
        context,
    )


def public_breed_detail(request, slug):
    """
    견종 상세페이지.
    """

    breed = get_object_or_404(
        DogBreed,
        slug=slug,
        is_published=True,
    )

    related_breeds = (
        DogBreed.objects
        .filter(
            is_published=True,
            fci_group=breed.fci_group,
        )
        .exclude(pk=breed.pk)
        .order_by(
            'sort_order',
            'name_ko',
        )[:4]
    )

    return render(
        request,
        'public/breed_detail.html',
        {
            'breed': breed,
            'related_breeds': related_breeds,
            'seo': _seo_context(request, f'{breed.name_ko} 특징·성격·역사 | 경상남도 반려견 협회', breed.summary or f'{breed.name_ko}의 원산지, FCI 분류, 외형, 성격과 역사를 확인하세요.', f'/breeds/{breed.slug}/', image=(breed.image.url if breed.image else breed.image_url), json_ld={'@context':'https://schema.org','@type':'WebPage','name':breed.name_ko,'description':breed.summary or breed.description,'url':request.build_absolute_uri(), 'breadcrumb':{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'홈','item':'https://thepetkorea.co.kr/'},{'@type':'ListItem','position':2,'name':'전 세계 견종','item':'https://thepetkorea.co.kr/breeds/'},{'@type':'ListItem','position':3,'name':breed.name_ko,'item':request.build_absolute_uri()}]}}),
        },
    )


# ============================================================
# PUBLIC NOTICE BOARD
# ============================================================

def public_notice_board(request):

    from django.core.paginator import Paginator
    from django.db.models import Q
    from django.shortcuts import render

    from .models import (
        BoardCategory,
        BoardPost,
    )

    categories = BoardCategory.objects.filter(
        board_type='notice',
        is_active=True,
    ).order_by(
        'sort_order',
        'pk',
    )

    posts = BoardPost.objects.filter(
        board_type='notice',
        is_published=True,
        is_hidden=False,
    ).select_related(
        'category',
    )

    keyword = request.GET.get(
        'q',
        ''
    ).strip()

    selected_category = request.GET.get(
        'category',
        ''
    ).strip()

    if keyword:

        posts = posts.filter(
            Q(title__icontains=keyword) |
            Q(body__icontains=keyword)
        )

    if selected_category:

        posts = posts.filter(
            category__slug=selected_category
        )

    posts = posts.order_by(
        '-is_pinned',
        '-is_important',
        '-created_at',
        '-pk',
    )

    paginator = Paginator(
        posts,
        15,
    )

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    return render(
        request,
        'website/board.html',
        {
            'categories': categories,
            'page_obj': page_obj,
            'keyword': keyword,
            'selected_category': selected_category,
            'seo': _seo_context(request, '공지 및 소식 | 경상남도 반려견 협회', '경상남도 반려견 협회의 공지사항과 새로운 소식을 확인하세요.', '/board.html', robots=('noindex,follow' if keyword or selected_category or request.GET.get('page') else 'index,follow,max-image-preview:large')),
        }
    )


def public_board_detail(request, pk):

    from django.shortcuts import (
        get_object_or_404,
        render,
    )
    from django.db.models import F

    from .models import BoardPost

    post = get_object_or_404(
        BoardPost.objects.select_related(
            'category'
        ),
        pk=pk,
        board_type='notice',
        is_published=True,
        is_hidden=False,
    )

    BoardPost.objects.filter(
        pk=post.pk
    ).update(
        view_count=F('view_count') + 1
    )

    post.refresh_from_db(
        fields=['view_count']
    )

    return render(
        request,
        'website/board_detail.html',
        {
            'post': post,
        }
    )

# ============================================================
# NOTICE COMPLETE SUPPORT
# ============================================================

def _notice_attachment_context(post):

    from .models import BoardAttachment

    attachments = list(
        BoardAttachment.objects.filter(
            post=post
        ).order_by('pk')
    )

    image_extensions = {
        'jpg', 'jpeg', 'png', 'gif',
        'webp', 'bmp', 'svg'
    }

    image_files = []
    download_files = []

    for attachment in attachments:

        file_obj = getattr(
            attachment,
            'file',
            None
        )

        if not file_obj:
            continue

        name = file_obj.name or ''
        extension = (
            name.rsplit('.', 1)[-1].lower()
            if '.' in name
            else ''
        )

        attachment.is_image_public = (
            extension in image_extensions
        )

        attachment.public_filename = (
            name.rsplit('/', 1)[-1]
        )

        try:
            attachment.public_size = file_obj.size
        except Exception:
            attachment.public_size = 0

        if attachment.is_image_public:
            image_files.append(attachment)
        else:
            download_files.append(attachment)

    return {
        'attachments': attachments,
        'image_files': image_files,
        'download_files': download_files,
    }


def public_notice_detail(request, pk):

    from django.db.models import F
    from django.shortcuts import (
        get_object_or_404,
        render,
    )

    from .models import BoardPost

    post = get_object_or_404(
        BoardPost.objects.select_related(
            'category'
        ),
        pk=pk,
        board_type='notice',
        is_published=True,
        is_hidden=False,
    )

    # 조회수 필드가 존재하는 경우에만 증가
    field_names = {
        f.name
        for f in BoardPost._meta.fields
    }

    view_field = None

    for candidate in (
        'view_count',
        'views',
        'hit',
        'hits',
    ):
        if candidate in field_names:
            view_field = candidate
            break

    if view_field:

        BoardPost.objects.filter(
            pk=post.pk
        ).update(
            **{
                view_field:
                    F(view_field) + 1
            }
        )

        post.refresh_from_db()

    previous_post = (
        BoardPost.objects
        .filter(
            board_type='notice',
            is_published=True,
            is_hidden=False,
            pk__lt=post.pk,
        )
        .order_by('-pk')
        .first()
    )

    next_post = (
        BoardPost.objects
        .filter(
            board_type='notice',
            is_published=True,
            is_hidden=False,
            pk__gt=post.pk,
        )
        .order_by('pk')
        .first()
    )

    context = {
        'post': post,
        'previous_post': previous_post,
        'next_post': next_post,
        'public_view_count': (
            getattr(post, view_field, None)
            if view_field
            else None
        ),
    }

    context.update(
        _notice_attachment_context(post)
    )

    context['seo'] = _seo_context(request, f'{post.title} | 경상남도 반려견 협회', post.body, f'/board/{post.pk}/', og_type='article', json_ld={'@context':'https://schema.org','@type':'Article','headline':post.title,'datePublished':post.created_at.isoformat(),'dateModified':post.updated_at.isoformat(),'mainEntityOfPage':request.build_absolute_uri(),'publisher':{'@type':'Organization','name':'경상남도 반려견 협회'}})

    return render(
        request,
        'website/board_detail.html',
        context,
    )


# ============================================================
# PUBLIC COMMUNITY BOARD
# ============================================================

def public_community_list(request):

    from django.core.paginator import Paginator
    from django.db.models import Q

    from .models import (
        BoardPost,
        BoardCategory,
    )

    keyword = request.GET.get(
        'q',
        ''
    ).strip()

    selected_category = request.GET.get(
        'category',
        ''
    ).strip()

    categories = (
        BoardCategory.objects
        .filter(
            board_type='community',
            is_active=True
        )
        .order_by(
            'sort_order',
            'id'
        )
    )

    posts = (
        BoardPost.objects
        .filter(
            board_type='community',
            is_published=True,
            is_hidden=False,
        )
        .select_related(
            'category',
            'author'
        )
    )

    if selected_category:

        posts = posts.filter(
            category__slug=selected_category
        )

    if keyword:

        posts = posts.filter(
            Q(title__icontains=keyword)
            |
            Q(body__icontains=keyword)
        )

    posts = posts.order_by(
        '-is_pinned',
        '-is_important',
        '-created_at',
        '-pk',
    )

    paginator = Paginator(
        posts,
        15
    )

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    return render(
        request,
        'website/community.html',
        {
            'categories': categories,
            'page_obj': page_obj,
            'keyword': keyword,
            'selected_category': selected_category,
            'seo': _seo_context(request, '자유게시판 | 경상남도 반려견 협회', '반려견과 반려생활에 관한 이야기를 나누는 경상남도 반려견 협회 자유게시판입니다.', '/community.html', robots='noindex,follow'),
        }
    )


def public_community_detail(request, pk):

    from django.shortcuts import (
        get_object_or_404,
        render,
    )
    from django.db.models import F

    from .models import (
        BoardPost,
        BoardComment,
        BoardLike,
        BoardAttachment,
    )

    post = get_object_or_404(
        BoardPost.objects.select_related(
            'category',
            'author',
        ),
        pk=pk,
        board_type='community',
        is_published=True,
        is_hidden=False,
    )

    BoardPost.objects.filter(
        pk=post.pk
    ).update(
        view_count=F('view_count') + 1
    )

    post.refresh_from_db(
        fields=['view_count']
    )

    comments = (
        BoardComment.objects
        .filter(
            post=post,
            parent__isnull=True,
        )
        .select_related('author')
        .prefetch_related(
            'replies__author'
        )
        .order_by('created_at')
    )

    attachments = (
        BoardAttachment.objects
        .filter(post=post)
        .order_by(
            'sort_order',
            'pk',
        )
    )

    like_count = (
        BoardLike.objects
        .filter(post=post)
        .count()
    )

    user_liked = False

    if request.user.is_authenticated:
        user_liked = (
            BoardLike.objects
            .filter(
                post=post,
                user=request.user,
            )
            .exists()
        )

    return render(
        request,
        'website/community_detail.html',
        {
            'post': post,
            'comments': comments,
            'attachments': attachments,
            'like_count': like_count,
            'user_liked': user_liked,
            'seo': _seo_context(request, f'{post.title} | 경상남도 반려견 협회', post.body, f'/community/{post.pk}/', robots='noindex,follow'),
        }
    )


@login_required
def public_community_create(request):

    from django.contrib import messages

    from django.shortcuts import (
        render,
        redirect,
    )

    from django.utils import timezone

    from .models import (
        BoardPost,
        BoardCategory,
        BoardAttachment,
    )

    categories = (
        BoardCategory.objects
        .filter(
            board_type='community',
            is_active=True
        )
        .order_by(
            'sort_order',
            'id'
        )
    )

    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        body = request.POST.get(
            'body',
            ''
        ).strip()

        category_id = request.POST.get(
            'category',
            ''
        ).strip()

        if not title:

            messages.error(
                request,
                '제목을 입력해주세요.'
            )

            return render(
                request,
                'website/community_form.html',
                {
                    'categories': categories,
                    'mode': 'create',
                }
            )

        if not body:

            messages.error(
                request,
                '내용을 입력해주세요.'
            )

            return render(
                request,
                'website/community_form.html',
                {
                    'categories': categories,
                    'mode': 'create',
                }
            )

        category = None

        if category_id:

            category = (
                BoardCategory.objects
                .filter(
                    pk=category_id,
                    board_type='community',
                    is_active=True
                )
                .first()
            )

        post = BoardPost.objects.create(
            board_type='community',
            category=category,
            author=request.user,
            title=title,
            body=body,
            is_published=True,
            is_hidden=False,
            allow_comments=True,
            published_at=timezone.now(),
        )

        for uploaded in request.FILES.getlist(
            'attachments'
        ):

            name = uploaded.name or ''

            extension = (
                name.rsplit('.', 1)[-1].lower()
                if '.' in name
                else ''
            )

            BoardAttachment.objects.create(
                post=post,
                file=uploaded,
                original_name=name,
                is_image=extension in {
                    'jpg',
                    'jpeg',
                    'png',
                    'gif',
                    'webp',
                    'bmp',
                },
            )

        messages.success(
            request,
            '게시글을 등록했습니다.'
        )

        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    return render(
        request,
        'website/community_form.html',
        {
            'categories': categories,
            'mode': 'create',
        }
    )


@login_required
def public_community_update(request, pk):

    from django.contrib import messages

    from django.shortcuts import (
        get_object_or_404,
        render,
        redirect,
    )

    from .models import (
        BoardPost,
        BoardCategory,
        BoardAttachment,
    )

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='community',
    )

    if (
        post.author_id != request.user.id
        and not request.user.is_staff
    ):
        from django.http import HttpResponseForbidden

        return HttpResponseForbidden(
            '수정 권한이 없습니다.'
        )

    categories = (
        BoardCategory.objects
        .filter(
            board_type='community',
            is_active=True
        )
        .order_by(
            'sort_order',
            'id'
        )
    )

    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        body = request.POST.get(
            'body',
            ''
        ).strip()

        if not title or not body:

            messages.error(
                request,
                '제목과 내용을 입력해주세요.'
            )

            return render(
                request,
                'website/community_form.html',
                {
                    'post': post,
                    'categories': categories,
                    'mode': 'update',
                }
            )

        category_id = request.POST.get(
            'category',
            ''
        ).strip()

        category = None

        if category_id:

            category = (
                BoardCategory.objects
                .filter(
                    pk=category_id,
                    board_type='community',
                    is_active=True
                )
                .first()
            )

        post.title = title
        post.body = body
        post.category = category

        post.save(
            update_fields=[
                'title',
                'body',
                'category',
                'updated_at',
            ]
        )

        delete_ids = request.POST.getlist(
            'delete_attachment'
        )

        if delete_ids:

            post.attachments.filter(
                pk__in=delete_ids
            ).delete()

        for uploaded in request.FILES.getlist(
            'attachments'
        ):

            name = uploaded.name or ''

            extension = (
                name.rsplit('.', 1)[-1].lower()
                if '.' in name
                else ''
            )

            BoardAttachment.objects.create(
                post=post,
                file=uploaded,
                original_name=name,
                is_image=extension in {
                    'jpg',
                    'jpeg',
                    'png',
                    'gif',
                    'webp',
                    'bmp',
                },
            )

        messages.success(
            request,
            '게시글을 수정했습니다.'
        )

        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    return render(
        request,
        'website/community_form.html',
        {
            'post': post,
            'categories': categories,
            'mode': 'update',
        }
    )


@login_required
@require_POST
def public_community_delete(request, pk):

    from django.contrib import messages

    from django.shortcuts import (
        get_object_or_404,
        redirect,
    )

    from django.http import HttpResponseForbidden

    from .models import BoardPost

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='community',
    )

    if (
        post.author_id != request.user.id
        and not request.user.is_staff
    ):

        return HttpResponseForbidden(
            '삭제 권한이 없습니다.'
        )

    post.delete()

    messages.success(
        request,
        '게시글을 삭제했습니다.'
    )

    return redirect(
        'public_community_list'
    )


# ============================================================
# COMMUNITY INTERACTION
# 댓글 / 대댓글 / 좋아요 / 신고
# ============================================================

@login_required
@require_POST
def public_community_comment_create(request, pk):

    from django.contrib import messages
    from django.shortcuts import (
        get_object_or_404,
        redirect,
    )

    from .models import (
        BoardPost,
        BoardComment,
    )

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='community',
        is_published=True,
        is_hidden=False,
    )

    if not post.allow_comments:
        messages.error(
            request,
            '댓글 작성이 허용되지 않은 게시글입니다.'
        )
        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    body = request.POST.get(
        'body',
        ''
    ).strip()

    if not body:
        messages.error(
            request,
            '댓글 내용을 입력해주세요.'
        )
        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    parent = None

    parent_id = request.POST.get(
        'parent',
        ''
    ).strip()

    if parent_id:

        parent = (
            BoardComment.objects
            .filter(
                pk=parent_id,
                post=post,
                is_hidden=False,
            )
            .first()
        )

        if not parent:
            messages.error(
                request,
                '답글을 작성할 댓글을 찾을 수 없습니다.'
            )
            return redirect(
                'public_community_detail',
                pk=post.pk
            )

        # 대댓글의 대댓글이 들어오더라도
        # 최상위 댓글 아래 1단계 구조로 정리
        if parent.parent_id:
            parent = parent.parent

    BoardComment.objects.create(
        post=post,
        author=request.user,
        parent=parent,
        body=body,
    )

    messages.success(
        request,
        '댓글을 등록했습니다.'
    )

    return redirect(
        'public_community_detail',
        pk=post.pk
    )


@login_required
@require_POST
def public_community_comment_delete(
    request,
    pk,
    comment_pk
):

    from django.contrib import messages
    from django.shortcuts import (
        get_object_or_404,
        redirect,
    )

    from .models import (
        BoardPost,
        BoardComment,
    )

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='community',
    )

    comment = get_object_or_404(
        BoardComment,
        pk=comment_pk,
        post=post,
    )

    is_manager = (
        request.user.is_staff
        or request.user.is_superuser
    )

    if (
        comment.author_id
        != request.user.id
        and not is_manager
    ):
        messages.error(
            request,
            '댓글을 삭제할 권한이 없습니다.'
        )
        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    # 답글이 있으면 실제 삭제 대신 숨김 처리
    has_children = BoardComment.objects.filter(
        parent=comment
    ).exists()

    if has_children:
        comment.body = '삭제된 댓글입니다.'
        comment.is_hidden = True
        comment.save(
            update_fields=[
                'body',
                'is_hidden',
                'updated_at',
            ]
        )
    else:
        comment.delete()

    messages.success(
        request,
        '댓글을 삭제했습니다.'
    )

    return redirect(
        'public_community_detail',
        pk=post.pk
    )


@login_required
@require_POST
def public_community_like_toggle(request, pk):

    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    from .models import (
        BoardPost,
        BoardLike,
    )

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='community',
        is_published=True,
        is_hidden=False,
    )

    like = BoardLike.objects.filter(
        post=post,
        user=request.user,
    ).first()

    if like:
        like.delete()
        liked = False
    else:
        BoardLike.objects.create(
            post=post,
            user=request.user,
        )
        liked = True

    count = BoardLike.objects.filter(
        post=post
    ).count()

    return JsonResponse({
        'ok': True,
        'liked': liked,
        'count': count,
    })


@login_required
@require_POST
def public_community_report(request, pk):

    from django.contrib import messages
    from django.shortcuts import (
        get_object_or_404,
        redirect,
    )

    from .models import (
        BoardPost,
        BoardReport,
    )

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='community',
        is_published=True,
        is_hidden=False,
    )

    if post.author_id == request.user.id:
        messages.error(
            request,
            '본인이 작성한 게시글은 신고할 수 없습니다.'
        )
        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    reason = request.POST.get(
        'reason',
        ''
    ).strip()

    detail = request.POST.get(
        'detail',
        ''
    ).strip()

    allowed_reasons = {
        'spam',
        'abuse',
        'illegal',
        'privacy',
        'commercial',
        'other',
    }

    if reason not in allowed_reasons:
        reason = 'other'

    # 동일 사용자의 같은 게시글 중복 신고 방지
    exists = BoardReport.objects.filter(
        post=post,
        reporter=request.user,
    ).exists()

    if exists:
        messages.info(
            request,
            '이미 신고한 게시글입니다.'
        )
        return redirect(
            'public_community_detail',
            pk=post.pk
        )

    BoardReport.objects.create(
        post=post,
        reporter=request.user,
        reason=reason,
        detail=detail,
    )

    messages.success(
        request,
        '신고가 접수되었습니다.'
    )

    return redirect(
        'public_community_detail',
        pk=post.pk
    )


@login_required
def chatbot_editor(request):
    from django.contrib import messages
    from .models import ChatbotSetting

    setting, _ = ChatbotSetting.objects.get_or_create(pk=1)

    if request.method == 'POST':

        setting.enabled = request.POST.get('enabled') == 'on'
        setting.ai_enabled = request.POST.get('ai_enabled') == 'on'

        setting.bot_name = (
            request.POST.get('bot_name', '').strip()
            or '경상남도 반려견 협회 챗봇'
        )

        setting.greeting = (
            request.POST.get('greeting', '').strip()
        )

        setting.system_prompt = (
            request.POST.get('system_prompt', '').strip()
        )

        setting.model_name = (
            request.POST.get('model_name', '').strip()
            or 'gpt-5-mini'
        )

        # 실제 암호화 저장은 OpenAI 연결 단계에서 적용한다.
        # 기존 키가 있는 상태에서 빈 값으로 저장되지 않게 한다.
        new_api_key = request.POST.get('api_key', '').strip()

        if new_api_key:
            setting.api_key_encrypted = new_api_key

        setting.contact_button_text = (
            request.POST.get('contact_button_text', '').strip()
            or '☎ 협회 문의하기'
        )

        setting.contact_phone = (
            request.POST.get('contact_phone', '').strip()
            or '010-3556-8603'
        )

        if request.FILES.get('bot_video'):
            setting.bot_video = request.FILES['bot_video']

        setting.save()

        messages.success(
            request,
            '챗봇 설정을 저장했습니다.'
        )

        return redirect(
            'operator_dashboard:chatbot_editor'
        )

    masked_key = ''

    if setting.api_key_encrypted:
        masked_key = '••••••••••••••••••••'

    return render(
        request,
        'dashboard/chatbot_editor.html',
        {
            'setting': setting,
            'masked_key': masked_key,
        }
    )


# ============================================================
# PUBLIC AI CHATBOT
# ============================================================

def public_chatbot_config(request):
    """
    Public chatbot configuration.
    API key is NEVER returned to the browser.
    """
    from django.http import JsonResponse
    from .models import ChatbotSetting

    setting, _ = ChatbotSetting.objects.get_or_create(pk=1)

    video_url = ''

    if setting.bot_video:
        try:
            video_url = setting.bot_video.url
            separator = '&' if '?' in video_url else '?'
            video_url = (
                video_url
                + separator
                + 'v='
                + str(int(setting.updated_at.timestamp()))
            )
        except Exception:
            video_url = ''

    response = JsonResponse({
        'enabled': setting.enabled,
        'ai_enabled': setting.ai_enabled,
        'bot_name': setting.bot_name,
        'greeting': setting.greeting,
        'video_url': video_url,
        'contact_button_text': setting.contact_button_text,
        'contact_phone': setting.contact_phone,
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


@require_POST
def public_chatbot_message(request):
    """
    Server-side OpenAI chatbot endpoint.
    OpenAI API key never reaches the browser.
    """
    import json

    from django.http import JsonResponse
    from .models import ChatbotSetting

    try:
        payload = json.loads(
            request.body.decode('utf-8')
        )
    except Exception:
        return JsonResponse(
            {
                'ok': False,
                'error': '잘못된 요청입니다.',
            },
            status=400
        )

    message = str(
        payload.get('message', '')
    ).strip()

    if not message:
        return JsonResponse(
            {
                'ok': False,
                'error': '질문을 입력해주세요.',
            },
            status=400
        )

    # 비정상적으로 긴 요청 방지
    if len(message) > 1500:
        return JsonResponse(
            {
                'ok': False,
                'error': '질문은 1,500자 이내로 입력해주세요.',
            },
            status=400
        )

    setting, _ = ChatbotSetting.objects.get_or_create(pk=1)

    if not setting.enabled:
        return JsonResponse(
            {
                'ok': False,
                'error': '현재 챗봇을 사용할 수 없습니다.',
            },
            status=503
        )

    if not setting.ai_enabled:
        return JsonResponse({
            'ok': True,
            'answer': (
                '현재 AI 상담 기능은 준비 중입니다. '
                '협회 문의하기를 이용해주세요.'
            ),
        })

    api_key = (
        setting.api_key_encrypted or ''
    ).strip()

    if not api_key:
        return JsonResponse(
            {
                'ok': False,
                'error': 'AI 설정이 완료되지 않았습니다.',
            },
            status=503
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key
        )

        system_prompt = (
            setting.system_prompt.strip()
            or (
                '당신은 경상남도 반려견 협회 공식 안내 챗봇입니다. '
                '질문에 정확하고 친절하게 답변하세요. '
                '확실하지 않은 내용은 추측하지 마세요.'
            )
        )

        short_answer_rule = '''
[답변 작성 규칙]
답변은 모바일 챗봇에서 읽기 쉽게 짧고 명확하게 작성하세요.
일반적인 질문은 3~5줄로 답변하세요.
복잡한 질문도 최대 7줄을 넘기지 마세요.
불필요한 배경설명, 반복, 긴 예시는 생략하세요.
필요하면 핵심 내용만 짧은 항목으로 나누세요.
사용자가 상세 설명을 요청한 경우에만 조금 더 자세히 답변하세요.
확실하지 않은 내용은 추측하지 말고 협회 문의를 안내하세요.
'''

        response = client.responses.create(
            model=setting.model_name,
            instructions=(
                system_prompt
                + "\n\n"
                + short_answer_rule
            ),
            input=message,
            reasoning={
                "effort": "minimal",
            },
            max_output_tokens=700,
        )

        answer = (
            response.output_text or ''
        ).strip()

        if not answer:
            answer = (
                '답변을 생성하지 못했습니다. '
                '협회 문의하기를 이용해주세요.'
            )

        return JsonResponse({
            'ok': True,
            'answer': answer,
        })

    except Exception as exc:

        # API key 등 민감정보가 사용자에게 노출되지 않도록
        # 실제 예외 내용은 응답하지 않는다.
        print(
            '[CHATBOT ERROR]',
            type(exc).__name__
        )

        return JsonResponse(
            {
                'ok': False,
                'error': (
                    'AI 답변을 불러오지 못했습니다. '
                    '잠시 후 다시 이용해주세요.'
                ),
            },
            status=502
        )


def public_intro_news_api(request):
    """
    메인 인트로 공지 및 소식 API

    공지사항:
      - notice

    협회 소식:
      - news
      - event
      - policy
    """
    from django.http import JsonResponse
    from .models import BoardPost

    base_qs = BoardPost.objects.filter(
        board_type='notice',
        is_published=True,
        is_hidden=False,
    ).select_related('category')

    notice_posts = (
        base_qs
        .filter(category__slug='notice')
        .order_by('-is_pinned', '-published_at', '-created_at')[:5]
    )

    association_posts = (
        base_qs
        .filter(category__slug__in=['news', 'event', 'policy'])
        .order_by('-is_pinned', '-published_at', '-created_at')[:5]
    )

    def serialize(post):
        dt = post.published_at or post.created_at

        return {
            'id': post.pk,
            'title': post.title,
            'category': post.category.name if post.category else '',
            'category_slug': post.category.slug if post.category else '',
            'date': dt.strftime('%Y.%m.%d') if dt else '',
            'url': f'/board/{post.pk}/',
        }

    return JsonResponse({
        'ok': True,
        'notice': [
            serialize(post)
            for post in notice_posts
        ],
        'association': [
            serialize(post)
            for post in association_posts
        ],
    })


# ============================================================
# POLICY / AGREEMENT MANAGEMENT
# ============================================================

@staff_member_required
def policy_editor(request):
    from django.contrib import messages
    from .models import PolicyDocument

    defaults = {
        'privacy': '개인정보처리방침',
        'terms': '웹사이트 이용약관',
        'rules': '[협회] 회원규칙',
    }

    for key, title in defaults.items():
        PolicyDocument.objects.get_or_create(
            key=key,
            defaults={'title': title, 'body': '', 'is_active': True},
        )

    if request.method == 'POST':
        for key in defaults:
            item = PolicyDocument.objects.get(key=key)
            item.title = (request.POST.get(f'{key}_title') or defaults[key]).strip()
            item.body = (request.POST.get(f'{key}_body') or '').strip()
            item.is_active = request.POST.get(f'{key}_active') == 'on'
            item.save()

        messages.success(request, '약관·규칙이 저장되어 회원가입 화면에 즉시 반영됩니다.')
        return redirect('operator_dashboard:policy_editor')

    documents = {
        x.key: x
        for x in PolicyDocument.objects.filter(key__in=defaults.keys())
    }

    return render(
        request,
        'dashboard/policy_editor.html',
        {'documents': documents},
    )


def public_policy_data(request):
    from django.http import JsonResponse
    from .models import PolicyDocument

    documents = {
        row.key: {
            'title': row.title,
            'body': row.body,
            'updated_at': row.updated_at.isoformat(),
        }
        for row in PolicyDocument.objects.filter(is_active=True)
    }

    response = JsonResponse({'ok': True, 'documents': documents})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


# ============================================================
# DOG LIFE
# ============================================================

DOG_LIFE_DISPLAY_TYPES = {
    'text',
    'image_large',
    'image_small',
    'video_horizontal',
    'video_vertical',
}


def _doglife_queryset():
    from django.db.models import Count
    from .models import BoardPost

    return (
        BoardPost.objects
        .filter(
            board_type='doglife',
            is_published=True,
            is_hidden=False,
        )
        .select_related('category', 'author', 'author__member_profile')
        .prefetch_related('attachments')
        .annotate(like_count=Count('likes', distinct=True))
    )


def _doglife_save_files(post, request):
    from .models import BoardAttachment

    uploaded = list(request.FILES.getlist('attachments'))

    for key in ('camera_image', 'camera_video'):
        item = request.FILES.get(key)
        if item:
            uploaded.append(item)

    uploaded = uploaded[:8]

    existing_count = post.attachments.count()
    saved = 0

    for upload in uploaded:
        content_type = str(getattr(upload, 'content_type', '') or '')
        is_image = content_type.startswith('image/')
        is_video = content_type.startswith('video/')

        if not (is_image or is_video):
            continue

        BoardAttachment.objects.create(
            post=post,
            file=upload,
            original_name=getattr(upload, 'name', '') or '',
            is_image=is_image,
            sort_order=existing_count + saved,
        )
        saved += 1

    return saved


def public_doglife_list(request):
    from .models import BoardCategory

    categories = list(
        BoardCategory.objects.filter(
            board_type='doglife',
            is_active=True,
        ).order_by('sort_order', 'id')
    )

    selected_category = (request.GET.get('category') or '').strip()
    base = _doglife_queryset().order_by('-published_at', '-created_at')

    # 카테고리는 유지하되 매 섹션의 편집 리듬이 반복되지 않도록
    # 네 가지 매거진 레이아웃을 순환한다.
    layouts = ('feature', 'mosaic', 'strip', 'editorial')

    def group_for(category, index, limit=None):
        qs = base.filter(category=category)
        if limit:
            qs = qs[:limit]
        return {
            'category': category,
            'posts': list(qs),
            'layout': layouts[index % len(layouts)],
        }

    if selected_category:
        selected = next(
            (x for x in categories if x.slug == selected_category),
            None,
        )
        if selected:
            selected_index = categories.index(selected)
            category_groups = [group_for(selected, selected_index)]
        else:
            category_groups = []
    else:
        category_groups = [
            group_for(category, index, 12)
            for index, category in enumerate(categories)
        ]

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'category_groups': category_groups,
        'seo': _seo_context(
            request,
            '견생(Dog Life) | 경상남도 반려견 협회',
            '반려견과 함께 사는 회원들의 생활팁, 산책, 건강관리, 자랑과 일상을 나누는 견생 콘텐츠입니다.',
            '/doglife/',
        ),
    }

    return render(request, 'website/doglife.html', context)

def public_doglife_detail(request, pk):
    from django.db.models import F
    from django.shortcuts import get_object_or_404
    from .models import BoardPost, BoardLike

    post = get_object_or_404(
        _doglife_queryset(),
        pk=pk,
    )

    BoardPost.objects.filter(pk=post.pk).update(
        view_count=F('view_count') + 1
    )
    post.refresh_from_db(fields=['view_count'])

    user_liked = False
    if request.user.is_authenticated:
        user_liked = BoardLike.objects.filter(
            post=post,
            user=request.user,
        ).exists()

    return render(
        request,
        'website/doglife_detail.html',
        {
            'post': post,
            'attachments': post.attachments.all(),
            'like_count': post.likes.count(),
            'user_liked': user_liked,
            'seo': _seo_context(
                request,
                post.title,
                (post.body or '')[:160],
                f'/doglife/{post.pk}/',
            ),
        },
    )


def _doglife_login_redirect(request):
    from urllib.parse import quote
    return redirect('/?login=1&next=' + quote(request.get_full_path(), safe='/' ))


def public_doglife_create(request):
    from django.contrib import messages
    from django.utils import timezone
    from .models import BoardCategory, BoardPost

    if not request.user.is_authenticated:
        return _doglife_login_redirect(request)

    categories = BoardCategory.objects.filter(
        board_type='doglife',
        is_active=True,
    ).order_by('sort_order', 'id')

    if request.method == 'POST':
        category = get_object_or_404(
            BoardCategory,
            pk=request.POST.get('category'),
            board_type='doglife',
            is_active=True,
        )

        title = (request.POST.get('title') or '').strip()
        body = (request.POST.get('body') or '').strip()
        display_type = (request.POST.get('display_type') or 'text').strip()

        if display_type not in DOG_LIFE_DISPLAY_TYPES:
            display_type = 'text'

        if not title:
            messages.error(request, '제목을 입력해주세요.')
        elif not body and not request.FILES:
            messages.error(request, '내용 또는 사진·영상을 등록해주세요.')
        else:
            post = BoardPost.objects.create(
                board_type='doglife',
                category=category,
                author=request.user,
                title=title,
                body=body,
                display_type=display_type,
                view_count=0,
                is_published=True,
                is_hidden=False,
                allow_comments=True,
                published_at=timezone.now(),
            )
            _doglife_save_files(post, request)
            messages.success(request, '견생 콘텐츠가 바로 등록되었습니다.')
            return redirect('public_doglife_detail', pk=post.pk)

    return render(
        request,
        'website/doglife_form.html',
        {
            'categories': categories,
            'post': None,
            'mode': 'create',
        },
    )


def public_doglife_update(request, pk):
    from django.contrib import messages
    from django.http import HttpResponseForbidden
    from .models import BoardAttachment, BoardCategory, BoardPost

    if not request.user.is_authenticated:
        return _doglife_login_redirect(request)

    post = get_object_or_404(BoardPost, pk=pk, board_type='doglife')

    if post.author_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden('수정 권한이 없습니다.')

    categories = BoardCategory.objects.filter(
        board_type='doglife',
        is_active=True,
    ).order_by('sort_order', 'id')

    if request.method == 'POST':
        category = get_object_or_404(
            BoardCategory,
            pk=request.POST.get('category'),
            board_type='doglife',
            is_active=True,
        )
        display_type = (request.POST.get('display_type') or 'text').strip()
        if display_type not in DOG_LIFE_DISPLAY_TYPES:
            display_type = 'text'

        title = (request.POST.get('title') or '').strip()
        if not title:
            messages.error(request, '제목을 입력해주세요.')
        else:
            post.category = category
            post.title = title
            post.body = (request.POST.get('body') or '').strip()
            post.display_type = display_type
            post.is_published = True
            post.is_hidden = False
            post.save()

            delete_ids = request.POST.getlist('delete_attachment')
            if delete_ids:
                BoardAttachment.objects.filter(
                    post=post,
                    pk__in=delete_ids,
                ).delete()

            _doglife_save_files(post, request)
            messages.success(request, '견생 콘텐츠를 수정했습니다.')
            return redirect('public_doglife_detail', pk=post.pk)

    return render(
        request,
        'website/doglife_form.html',
        {
            'categories': categories,
            'post': post,
            'mode': 'update',
        },
    )


@require_POST
def public_doglife_delete(request, pk):
    from django.contrib import messages
    from django.http import HttpResponseForbidden
    from .models import BoardPost

    if not request.user.is_authenticated:
        return _doglife_login_redirect(request)

    post = get_object_or_404(BoardPost, pk=pk, board_type='doglife')

    if post.author_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden('삭제 권한이 없습니다.')

    post.delete()
    messages.success(request, '견생 콘텐츠를 삭제했습니다.')
    return redirect('public_doglife_list')


@require_POST
def public_doglife_like_toggle(request, pk):
    from django.http import JsonResponse
    from .models import BoardLike, BoardPost

    if not request.user.is_authenticated:
        return JsonResponse(
            {'ok': False, 'message': '로그인이 필요합니다.'},
            status=401,
        )

    post = get_object_or_404(
        BoardPost,
        pk=pk,
        board_type='doglife',
        is_published=True,
        is_hidden=False,
    )

    like = BoardLike.objects.filter(post=post, user=request.user).first()

    if like:
        like.delete()
        liked = False
    else:
        BoardLike.objects.create(post=post, user=request.user)
        liked = True

    return JsonResponse({
        'ok': True,
        'liked': liked,
        'count': post.likes.count(),
    })
