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

class ContentItem(models.Model):
    KINDS=[('notice','공지사항'),('community','자유게시판'),('breed','전 세계 견종'),('intro','인트로 갤러리'),('popup','팝업')]
    kind=models.CharField(max_length=20,choices=KINDS,db_index=True); title=models.CharField(max_length=200); label=models.CharField(max_length=80,blank=True); body=models.TextField(blank=True); image=models.FileField(upload_to='content/%Y/%m/',blank=True); link=models.CharField(max_length=500,blank=True); is_published=models.BooleanField(default=True); sort_order=models.IntegerField(default=0); popup_start=models.DateTimeField(null=True,blank=True); popup_end=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','-created_at']
    def __str__(self): return self.title
