from django.conf import settings
from django.db import models

class PartnerCategory(models.Model):
    code=models.SlugField(unique=True); name=models.CharField(max_length=50); sort_order=models.PositiveSmallIntegerField(default=0)
    def __str__(self): return self.name
class Partner(models.Model):
    PAYMENT_TYPES=[
        ('monthly','월납'),
        ('annual','연납'),
    ]

    category=models.ForeignKey(
        PartnerCategory,
        on_delete=models.PROTECT,
        related_name='partners'
    )
    name=models.CharField(max_length=150)
    address=models.CharField(max_length=300)
    phone=models.CharField(max_length=40,blank=True)
    city=models.CharField(max_length=30,db_index=True)

    latitude=models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude=models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )


    kakao_place_id = models.CharField(
        max_length=50,
        blank=True,
        default='',
    )

    kakao_place_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
    )

    is_affiliated=models.BooleanField(
        default=False,
        verbose_name='협력업체'
    )

    ad_monthly_fee=models.PositiveIntegerField(
        default=0,
        verbose_name='월 광고금액'
    )
    ad_start_date=models.DateField(
        null=True,
        blank=True,
        verbose_name='광고 시작일'
    )
    ad_end_date=models.DateField(
        null=True,
        blank=True,
        verbose_name='광고 종료일'
    )
    ad_payment_type=models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        blank=True,
        default='',
        verbose_name='광고비 납부방식'
    )

    is_active=models.BooleanField(default=True)
    source=models.CharField(max_length=100,blank=True)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['category','name','address'],name='uniq_partner_location')]; ordering=['city','name']
    def __str__(self): return self.name
class PartnerBenefit(models.Model):
    partner=models.ForeignKey(Partner,on_delete=models.CASCADE,related_name='benefits'); title=models.CharField(max_length=150); description=models.TextField(blank=True); active=models.BooleanField(default=True)
    def __str__(self): return f'{self.partner} · {self.title}'
class ContentItem(models.Model):
    KINDS=[('notice','공지사항'),('community','자유게시판'),('breed','전 세계 견종'),('intro','인트로 갤러리'),('hero','메인 비주얼'),('popup','팝업')]
    MEDIA_TYPES=[('image','이미지'),('video_file','영상 파일'),('video_url','영상 링크')]
    kind=models.CharField(max_length=20,choices=KINDS,db_index=True); title=models.CharField(max_length=200); label=models.CharField(max_length=80,blank=True); body=models.TextField(blank=True); image=models.FileField(upload_to='content/%Y/%m/',blank=True); image_url=models.URLField(max_length=1200,blank=True); link=models.CharField(max_length=500,blank=True); media_type=models.CharField(max_length=20,choices=MEDIA_TYPES,default='image'); video=models.FileField(upload_to='content/video/%Y/%m/',blank=True); video_url=models.URLField(max_length=1000,blank=True); autoplay=models.BooleanField(default=True); muted=models.BooleanField(default=True); loop=models.BooleanField(default=True); is_published=models.BooleanField(default=True); sort_order=models.IntegerField(default=0); popup_start=models.DateTimeField(null=True,blank=True); popup_end=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    hero_eyebrow=models.CharField(max_length=200,blank=True); hero_title=models.CharField(max_length=300,blank=True); hero_meta1=models.CharField(max_length=300,blank=True); hero_meta2=models.CharField(max_length=300,blank=True); hero_button1_text=models.CharField(max_length=80,blank=True); hero_button1_link=models.CharField(max_length=500,blank=True); hero_button2_text=models.CharField(max_length=80,blank=True); hero_button2_link=models.CharField(max_length=500,blank=True)
    hero_meta1_font_size=models.PositiveSmallIntegerField(default=16)
    hero_meta2_font_size=models.PositiveSmallIntegerField(default=16)
    class Meta: ordering=['sort_order','-created_at']
    def __str__(self): return self.title

