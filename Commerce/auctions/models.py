from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing')

class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1024)
    start_bid = models.IntegerField()
    image_url = models.CharField(max_length=1024, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class Bid(models.Model):
    amount = models.IntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bid')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)