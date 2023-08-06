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

from .models import User, Post, Follow


class NewPostForm(forms.Form):
    content = forms.CharField(label="New Post", widget=forms.Textarea)


def index(request, pageNum=1):
    posts = Post.objects.all().order_by("-timePosted")
    pages = Paginator(posts, 10) 
    return render(request, "network/index.html", {
        "form": NewPostForm(),
        "pages": pages,
        "currentPageNum": pageNum,
        "posts": pages.page(pageNum)
    })

@csrf_exempt
@login_required
def postAPI(request, post_id):
    # Query for requested post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Update post data
    elif request.method == "PUT":

        data = json.loads(request.body)
        if data.get("hearts") is not None:
            post.hearts = data["hearts"]
        if data.get("content") is not None:
            post.content = data["content"]

        post.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@login_required
def edit(request, post_id):
    post = Post.objects.get(id=post_id)
    if post.postingUser.id != request.user.id:
        return HttpResponse("Error: not authorized to edit that post.")
    return render(request, "network/edit.html", {
        "form": NewPostForm(),
    })
    

@login_required
def following(request, pageNum=1):
    user = User.objects.get(id=request.user.id)
    follows = user.users.all() # I don't understand why this works. I thought it should be users_they_follow, but it's not...
    post_list = []
    for follow in follows:
        posts = Post.objects.filter(postingUser=User(id=follow.user_they_follow.id),)
        for post in posts:
            post_list.append(post)
    # sort the list so they show up in the correct order. This would be a performance bottleneck at scale.
    post_list.sort(key=lambda x: x.timePosted, reverse=True)
    pages = Paginator(post_list, 10) 
    return render(request, "network/following.html", {
        "pages": pages,
        "currentPageNum": pageNum,
        "posts": pages.page(pageNum)
    })

def user(request,user_id,pageNum=1):
    isNotSelf = user_id!=request.user.id
    user_is_following = User.objects.get(id=user_id).users_they_follow.all().filter(user=request.user.id).exists()
    posts = Post.objects.filter(postingUser=User(id=user_id),).order_by("-timePosted")
    pages = Paginator(posts, 10) 
    return render(request, "network/user.html",{
        "user": User.objects.get(id=user_id),
        "pages": pages,
        "currentPageNum": pageNum,
        "posts": pages.page(pageNum),
        "followers":User.objects.get(id=user_id).users.count(),
        "following":User.objects.get(id=user_id).users_they_follow.count(),
        "user_is_following": user_is_following,
        "isNotSelf" : isNotSelf
    })

def unfollow(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        follow = Follow.objects.get(user=request.user.id,user_they_follow=user_id)
        follow.delete()
        return HttpResponseRedirect(reverse("user",args=(user_id,)))



def follow(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]

        # check if user is already in the users_they_follow_list
        users_they_follow = User.objects.get(id=user_id).users_they_follow.all()
        if users_they_follow.filter(pk=request.user.id).exists():
            return HttpResponseRedirect(reverse("user",args=(user_id,)))
        else:
            follow = Follow(user=User(request.user.id),
                            user_they_follow=User(user_id))
            follow.save()
            return HttpResponseRedirect(reverse("user",args=(user_id,)))

@login_required
def add(request):

    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = Post(
                    content = form.cleaned_data["content"],
                    hearts = 0,
                    postingUser = User(request.user.id)
                    )
            post.save()

    return HttpResponseRedirect(reverse("index"))

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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
