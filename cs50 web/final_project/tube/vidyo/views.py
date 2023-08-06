from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from PIL import Image
from django.core.exceptions import ValidationError


from .models import User, Video, Comment, Subscribe, View, Rating

class NewUploadForm(forms.Form):
    title = forms.CharField(label="title",max_length=100)
    description = forms.CharField(label="Description", widget=forms.Textarea, max_length=280)
    thumbnail = forms.ImageField(allow_empty_file=False)
    video = forms.FileField(allow_empty_file=False)

class CommentForm(forms.Form):
    comment_text = forms.CharField(label="Add a comment", max_length=280)

def index(request):
    if request.user.id:
        user = User.objects.get(id=request.user.id)
        subscriptions = user.subscriptions.all() # I don't understand why this works. I thought it should be users_they_follow, but it's not...
        video_list = []
        for sub in subscriptions:
            videos = Video.objects.filter(channel=User(id=sub.subscriptions.id),)
            for video in videos:
                video_list.append(video)
        # sort the list so they show up in the correct order. This would be a performance bottleneck at scale.
        video_list.sort(key=lambda x: x.timestamp, reverse=True)
        return render(request, "vidyo/index.html",
                    {"videos":video_list})
    else:
        return render(request, "vidyo/index.html",
                    {"videos":Video.objects.all()})


@csrf_exempt
@login_required
def videoAPI(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return JsonResponse({"error": "Video not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(video.serialize())

    elif request.method == "PUT":

        data = json.loads(request.body)
        if data.get("rating") is not None:
            video.rating = data["rating"]
        video.save()

        return HttpResponse(status=204)

    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def watch(request, video_id):

    # save the fact that this video has been viewed.
    view = View(video=Video.objects.get(id=video_id),
                viewer=User.objects.get(id=request.user.id))
    view.save()

    channel_id = Video.objects.get(id=video_id).channel.id
    isNotSelf = channel_id !=request.user.id
    user_is_subscribed = User.objects.get(id=channel_id).subscribers.all().filter(subscriber=request.user.id).exists()
    print(User.objects.get(id=channel_id).subscribers.all())
    return render(request, "vidyo/watch.html",{
      "video": Video.objects.get(id=video_id),
      "commentForm": CommentForm(),
      "isNotSelf": isNotSelf,
      "user_is_subscribed": user_is_subscribed,
      "comments":Comment.objects.filter(video=video_id).order_by("-timestamp")  })

@login_required
def comment(request):
    if request.method == "POST":
        video_id = request.POST["video_id"]
        video = Video.objects.get(id=video_id)
        comment = Comment(channel=User(request.user.id),
                          video=video,
                          commentText=request.POST["comment_text"])

        comment.save()
        return HttpResponseRedirect(reverse("watch", args=(video_id,)))

# TOOD figure out the search route.

def unsubscribe(request):
    if request.method == "POST":
        channel_id = request.POST["channel_id"]
        video_id = request.POST["video_id"]
        subscription = Subscribe.objects.get(subscriber=request.user.id,subscriptions=channel_id)
        subscription.delete()
        return HttpResponseRedirect(reverse("watch", args=(video_id,)))

def subscribe(request):
    if request.method == "POST":
        channel_id = request.POST["channel_id"]
        video_id = request.POST["video_id"]

        # check if user is already subscribed
        subscriptions = User.objects.get(id=channel_id).subscriptions.all()
        if subscriptions.filter(pk=request.user.id).exists():
            return HttpResponseRedirect(reverse("watch", args=(video_id,)))
        else:
            subscribe = Subscribe(subscriber=User(request.user.id),
                            subscriptions=User(channel_id))
            subscribe.save()
            return HttpResponseRedirect(reverse("watch", args=(video_id,)))


def viewed(request):
  return render(request, "vidyo/viewed.html",
                {"videos":Video.objects.all().annotate(view_count=Count('views')).order_by('-view_count')})

def discussed(request):
  return render(request, "vidyo/discussed.html",
                {"videos":Video.objects.all().annotate(comment_count=Count('comments')).order_by('-comment_count')})

def channel(request,channel_id):
  return render(request, "vidyo/your-videos.html",{
      "videos":Video.objects.filter(channel=channel_id)
  })

def rating(request):
    if request.method == "POST":
        video_id = request.POST["video_id"]
        rating = request.POST["rating"]

        r = Rating(video=Video(video_id),
                        rater= User(request.user.id),
                        rating=rating
                        )
        r.save


def upload(request):
   if request.method == "POST":

        form = NewUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['thumbnail']
            video = Video(
                    title = form.cleaned_data["title"],
                    description = form.cleaned_data["description"],
                    thumbnail = request.FILES['thumbnail'],
                    video = request.FILES['video'],
                    channel = User(request.user.id)
                    )
            try:
                #TODO: ideally you'd test each field and provide a more user firendly error message.
                video.full_clean()
                video.save()
                return HttpResponseRedirect(reverse("index"))
            except ValidationError as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Invalid form")
        
   else:
      return render(request, "vidyo/upload.html", {
        "form": NewUploadForm(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "vidyo/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "vidyo/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "vidyo/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "vidyo/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "vidyo/register.html")