class MemberProfile(models.Model):
    GENDERS=[('M','남성'),('F','여성'),('O','기타')]; STATUSES=[('general','일반회원'),('pending','정회원 승인대기'),('regular','정회원'),('withdrawn','탈퇴')]
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='member_profile'); name=models.CharField(max_length=80); birth_date=models.DateField(null=True,blank=True); gender=models.CharField(max_length=1,choices=GENDERS,blank=True); phone=models.CharField(max_length=30,blank=True); region=models.CharField(max_length=40,blank=True); address_detail=models.CharField(max_length=250,blank=True); privacy_agreed=models.BooleanField(default=False); regular_member_requested=models.BooleanField(default=False); membership_status=models.CharField(max_length=20,choices=STATUSES,default='general'); joined_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name or self.user.get_username()
class MembershipCardGrant(models.Model):
    SOURCES=[('legacy','기존 정회원 예외발급'),('payment','토스 연회비 결제')]
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='membership_card_grant')
    source=models.CharField(max_length=20,choices=SOURCES)
    payment=models.OneToOneField('PaymentRecord',on_delete=models.SET_NULL,null=True,blank=True,related_name='membership_card_grant')
    issued_at=models.DateTimeField(auto_now_add=True)
    valid_from=models.DateField()
    valid_to=models.DateField()
    is_active=models.BooleanField(default=True)
    def __str__(self): return f'{self.user} · {self.get_source_display()}'

class DogRegistration(models.Model):
    STATUS=[('pending','승인대기'),('approved','승인'),('rejected','반려')]
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='dogs'); dog_name=models.CharField(max_length=80); registration_no=models.CharField(max_length=80,blank=True); breed=models.CharField(max_length=100,blank=True); birth_date=models.DateField(null=True,blank=True); gender=models.CharField(max_length=20,blank=True); status=models.CharField(max_length=20,choices=STATUS,default='pending'); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.dog_name
class MemberBenefit(models.Model):
    title=models.CharField(max_length=150); description=models.TextField(blank=True); valid_from=models.DateField(null=True,blank=True); valid_to=models.DateField(null=True,blank=True); is_active=models.BooleanField(default=True); sort_order=models.IntegerField(default=0)
    def __str__(self): return self.title
class Inquiry(models.Model):
    STATUS=[('new','신규'),('processing','처리중'),('done','답변완료')]
    name=models.CharField(max_length=80); phone=models.CharField(max_length=30,blank=True); email=models.EmailField(blank=True); subject=models.CharField(max_length=200); body=models.TextField(); status=models.CharField(max_length=20,choices=STATUS,default='new'); admin_memo=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.subject


