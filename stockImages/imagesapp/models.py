from django.db import models
from django.contrib.auth.models import User
from datetime import date

class TagsModel(models.Model):
    tagname = models.CharField(max_length=100,unique=True)

class ImageModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    description = models.TextField(default='',null=True)
    createdDate = models.DateField(default=date.today())


class ImageSourceModel(models.Model):
    image = models.ForeignKey(ImageModel,on_delete=models.CASCADE,null=True,related_name="images")
    imagesrc = models.ImageField(upload_to='documents/')
    tag = models.ManyToManyField(TagsModel)

class RenditionImages(models.Model):
    real_image = models.ForeignKey(ImageSourceModel,on_delete=models.CASCADE,related_name="thumbnails")
    thumbnail_img = models.ImageField(upload_to='documents/')