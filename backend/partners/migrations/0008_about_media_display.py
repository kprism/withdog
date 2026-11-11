from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("partners","0007_about_page_cms")]
    operations=[
      migrations.AddField(model_name="aboutpagesetting",name="title_radius",field=models.PositiveSmallIntegerField(default=10)),
      migrations.AddField(model_name="aboutpagesetting",name="greeting_radius",field=models.PositiveSmallIntegerField(default=10)),
      migrations.AddField(model_name="aboutpagesetting",name="history_radius",field=models.PositiveSmallIntegerField(default=10)),
      migrations.AddField(model_name="aboutpagesetting",name="org_radius",field=models.PositiveSmallIntegerField(default=10)),
      migrations.AddField(model_name="aboutpagesetting",name="greeting_media_fit",field=models.CharField(default="contain",max_length=10)),
      migrations.AddField(model_name="aboutpagesetting",name="history_media_fit",field=models.CharField(default="contain",max_length=10)),
      migrations.AddField(model_name="aboutpagesetting",name="org_media_fit",field=models.CharField(default="contain",max_length=10)),
    ]
