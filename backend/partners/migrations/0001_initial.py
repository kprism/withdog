from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[
      migrations.CreateModel(name='PartnerCategory',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('code',models.SlugField(unique=True)),('name',models.CharField(max_length=50)),('sort_order',models.PositiveSmallIntegerField(default=0))]),
      migrations.CreateModel(name='Partner',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=150)),('address',models.CharField(max_length=300)),('phone',models.CharField(blank=True,max_length=40)),('city',models.CharField(db_index=True,max_length=30)),('latitude',models.DecimalField(blank=True,decimal_places=7,max_digits=10,null=True)),('longitude',models.DecimalField(blank=True,decimal_places=7,max_digits=10,null=True)),('is_affiliated',models.BooleanField(default=False)),('is_active',models.BooleanField(default=True)),('source',models.CharField(blank=True,max_length=100)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('category',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='partners',to='partners.partnercategory'))],options={'ordering':['city','name']}),
      migrations.AddConstraint(model_name='partner',constraint=models.UniqueConstraint(fields=('category','name','address'),name='uniq_partner_location')),
      migrations.CreateModel(name='PartnerBenefit',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('title',models.CharField(max_length=150)),('description',models.TextField(blank=True)),('active',models.BooleanField(default=True)),('partner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='benefits',to='partners.partner'))])]