# === WEBSITE SITE SETTING ===
class SiteSetting(models.Model):
    site_name = models.CharField(
        max_length=120,
        default='경상남도 반려견 협회',
    )
    site_subtitle = models.CharField(
        max_length=200,
        blank=True,
        default='Gyeongnam Pet Dog Association',
    )
    logo = models.ImageField(
        upload_to='site/logo/',
        blank=True,
    )
    logo_video = models.FileField(
        upload_to='site/logo/video/',
        blank=True,
    )

    # Intro/global brand presentation controls.
    header_logo_size = models.PositiveSmallIntegerField(default=48)
    header_site_name_size = models.PositiveSmallIntegerField(default=17)
    header_site_name_weight = models.PositiveSmallIntegerField(default=800)
    header_subtitle_size = models.PositiveSmallIntegerField(default=12)
    header_subtitle_weight = models.PositiveSmallIntegerField(default=500)
    header_menu_font_size = models.PositiveSmallIntegerField(default=16)
    header_menu_font_weight = models.PositiveSmallIntegerField(default=700)
    intro_header_opacity = models.PositiveSmallIntegerField(default=82)

    # Canonical intro editing canvas.
    intro_stage_width = models.PositiveIntegerField(default=1920)
    intro_stage_height = models.PositiveIntegerField(default=864)

    hero_eyebrow = models.CharField(
        max_length=200,
        blank=True,
        default='GYEONGNAM PET DOG ASSOCIATION',
    )
    hero_title = models.CharField(
        max_length=300,
        default='믿을 수 있는\n반려견 협회',
    )
    hero_meta1 = models.CharField(
        max_length=300,
        blank=True,
        default='고유번호 539-80-02508 · 대표자 심규진',
    )
    hero_meta2 = models.CharField(
        max_length=300,
        blank=True,
        default='경남 창원시 성산구 용지로 159, iM뱅크(대구은행) 4층 405호',
    )

    hero_button1_text = models.CharField(
        max_length=80,
        blank=True,
        default='반려견 회원등록',
    )
    hero_button1_link = models.CharField(
        max_length=500,
        blank=True,
        default='#join',
    )
    hero_button2_text = models.CharField(
        max_length=80,
        blank=True,
        default='회원혜택',
    )
    hero_button2_link = models.CharField(
        max_length=500,
        blank=True,
        default='benefits.html',
    )

    # === KAKAO MAP SETTINGS ===
    kakao_javascript_key = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='카카오 JavaScript 키',
    )
    kakao_rest_api_key = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='카카오 REST API 키',
    )

    favicon = models.ImageField(upload_to='site/favicon/', blank=True)
    meta_description = models.CharField(max_length=320, blank=True, default='')
    meta_keywords = models.CharField(max_length=500, blank=True, default='')
    canonical_url = models.URLField(max_length=500, blank=True, default='https://thepetkorea.co.kr/')
    naver_site_verification = models.CharField(max_length=255, blank=True, default='')
    google_site_verification = models.CharField(max_length=255, blank=True, default='')
    og_title = models.CharField(max_length=200, blank=True, default='')
    og_description = models.CharField(max_length=320, blank=True, default='')
    og_image_url = models.URLField(max_length=1000, blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '홈페이지 기본설정'
        verbose_name_plural = '홈페이지 기본설정'

    def __str__(self):
        return self.site_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class IntroLayer(models.Model):
    LAYER_TYPES = [
        ('text', '텍스트'),
        ('image', '이미지'),
        ('video', '동영상'),
        ('button', '버튼'),
        ('overlay', '오버레이'),
    ]
    ANIMATIONS = [
        ('fade-up', 'Fade Up'),
        ('fade', 'Fade In'),
        ('slide-left', 'Slide Left'),
        ('slide-right', 'Slide Right'),
        ('zoom-in', 'Zoom In'),
        ('none', '없음'),
    ]
    OBJECT_FITS = [('contain', 'Contain'), ('cover', 'Cover')]

    hero = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='intro_layers',
        limit_choices_to={'kind': 'hero'},
    )
    name = models.CharField(max_length=100, default='새 레이어')
    layer_type = models.CharField(max_length=20, choices=LAYER_TYPES, default='text')
    text = models.TextField(blank=True, default='')
    link = models.CharField(max_length=500, blank=True, default='')
    image = models.FileField(upload_to='intro/layers/', blank=True)
    video = models.FileField(upload_to='intro/layers/video/', blank=True)

    x_px = models.IntegerField(default=120)
    y_px = models.IntegerField(default=220)
    width_px = models.PositiveIntegerField(default=520)
    height_px = models.PositiveIntegerField(default=120)

    opacity = models.PositiveSmallIntegerField(default=100)
    z_index = models.PositiveSmallIntegerField(default=2)
    font_size = models.PositiveSmallIntegerField(default=40)
    font_weight = models.PositiveSmallIntegerField(default=800)
    color = models.CharField(max_length=40, default='#ffffff')
    background = models.CharField(max_length=80, blank=True, default='transparent')
    border_radius = models.PositiveSmallIntegerField(default=0)
    object_fit = models.CharField(max_length=10, choices=OBJECT_FITS, default='contain')

    animation = models.CharField(max_length=20, choices=ANIMATIONS, default='fade-up')
    animation_delay_ms = models.PositiveIntegerField(default=200)
    animation_duration_ms = models.PositiveIntegerField(default=700)

    is_visible = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['z_index', 'sort_order', 'pk']

    def __str__(self):
        return f'{self.hero_id} · {self.name}'


