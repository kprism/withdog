from django.db import migrations, models

def seed_hero(apps, schema_editor):
    ContentItem=apps.get_model('partners','ContentItem'); SiteSetting=apps.get_model('partners','SiteSetting')
    setting=SiteSetting.objects.filter(pk=1).first()
    defaults={
      'hero_eyebrow': getattr(setting,'hero_eyebrow','GYEONGNAM PET DOG ASSOCIATION') if setting else 'GYEONGNAM PET DOG ASSOCIATION',
      'hero_title': getattr(setting,'hero_title','믿을 수 있는\n반려견 협회') if setting else '믿을 수 있는\n반려견 협회',
      'hero_meta1': getattr(setting,'hero_meta1','고유번호 539-80-02508 · 대표자 심규진') if setting else '고유번호 539-80-02508 · 대표자 심규진',
      'hero_meta2': getattr(setting,'hero_meta2','경남 창원시 성산구 용지로 159, iM뱅크(대구은행) 4층 405호') if setting else '경남 창원시 성산구 용지로 159, iM뱅크(대구은행) 4층 405호',
      'hero_button1_text': getattr(setting,'hero_button1_text','반려견 회원등록') if setting else '반려견 회원등록',
      'hero_button1_link': getattr(setting,'hero_button1_link','#join') if setting else '#join',
      'hero_button2_text': getattr(setting,'hero_button2_text','회원혜택') if setting else '회원혜택',
      'hero_button2_link': getattr(setting,'hero_button2_link','benefits.html') if setting else 'benefits.html',
    }
    existing=list(ContentItem.objects.filter(kind='hero').order_by('sort_order','pk'))
    if existing:
        for x in existing:
            changed=[]
            for k,v in defaults.items():
                if not getattr(x,k,''):
                    setattr(x,k,v); changed.append(k)
            if changed: x.save(update_fields=changed)
        return
    urls=[
      'https://images.unsplash.com/photo-1558788353-f76d92427f16?auto=format&fit=crop&w=2000&q=85',
      'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=2000&q=85',
      'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?auto=format&fit=crop&w=2000&q=85',
    ]
    for i,url in enumerate(urls,1): ContentItem.objects.create(kind='hero',title=f'슬라이드 {i}',sort_order=i,media_type='image',image_url=url,is_published=True,autoplay=True,muted=True,loop=True,**defaults)

class Migration(migrations.Migration):
    dependencies=[('partners','0005_sitesetting')]
    operations=[
      migrations.AddField(model_name='contentitem',name='image_url',field=models.URLField(blank=True,max_length=1200)),
      migrations.AddField(model_name='contentitem',name='hero_eyebrow',field=models.CharField(blank=True,max_length=200)),
      migrations.AddField(model_name='contentitem',name='hero_title',field=models.CharField(blank=True,max_length=300)),
      migrations.AddField(model_name='contentitem',name='hero_meta1',field=models.CharField(blank=True,max_length=300)),
      migrations.AddField(model_name='contentitem',name='hero_meta2',field=models.CharField(blank=True,max_length=300)),
      migrations.AddField(model_name='contentitem',name='hero_button1_text',field=models.CharField(blank=True,max_length=80)),
      migrations.AddField(model_name='contentitem',name='hero_button1_link',field=models.CharField(blank=True,max_length=500)),
      migrations.AddField(model_name='contentitem',name='hero_button2_text',field=models.CharField(blank=True,max_length=80)),
      migrations.AddField(model_name='contentitem',name='hero_button2_link',field=models.CharField(blank=True,max_length=500)),
      migrations.RunPython(seed_hero,migrations.RunPython.noop),
    ]
