from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('upload',views.upload,name='upload'),
    path('apimage',views.districtplot,name='plot'),
    path('plot',views.plot,name='barplot'),
    path('form.html',views.plot,name='form'),

]