# === ABOUT PAGE CMS ===
class AboutPageSetting(models.Model):
    title_eyebrow=models.CharField(max_length=250,default='OVERVIEW OF THE COMPANION DOG\nASSOCIATION')
    title_heading=models.CharField(max_length=200,default='반려견 협회개요')
    title_tagline=models.CharField(max_length=250,default='반려견과 반려인들의 상호 권익 도모')
    title_media_type=models.CharField(max_length=20,choices=ContentItem.MEDIA_TYPES,default='image')
    title_image=models.FileField(upload_to='about/title/',blank=True)
    title_video=models.FileField(upload_to='about/title/video/',blank=True)
    title_video_url=models.URLField(max_length=1200,blank=True)
    title_contact_text=models.CharField(max_length=250,default='회원 여러분과 함께 성장하는 협회')
    title_contact_info=models.CharField(max_length=300,default='☎ 010-3556-8603　✉ him194200@gmail.com')
    gap_title_greeting=models.PositiveIntegerField(default=0)
    greeting_eyebrow=models.CharField(max_length=100,default='GREETING')
    greeting_title=models.CharField(max_length=100,default='인사말')
    greeting_body=models.TextField(default='안녕하십니까, 경상남도 반려견 협회 홈페이지를 찾아주신 여러분께 진심으로 감사드립니다.\n\n저희 협회는 경상남도에 거주하는 반려견과 반려인들의 상호 권익을 도모하고, 살기 좋은 경상남도를 만들기 위한 공동의 노력을 통해 동물복지 향상에 이바지하고자 설립되었습니다.\n\n반려견 등록 지원, 교육·훈련 프로그램, 제휴 동물병원 의료 지원 등 다양한 사업을 통해 반려인으로서의 긍지를 실현하고, 비반려인과의 유대관계를 형성하는 데 앞장서겠습니다.\n\n앞으로도 회원 여러분과 함께 성장하는 협회가 되도록 최선을 다하겠습니다. 감사합니다.')
    greeting_signature=models.CharField(max_length=200,default='경상남도 반려견 협회 대표자 심규진')
    greeting_subtitle=models.CharField(max_length=200,default='Gyeongnam Pet Dog Association')
    greeting_media_type=models.CharField(max_length=20,choices=ContentItem.MEDIA_TYPES,default='image')
    greeting_image=models.FileField(upload_to='about/greeting/',blank=True)
    greeting_video=models.FileField(upload_to='about/greeting/video/',blank=True)
    greeting_video_url=models.URLField(max_length=1200,blank=True)
    gap_greeting_mission=models.PositiveIntegerField(default=0)
    mission_eyebrow=models.CharField(max_length=100,default='MISSION & VALUES')
    mission_title=models.CharField(max_length=150,default='설립목적 & 핵심가치')
    mission_desc=models.TextField(default='경상남도 반려견 협회는 반려견들과 비반려견인과의 친목과 단결을 도모하고, 이를 바탕으로 반려견 복지 향상에 기여하며, 반려인으로서의 긍지를 실현함과 비반려인과의 유대관계 형성을 목적으로 합니다.')
    values_json=models.JSONField(default=list,blank=True)
    history_title=models.CharField(max_length=100,default='연혁')
    history_media_type=models.CharField(max_length=20,choices=ContentItem.MEDIA_TYPES,default='image')
    history_image=models.FileField(upload_to='about/history/',blank=True)
    history_video=models.FileField(upload_to='about/history/video/',blank=True)
    history_video_url=models.URLField(max_length=1200,blank=True)
    org_title=models.CharField(max_length=100,default='조직 구성')
    org_media_type=models.CharField(max_length=20,choices=ContentItem.MEDIA_TYPES,default='image')
    org_image=models.FileField(upload_to='about/org/',blank=True)
    org_video=models.FileField(upload_to='about/org/video/',blank=True)
    org_video_url=models.URLField(max_length=1200,blank=True)
    member_card_image=models.FileField(upload_to='about/membership/',blank=True)
    partner_sticker_image=models.FileField(upload_to='about/membership/',blank=True)
    updated_at=models.DateTimeField(auto_now=True)
    # ABOUT_MEDIA_DISPLAY_FIELDS_20261001
    title_radius = models.PositiveSmallIntegerField(default=10)
    greeting_radius = models.PositiveSmallIntegerField(default=10)
    history_radius = models.PositiveSmallIntegerField(default=10)
    org_radius = models.PositiveSmallIntegerField(default=10)
    greeting_media_fit = models.CharField(max_length=10, default='contain')
    # ABOUT_GREETING_BADGE_FIELDS_20261001
    greeting_badge_text = models.CharField(max_length=200, default='대표자 심규진')
    greeting_badge_left = models.IntegerField(default=25)
    greeting_badge_bottom = models.IntegerField(default=-20)
    greeting_badge_radius = models.PositiveSmallIntegerField(default=28)
    history_media_fit = models.CharField(max_length=10, default='contain')
    org_media_fit = models.CharField(max_length=10, default='contain')

    @classmethod
    def get_solo(cls):
        obj,_=cls.objects.get_or_create(pk=1)
        if not obj.values_json:
            obj.values_json=[{'icon':'🐾','title':'생명존중','text':'모든 반려견은 소중한 생명이며, 존엄하게 대우받아야 합니다.'},{'icon':'🤝','title':'상생과 공존','text':'반려인과 비반려인이 함께 행복한 지역사회를 만들어갑니다.'},{'icon':'📚','title':'책임있는 문화','text':'올바른 반려 문화 정착을 위한 교육과 캠페인을 지속합니다.'},{'icon':'🏛️','title':'투명한 운영','text':'회원과 지역사회에 투명하게 운영 현황을 공개합니다.'}]; obj.save(update_fields=['values_json'])
        return obj

