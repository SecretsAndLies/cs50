from django.urls import path
from . import views


urlpatterns = [
     path("", views.index, name="index"),
     path("viewed", views.viewed, name="viewed"),
     path("discussed", views.discussed, name="discussed"),
     path("channel/<int:channel_id>", views.channel, name="channel"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("upload", views.upload, name="upload"),
    path("comment", views.comment, name="comment"),
    path("subscribe", views.subscribe, name="subscribe"),
    path("unsubscribe", views.unsubscribe, name="unsubscribe"),
    path("video-api/<int:video_id>", views.videoAPI, name="videoAPI"),

     path("watch/<int:video_id>", views.watch, name="watch")
 ]