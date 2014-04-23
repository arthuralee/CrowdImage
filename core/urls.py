from django.conf.urls import patterns, url
 
from core import views
 
urlpatterns = patterns('',
    url(r'^api/submitpic/?$', views.submitPic, name='submitPic'),
    url(r'^api/getblock/?$', views.getBlock, name='getBlock'),
    url(r'^api/returnblock/?$', views.returnBlock, name='returnBlock'),
)