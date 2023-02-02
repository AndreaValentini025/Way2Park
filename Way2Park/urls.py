from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hello', views.hello, name='hello'),
    path('homepage', views.ParcheggiListView.as_view(), name='homepage'),
    path('link',views.formAssociaTargaMP, name='link'),
    path('associazione', views.associazione, name='associazione'),
]