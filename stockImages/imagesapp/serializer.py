from rest_framework.serializers import ModelSerializer,RelatedField
from rest_framework import serializers
from .models import *
from PIL import Image
import os,re
from django.contrib.auth.hashers import make_password
from .utils import custom_exception_handler
from rest_framework.exceptions import APIException

SAMPLE_TAGS = ("food", "sports", "animals", "transport", "economics", "movies", "actors")

class TagModelSerializer(RelatedField):
    def to_representation(self, value):
        return '{}'.format(value.tagname)

class ThumbnailsImagesSerializer(RelatedField):
    def to_representation(self, value):
        return '{}'.format(value.thumbnail_img)

class ImageSourceSerializer(ModelSerializer):
    tag = TagModelSerializer(many=True,read_only=True)

    class Meta:
        model = ImageSourceModel
        fields = ("imagesrc","tag")

class SignUpSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("username","email","password","first_name","last_name")
    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return User.objects.create(**validated_data)

class ImageUploadSerializer(ModelSerializer):
    SIZES_LIST = list([])
    SIZE=list([])

    MIN_ASPECT_RATIO = 9/16
    MAX_ASPECT_RATIO = 16/9
    SHORTER_EDGE_MIN = 1200
    RESHORTER_EDGE_Lengths = [240,720]

    TAGS_LIST = []

    FAIL_IMAGES_COUNT = 0

    images = ImageSourceSerializer(many=True)
    class Meta:
        model = ImageModel
        fields = ("description","images")

    def get_resize_image_filename(self,oldimg,filename,size,counter):
        newimg = oldimg.resize(tuple(size))
        new_filename = 'documents/thumbenail{0}_{1}'.format(counter,filename)
        if not os.path.exists(new_filename):
            newimg.save(new_filename)
            return new_filename

    def check_shorter_edge(self):
        shortedge = min(self.SIZE)
        if shortedge>self.SHORTER_EDGE_MIN:
            return True
        else:
            return False

    def check_aspect_ratio(self,aspect):
        if self.MIN_ASPECT_RATIO <= aspect <= self.MAX_ASPECT_RATIO:
            width = self.SIZE[0]
            height = self.SIZE[1]
            if width > height:
                self.SIZES_LIST = list(map(lambda a: list([width,height-a]),self.RESHORTER_EDGE_Lengths))
                return True
            elif width < height:
                self.SIZES_LIST = list(map(lambda a: list([width-a,height]),self.RESHORTER_EDGE_Lengths))
                return True
            else:
                self.SIZES_LIST = list(map(lambda a: list([width,height-a]),self.RESHORTER_EDGE_Lengths))
                return True
        return False

    def fetech_tags_api(self,image):
        return SAMPLE_TAGS

    def filter_tags_description(self,desc):
        r = re.compile(r'#\b(\w+)\b')
        lis = r.findall(desc)
        self.TAGS_LIST = lis

    def create_img_tag_relations(self,image_object):
        lis = TagsModel.objects.filter(tagname__in=self.TAGS_LIST)
        for obj in lis :
            image_object.tag.add(obj)
        image_object.save()

    def create_img_tags(self,image):
        sample_tags=self.fetech_tags_api(image)
        self.TAGS_LIST.extend(sample_tags)
        self.TAGS_LIST = list(set(self.TAGS_LIST))
        spl = set(self.TAGS_LIST)
        dblis = TagsModel.objects.all().values_list('tagname',flat=True)
        filter_set = spl-set(dblis)
        filter_list = [TagsModel(tagname=i) for i in list(filter_set)]
        TagsModel.objects.bulk_create(filter_list)

    def create_image(self,image,imagedetails):
        validated_data = dict([('imagesrc',image),('image',imagedetails)])
        image = ImageSourceSerializer.create(ImageSourceSerializer(),validated_data)
        return image

    def create_images_sources(self,imageObj,imagedetails):
        image = imageObj["imagesrc"]
        imgrc = Image.open(image)
        width, height = imgrc.size
        self.SIZE = list([width, height])
        aspect_ratio = width / height
        if self.check_aspect_ratio(aspect_ratio) and self.check_shorter_edge():
            imageobject = self.create_image(image,imagedetails)
            self.create_img_tags(imgrc)
            self.create_img_tag_relations(imageobject)
            filename = str(image)
            counter = 1
            for size in self.SIZES_LIST:
                data = dict([('thumbnail_img', self.get_resize_image_filename(imgrc, filename, size, counter)),
                             ('real_image', imageobject)])
                RenditionImages.objects.create(**data)
                counter += 1
        else:
            self.FAIL_IMAGES_COUNT +=1

    def create(self, validated_data):
        images = validated_data.pop("images")
        desc = validated_data["description"]
        self.filter_tags_description(desc)
        imagedetails = super(ImageUploadSerializer, self).create(validated_data)
        for image in images:
            self.create_images_sources(image,imagedetails)
        if len(images)==self.FAIL_IMAGES_COUNT:
            imagedetails.delete()
            print("dsdsdsdsdsdsdsddsdsd")
            raise APIException(detail="AllImagesFailed",code=400)
        elif self.FAIL_IMAGES_COUNT>0:
            raise APIException(detail="PartialImagesSuccess-{0},{1}".format(self.FAIL_IMAGES_COUNT,len(images)-self.FAIL_IMAGES_COUNT),code=201)
        return imagedetails