class AboutHistoryItem(models.Model):
    date=models.CharField(max_length=40); text=models.CharField(max_length=500); sort_order=models.IntegerField(default=0)
    class Meta: ordering=['sort_order','pk']

class AboutOrgItem(models.Model):
    role=models.CharField(max_length=80); count=models.PositiveIntegerField(default=1); sort_order=models.IntegerField(default=0)
    class Meta: ordering=['sort_order','pk']


# ============================================================
# WORLD DOG BREED DATABASE
# ============================================================

class DogBreed(models.Model):
    """
    전 세계 견종 데이터베이스.

    FCI/공인 견종 자료를 구조화하여 저장하고
    사용자 견종 목록 및 상세페이지에서 사용한다.
    """

    # --------------------------------------------------------
    # 기본 식별정보
    # --------------------------------------------------------

    name_ko = models.CharField(
        '견종명',
        max_length=200,
        db_index=True,
    )

    name_en = models.CharField(
        '영문 견종명',
        max_length=200,
        blank=True,
        db_index=True,
    )

    slug = models.SlugField(
        'URL 식별자',
        max_length=220,
        unique=True,
        allow_unicode=True,
    )

    # --------------------------------------------------------
    # FCI 분류
    # --------------------------------------------------------

    fci_group = models.PositiveSmallIntegerField(
        'FCI 그룹',
        null=True,
        blank=True,
        db_index=True,
    )

    fci_group_name = models.CharField(
        'FCI 그룹명',
        max_length=250,
        blank=True,
    )

    fci_section = models.CharField(
        'FCI 섹션',
        max_length=250,
        blank=True,
    )

    fci_standard_no = models.CharField(
        'FCI 표준번호',
        max_length=50,
        blank=True,
        db_index=True,
    )

    # --------------------------------------------------------
    # 견종 기본정보
    # --------------------------------------------------------

    origin = models.CharField(
        '원산지',
        max_length=200,
        blank=True,
    )

    patronage = models.CharField(
        '후원국/관리국',
        max_length=200,
        blank=True,
    )

    use = models.TextField(
        '용도',
        blank=True,
    )

    classification = models.TextField(
        '분류',
        blank=True,
    )

    # --------------------------------------------------------
    # 상세 설명
    # --------------------------------------------------------

    summary = models.TextField(
        '요약',
        blank=True,
    )

    history = models.TextField(
        '역사',
        blank=True,
    )

    appearance = models.TextField(
        '외형',
        blank=True,
    )

    temperament = models.TextField(
        '성격/기질',
        blank=True,
    )

    description = models.TextField(
        '상세 설명',
        blank=True,
    )

    # --------------------------------------------------------
    # 이미지
    # --------------------------------------------------------

    image = models.FileField(
        '대표 이미지',
        upload_to='breeds/',
        blank=True,
        null=True,
    )

    image_url = models.URLField(
        '외부 이미지 URL',
        max_length=1000,
        blank=True,
    )

    image_source = models.CharField(
        '이미지 출처',
        max_length=500,
        blank=True,
    )

    # --------------------------------------------------------
    # 출처 / 자동수집 관리
    # --------------------------------------------------------

    source_name = models.CharField(
        '자료 출처',
        max_length=100,
        blank=True,
    )

    source_url = models.URLField(
        '원문 URL',
        max_length=1000,
        blank=True,
    )

    source_id = models.CharField(
        '원문 식별자',
        max_length=150,
        blank=True,
        db_index=True,
    )

    # 원본에서 추출한 추가 정보를 보존하기 위한 공간
    extra_data = models.JSONField(
        '추가 데이터',
        default=dict,
        blank=True,
    )

    # --------------------------------------------------------
    # 공개 / 정렬
    # --------------------------------------------------------

    is_published = models.BooleanField(
        '공개',
        default=False,
        db_index=True,
    )

    sort_order = models.IntegerField(
        '정렬순서',
        default=0,
    )

    # --------------------------------------------------------
    # 시간
    # --------------------------------------------------------

    # KKF / FCI structured breed information
    height_male = models.CharField(
        max_length=100,
        blank=True,
    )

    height_female = models.CharField(
        max_length=100,
        blank=True,
    )

    purpose_detail = models.TextField(
        blank=True,
    )

    head = models.TextField(
        blank=True,
    )

    neck = models.TextField(
        blank=True,
    )

    body = models.TextField(
        blank=True,
    )

    tail = models.TextField(
        blank=True,
    )

    limbs = models.TextField(
        blank=True,
    )

    gait = models.TextField(
        blank=True,
    )

    coat = models.TextField(
        blank=True,
    )

    size_detail = models.TextField(
        blank=True,
    )

    faults = models.TextField(
        blank=True,
    )

    disqualification = models.TextField(
        blank=True,
    )

    source_group_id = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    source_detail_url = models.URLField(
        max_length=1000,
        blank=True,
    )

    collected_at = models.DateTimeField(
        '최종 수집일',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        '등록일',
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        '수정일',
        auto_now=True,
    )

    class Meta:
        verbose_name = '견종'
        verbose_name_plural = '견종'
        ordering = [
            'fci_group',
            'sort_order',
            'name_ko',
        ]
        indexes = [
            models.Index(
                fields=['fci_group', 'name_ko'],
                name='breed_group_name_idx',
            ),
        ]

    def __str__(self):
        if self.name_en:
            return f'{self.name_ko} ({self.name_en})'

        return self.name_ko


