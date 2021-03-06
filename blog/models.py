

from django.db import models

# Create your models here.
# lets us explicitly set upload path and filename
from django.utils import timezone

from users.models import User


class BlogPost(models.Model):
    id = models.UUIDField(primary_key=True)
    post_title = models.CharField(max_length=255, null=False)
    post_content = models.TextField(null=False)
    post_author = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post_date = models.DateTimeField(default=timezone.now)
    post_type = models.CharField(max_length=55, null=False)
    post_category = models.CharField(max_length=55, null=False)
    post_status = models.CharField(max_length=55, null=False)

    def __str__(self):
        return self.name


class BlogMedia(models.Model):
    ID = models.UUIDField(primary_key=True)
    media_author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False)
    media_name = models.CharField(
        max_length=80, blank=False, null=False)
    media_path = models.TextField()
    media_type = models.CharField(max_length=20)
    media_status = models.CharField(max_length=20)
    media_parent = models.ForeignKey(BlogPost, null=True, on_delete=models.CASCADE)
    media_date = models.DateTimeField(default=timezone.now)
    media_category = models.TextField(max_length=40, null=False)