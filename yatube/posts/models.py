from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q, F

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f"{self.title}"


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(verbose_name="date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="posts", blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    date_created = models.DateTimeField(verbose_name="date created", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='user_not_author'
            )
        ]