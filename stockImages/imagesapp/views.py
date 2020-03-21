from django.shortcuts import render
from rest_framework.generics import *
from django.contrib.auth.models import User
from .models import *
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from .serializer import *
import re
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.parsers import FormParser,MultiPartParser
from django.contrib.auth import authenticate
import json
# Create your views here.

class ImageUploadView(CreateAPIView):
    queryset = ImageModel.objects.all()
    serializer_class = ImageUploadSerializer
    parser_classes = (MultiPartParser,FormParser)

    def create(self, request, *args, **kwargs):
        data = request.data
        # data["user"]=request.user
        newData = dict([])
        for field in request.FILES.keys():
            newData["images"] = []
            for image in request.FILES.getlist(field):
                newinnerData = dict([])
                newinnerData["imagesrc"] = image
                newData["images"].append(newinnerData)
        newData["description"] = data["description"]
        print("nsdds",newData)
        serializer = self.get_serializer(data=newData)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)
        return Response(serializer.data)


class ImagesListView(ListAPIView):
    queryset = ImageSourceModel.objects.all()
    serializer_class = ImageSourceSerializer

    def filter_queryset_date(self,dictonary,queryset):
        fromDate = dictonary.get("from", None)
        toDate = dictonary.get("to", None)
        onDate = dictonary.get("date",None)
        print(fromDate)

        if toDate and fromDate:
            toDate=datetime.strptime(toDate, "%d-%m-%Y").date()
            fromDate=datetime.strptime(fromDate, "%d-%m-%Y").date()
            return queryset.filter(image__createdDate__range=(fromDate, toDate))
        elif toDate:
            toDate=datetime.strptime(toDate, "%d-%m-%Y").date()
            print(toDate,"sasaas")
            return queryset.filter(image__createdDate__lte=toDate)
        elif onDate:
            dateList = onDate.split('-')

            return queryset.filter(image__createdDate=onDate)
        elif fromDate:
            fromDate=datetime.strptime(fromDate, "%d-%m-%Y").date()
            return queryset.filter(image__createdDate__gte=fromDate)
        else:
            return queryset

    def filter_queryset_tags(self,dictonary,queryset):
        tags = dictonary.get("tags",None)
        if tags :
            tags = tags.split(',')
            return queryset.filter(tag__tagname__in=tags)
        else:
            return queryset

    def filter_desc_queryset(self,desc_queries,queryset):
        if len(desc_queries)>0:
            # desc_queries = [re.findall(r'\"[^\".]*\"',text) for text in desc_queries]
            s = ''.join(desc_queries)
            desc_str = ''.join(s.split('"'))
            return queryset.filter(image__description__icontains=desc_str)
        else:
            return queryset

    def get_queryset(self):
        queryset = self.queryset.all()
        searchText = self.request.GET.get('search',None)
        if searchText:
            queries = re.findall(r'\b(\w+):(\S+)\b', searchText,flags=re.IGNORECASE)
            queries_dict = dict(queries)
            desc_queries = re.findall(r'desc:\"[^\".]*\"', searchText)
            queryset =self.filter_desc_queryset(desc_queries,
                        self.filter_queryset_tags(queries_dict,self.filter_queryset_date(queries_dict,queryset)))
        return queryset.all()

class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    queryset = User.objects.all()

class LoginView(APIView):
    def post(self,request):
        username=request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username,password=password)
        if user is not None:
            return JsonResponse({"username":user.username})
        else:
            return JsonResponse({"error":"failed"})