# ============================================================
# NOTICE / COMMUNITY BOARD SYSTEM
# ============================================================

class BoardCategory(models.Model):

    BOARD_TYPES = [
        ('notice', '공지사항'),
        ('community', '자유게시판'),
    ]

    board_type = models.CharField(
        max_length=20,
        choices=BOARD_TYPES,
        db_index=True
    )

    name = models.CharField(
        max_length=80
    )

    slug = models.SlugField(
        max_length=100
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            'board_type',
            'sort_order',
            'id',
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['board_type', 'slug'],
                name='unique_board_category_slug'
            )
        ]

    def __str__(self):
        return f'{self.get_board_type_display()} / {self.name}'


class BoardPost(models.Model):

    BOARD_TYPES = [
        ('notice', '공지사항'),
        ('community', '자유게시판'),
    ]

    board_type = models.CharField(
        max_length=20,
        choices=BOARD_TYPES,
        db_index=True
    )

    category = models.ForeignKey(
        BoardCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='board_posts'
    )

    title = models.CharField(
        max_length=250
    )

    body = models.TextField()

    view_count = models.PositiveIntegerField(
        default=0
    )

    is_published = models.BooleanField(
        default=True
    )

    is_pinned = models.BooleanField(
        default=False
    )

    is_important = models.BooleanField(
        default=False
    )

    is_featured = models.BooleanField(
        default=False
    )

    is_hidden = models.BooleanField(
        default=False
    )

    allow_comments = models.BooleanField(
        default=True
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            '-is_pinned',
            '-published_at',
            '-created_at',
        ]

        indexes = [
            models.Index(
                fields=['board_type', 'is_published']
            ),
            models.Index(
                fields=['board_type', 'category']
            ),
        ]

    def __str__(self):
        return self.title


class BoardAttachment(models.Model):

    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(
        upload_to='board/%Y/%m/%d/'
    )

    original_name = models.CharField(
        max_length=255,
        blank=True
    )

    is_image = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            'sort_order',
            'id',
        ]


class BoardComment(models.Model):

    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='board_comments'
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    body = models.TextField()

    is_hidden = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['created_at']


class BoardLike(models.Model):

    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='board_likes'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                name='unique_board_post_like'
            )
        ]


class BoardReport(models.Model):

    STATUS_CHOICES = [
        ('pending', '접수'),
        ('reviewed', '검토완료'),
        ('dismissed', '문제없음'),
        ('actioned', '조치완료'),
    ]

    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name='reports'
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='board_reports'
    )

    reason = models.CharField(
        max_length=250
    )

    detail = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


# ============================================================
# COMMUNITY GROUP
# 자유게시판 기반 소모임 확장
# ============================================================

