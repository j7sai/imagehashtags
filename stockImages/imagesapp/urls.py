from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^image/$',ImageUploadView.as_view()),
    url(r'^images/$',ImagesListView.as_view()),

]