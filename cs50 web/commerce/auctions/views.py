from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Comment, Bid, ItemToWatch
from django.contrib.auth.decorators import login_required

from django import forms


class ListingForm(forms.Form):
    choices = [
        ("", ""),
        ("sport", "sport"),
        ("magic", "magic"),
        ("home", "home"),
        ("school", "school"),
        ("other", "other"),
    ]  # i tried to query for this list using AuctionListing.objects.all(), but couldn't figure it out.

    title = forms.CharField(label='title', max_length=80)
    description = forms.CharField(label='description', max_length=280)
    currentPrice = forms.IntegerField(label="starting bid", min_value=0)
    imageUrl = forms.URLField(label="image url", required=False)
    category = forms.ChoiceField(label="Category",
                                 choices=choices)


class BidForm(forms.Form):
    bid = forms.IntegerField(label="Bid Amount", min_value=0)


class CommentForm(forms.Form):
    comment_text = forms.CharField(label="Add a comment", max_length=280)


def index(request):

    listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html",
                  {"listings": listings})


@login_required
def watchlist(request):
    if request.method == "POST":
        if request.POST["add_or_remove"] == "add":
            item_id = request.POST["listing_id"]
            listing = AuctionListing.objects.get(id=item_id)

            watch = ItemToWatch(
                item=listing, user=User(request.user.id))
            watch.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

        if request.POST["add_or_remove"] == "remove":
            item_id = request.POST["listing_id"]
            listing = AuctionListing.objects.get(id=item_id)
            ItemToWatch.objects.get(
                item=item_id, user=request.user.id).delete()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    watch_items = ItemToWatch.objects.filter(user=request.user.id)

    return render(request, "auctions/watchlist.html",
                  {"listings": watch_items})


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def bid(request):
    if request.method == "POST":
        item_id = request.POST["listing_id"]
        bidAmount = int(request.POST["bid"])
        item = AuctionListing.objects.get(id=item_id)
        currentPrice = item.currentPrice
        if bidAmount > currentPrice:
            bidObject = Bid(itemId=item,
                            bidderUserId=User(request.user.id),
                            bidAmount=bidAmount)
            bidObject.save()
            item.currentPrice = bidAmount
            item.save()

        else:
            # TODO: fix error so it returns within the page.
            message = "Error: Bid not higher than current bid."
            return HttpResponse(message)

        return HttpResponseRedirect(reverse("listing", args=(item_id,)))


@login_required
def closeItem(request):
    if request.method == "POST":
        item_id = request.POST["listing_id"]
        listing = AuctionListing.objects.get(id=item_id)
        if User(request.user.id) == listing.listingUserName:
            listing.isClosed = True
            listing.save()
        return HttpResponseRedirect(reverse("listing", args=(item_id,)))


@login_required
def commentItem(request):
    if request.method == "POST":
        item_id = request.POST["listing_id"]
        listing = AuctionListing.objects.get(id=item_id)
        comment = Comment(commenterUserId=User(request.user.id),
                          itemId=listing,
                          commentText=request.POST["comment_text"])

        comment.save()
        return HttpResponseRedirect(reverse("listing", args=(item_id,)))


def listing(request, item_id):
    listing = AuctionListing.objects.get(id=item_id)
    comments = Comment.objects.filter(itemId=item_id)
    isOnWatchlist = ItemToWatch.objects.filter(
        user=request.user.id, item=item_id).exists()

    bids = Bid.objects.filter(itemId=item_id).count()
    if bids:
        top_bid = Bid.objects.filter(itemId=item_id).order_by("-bidAmount")[0]
        isWinner = top_bid.bidderUserId.id == request.user.id
    else:
        isWinner=False

    isOwner = listing.listingUserName.id == request.user.id

    commentForm = CommentForm()
    return render(request, "auctions/listing.html", {"listing": listing,
                                                     "comments": comments,
                                                     "isOnWatchlist": isOnWatchlist,
                                                     "isOwner": isOwner,
                                                     "isWinner": isWinner,
                                                     "commentForm": commentForm,
                                                     "bidForm": BidForm(),
                                                     })


def category(request, category_name):
    listings = AuctionListing.objects.filter(
        category=category_name, isClosed=False)
    return render(request, "auctions/category.html", {"category": category_name,
                                                      "listings": listings})


def categories(request):
    listings = AuctionListing.objects.all()
    categories = set()
    for listing in listings:
        categories.add(listing.category)

    return render(request, "auctions/categories.html", {"categories": categories})


def new(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = AuctionListing(
                listingUserName=User(request.user.id),
                title=request.POST["title"],
                description=request.POST["description"],
                currentPrice=request.POST["currentPrice"],
                imageUrl=request.POST["imageUrl"],
                category=request.POST["category"]
            )
            listing.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        # invalid form
        else:
            return render(request, "auctions/new.html", {'form': form})

    form = ListingForm()
    return render(request, "auctions/new.html", {'form': form})
