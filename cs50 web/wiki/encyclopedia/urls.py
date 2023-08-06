from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("random", views.random, name="random"),
    path("edit", views.edit, name="edit"),
    path("wiki/<str:title>", views.article, name="article"),

]
