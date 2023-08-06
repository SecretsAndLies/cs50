from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=280)
    postingUser = models.ForeignKey(User, on_delete=models.CASCADE)
    timePosted = models.DateTimeField(auto_now_add=True)
    hearts = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.content} | hearts: {self.hearts} | user: {self.postingUser} | time: {self.timePosted}"

    def serialize(self):
        return {
            "id": self.id,
            "content":self.content,
            "timePosted":self.timePosted,
            "postingUser":self.postingUser.username,
            "hearts": self.hearts,
        }



class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    user_they_follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_they_follow")

    def __str__(self) -> str:
        return f"{self.user} follows {self.user_they_follow}"
