from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    listingUserName = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=280)
    currentPrice = models.PositiveIntegerField()
    imageUrl = models.URLField(
        default="https://static.vecteezy.com/system/resources/previews/005/720/408/original/crossed-image-icon-picture-not-available-delete-picture-symbol-free-vector.jpg")
    category = models.CharField(max_length=80)
    isClosed = models.BooleanField(default=False)
    timeCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} : {self.title}"


class ItemToWatch(models.Model):
    item = models.ForeignKey(
        AuctionListing, blank=True, related_name="watched", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Item: {self.item.title} User: {self.user.username}"


class Bid(models.Model):
    itemId = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bidderUserId = models.ForeignKey(User, on_delete=models.CASCADE)
    bidTime = models.DateTimeField(auto_now_add=True)
    bidAmount = models.PositiveIntegerField()

    def __str__(self):
        return f"Bid: {self.bidAmount} Item: {self.itemId.title}  User: {self.bidderUserId.username}"


class Comment(models.Model):
    commenterUserId = models.ForeignKey(User, on_delete=models.CASCADE)
    itemId = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    commentText = models.CharField(max_length=280)
    commentTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.commenterUserId.username} item: {self.itemId.title} comment: {self.commentText}"