class CommunityGroup(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_community_groups'
    )

    name = models.CharField(
        max_length=120
    )

    slug = models.SlugField(
        max_length=140,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    region = models.CharField(
        max_length=80,
        blank=True
    )

    image = models.ImageField(
        upload_to='community/groups/',
        blank=True
    )

    is_public = models.BooleanField(
        default=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class CommunityGroupMember(models.Model):

    ROLES = [
        ('owner', '모임장'),
        ('manager', '운영진'),
        ('member', '회원'),
    ]

    group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='member'
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'user'],
                name='unique_community_group_member'
            )
        ]


class CommunityGroupPost(models.Model):

    group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name='group_posts'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='community_group_posts'
    )

    title = models.CharField(
        max_length=250
    )

    body = models.TextField()

    is_pinned = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            '-is_pinned',
            '-created_at',
        ]


class ChatbotSetting(models.Model):
    """
    Public website AI chatbot configuration.
    One configuration row is used site-wide.
    """

    enabled = models.BooleanField(
        default=True,
        verbose_name='챗봇 사용'
    )

    ai_enabled = models.BooleanField(
        default=False,
        verbose_name='OpenAI 사용'
    )

    bot_name = models.CharField(
        max_length=100,
        default='경상남도 반려견 협회 챗봇',
        verbose_name='챗봇 이름'
    )

    greeting = models.TextField(
        default=(
            '안녕하세요! 경상남도 반려견 협회 챗봇입니다.\n'
            '협회 정보, 반려견 등록·예방접종·법령 등 '
            '무엇이든 물어보세요!'
        ),
        verbose_name='첫 인사말'
    )

    system_prompt = models.TextField(
        blank=True,
        default=(
            '당신은 경상남도 반려견 협회 공식 안내 챗봇입니다. '
            '사용자에게 정확하고 친절하게 답변하세요. '
            '확실하지 않은 정보는 추측하지 말고 협회 문의를 안내하세요.'
        ),
        verbose_name='AI 시스템 지침'
    )

    model_name = models.CharField(
        max_length=100,
        default='gpt-5-mini',
        verbose_name='OpenAI 모델'
    )

    api_key_encrypted = models.TextField(
        blank=True,
        default='',
        verbose_name='OpenAI API Key'
    )

    contact_button_text = models.CharField(
        max_length=100,
        default='☎ 협회 문의하기',
        verbose_name='문의 버튼 문구'
    )

    contact_phone = models.CharField(
        max_length=30,
        default='010-3556-8603',
        verbose_name='문의 전화번호'
    )

    bot_video = models.FileField(
        upload_to='chatbot/',
        blank=True,
        null=True,
        verbose_name='챗봇 영상'
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.bot_name


class TossPaymentSetting(models.Model):
    id=models.PositiveSmallIntegerField(primary_key=True,default=1,editable=False)
    test_client_key=models.CharField(max_length=255,blank=True,default='')
    test_secret_key=models.CharField(max_length=255,blank=True,default='')
    live_client_key=models.CharField(max_length=255,blank=True,default='')
    live_secret_key=models.CharField(max_length=255,blank=True,default='')
    live_enabled=models.BooleanField(default=False)
    annual_fee=models.PositiveIntegerField(default=30000)
    settlement_bank=models.CharField(max_length=80,blank=True,default='')
    settlement_account=models.CharField(max_length=100,blank=True,default='')
    settlement_holder=models.CharField(max_length=100,blank=True,default='')
    settlement_cycle=models.CharField(max_length=100,blank=True,default='')
    card_fee_rate=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    updated_at=models.DateTimeField(auto_now=True)
    @classmethod
    def get_solo(cls):
        obj,_=cls.objects.get_or_create(pk=1);return obj

class PaymentRecord(models.Model):
    ENVIRONMENTS=[('test','테스트'),('live','라이브')]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='payment_records')
    environment=models.CharField(max_length=10,choices=ENVIRONMENTS,default='test',db_index=True)
    order_id=models.CharField(max_length=64,unique=True)
    payment_key=models.CharField(max_length=200,blank=True,default='',db_index=True)
    order_name=models.CharField(max_length=100,default='정회원 연회비')
    amount=models.PositiveIntegerField(default=30000)
    status=models.CharField(max_length=30,default='READY',db_index=True)
    method=models.CharField(max_length=50,blank=True,default='')
    approved_at=models.DateTimeField(null=True,blank=True)
    raw_response=models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']
