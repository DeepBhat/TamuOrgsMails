
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('update', views.update, name="update"),
    path('download', views.download_csv, name="download"),
    path('mass-email', views.mass_email, name="mass_email")
]
