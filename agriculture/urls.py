from django.urls import path

from . import views


app_name = "agriculture"

urlpatterns = [
    path("", views.index, name="index"),
    path("form/", views.load_form, name="load-form"),
    path("calculate/<slug:slug>/", views.calculate, name="calculate"),
]
