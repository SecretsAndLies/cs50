from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.core.exceptions import ValidationError
from PIL import Image
from moviepy.editor import VideoFileClip
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    pass

def validate_thumbnail_dimensions(image):
    img = Image.open(image)
    width, height = img.size
    max_width = 1920
    max_height = 1080

    if width > max_width or height > max_height:
        raise ValidationError(f"The image dimensions should be within {max_width}x{max_height} pixels.")

def validate_video_length(instance):
    max_length = 60
    video_path = instance.video.path
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    del clip

    if duration > max_length:
        instance.delete() #delete the object if it fails this validation
        raise ValidationError("The video length should be within {max_length} seconds.")



class Video(models.Model):
    channel = models.ForeignKey(User, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=280)
    thumbnail = models.ImageField(upload_to="videos", validators=[validate_thumbnail_dimensions])
    timestamp = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to="thumbnails")
    def __str__(self) -> str:
        return f"{self.title} - {self.channel.username}"

    def serialize(self):
        return {
            "id": self.id,
            "timePosted":self.timestamp,
            "title":self.title,
            # RATINGS?
        }

# this exists because if the video file isn't saved to disk, then you cant access it.
@receiver(post_save, sender=Video)
def validate_video(sender, instance, **kwargs):
    validate_video_length(instance)

class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments")
    channel = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    commentText = models.CharField(max_length=280)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return f"{self.channel.username} - {self.commentText}"

class Rating(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="ratings")
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    timestamp = models.DateTimeField(auto_now_add=True)

class View(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="views")
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="views")
    timestamp = models.DateTimeField(auto_now_add=True)

class Subscribe(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    subscriptions = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscribers")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.subscriber} subscribes to {self.subscriptions}"

