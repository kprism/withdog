from django.conf import settings
from django.db import models

class PartnerCategory(models.Model):
    code=models.SlugField(unique=True); name=models.CharField(max_length=50); sort_order=models.PositiveSmallIntegerField(default=0)
    def __str__(self): return self.name
class Partner(models.Model):
    category=models.ForeignKey(PartnerCategory,on_delete=models.PROTECT,related_name='partners'); name=models.CharField(max_length=150); address=models.CharField(max_length=300); phone=models.CharField(max_length=40,blank=True); city=models.CharField(max_length=30,db_index=True); latitude=models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True); longitude=models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True); is_affiliated=models.BooleanField(default=False); is_active=models.BooleanField(default=True); source=models.CharField(max_length=100,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['category','name','address'],name='uniq_partner_location')]; ordering=['city','name']
    def __str__(self): return self.name
class PartnerBenefit(models.Model):
    partner=models.ForeignKey(Partner,on_delete=models.CASCADE,related_name='benefits'); title=models.CharField(max_length=150); description=models.TextField(blank=True); active=models.BooleanField(default=True)
    def __str__(self): return f'{self.partner} · {self.title}'
class ContentItem(models.Model):
    KINDS=[('notice','공지사항'),('community','자유게시판'),('breed','전 세계 견종'),('intro','인트로 갤러리'),('popup','팝업')]
    kind=models.CharField(max_length=20,choices=KINDS,db_index=True); title=models.CharField(max_length=200); label=models.CharField(max_length=80,blank=True); body=models.TextField(blank=True); image=models.FileField(upload_to='content/%Y/%m/',blank=True); link=models.CharField(max_length=500,blank=True); is_published=models.BooleanField(default=True); sort_order=models.IntegerField(default=0); popup_start=models.DateTimeField(null=True,blank=True); popup_end=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','-created_at']
    def __str__(self): return self.title

class MemberProfile(models.Model):
    GENDERS=[('M','남성'),('F','여성'),('O','기타')]; STATUSES=[('general','일반회원'),('pending','정회원 승인대기'),('regular','정회원'),('withdrawn','탈퇴')]
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='member_profile'); name=models.CharField(max_length=80); birth_date=models.DateField(null=True,blank=True); gender=models.CharField(max_length=1,choices=GENDERS,blank=True); phone=models.CharField(max_length=30,blank=True); region=models.CharField(max_length=40,blank=True); address_detail=models.CharField(max_length=250,blank=True); privacy_agreed=models.BooleanField(default=False); regular_member_requested=models.BooleanField(default=False); membership_status=models.CharField(max_length=20,choices=STATUSES,default='general'); joined_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name or self.user.get_username()
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
