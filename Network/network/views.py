from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Follow
from .forms import AddForm
import json

def index(request):
    is_profile = is_follow = target_user = follower_count = following_count = None
    post = Post.objects.order_by('-created_at')
    if request.GET.get('user'):
        is_profile = True
        target_user = User.objects.get(username=request.GET.get('user'))
        post = Post.objects.filter(user__username=request.GET.get('user')).order_by('-created_at')
        follower_count = Follow.objects.filter(follower=target_user).count()
        following_count = Follow.objects.filter(user=target_user).count()
        if request.user.is_authenticated:
            is_follow = Follow.objects.filter(user=request.user, follower=target_user).exists()
    elif request.GET.get('type') == 'following':
        following = Follow.objects.filter(user=request.user)
        post = Post.objects.filter(user__in=[i.follower for i in following]).order_by('-created_at')
    return render(request, "network/index.html", { 
        "form": AddForm(),
        "target_user": request.GET.get('user'),
        "is_profile": is_profile,
        "is_follow": is_follow,
        "follower_count": follower_count,
        "following_count": following_count,
        "page_obj": Paginator(post, 10).get_page(request.GET.get('page'))
    })

@csrf_exempt
@login_required(login_url='/login')
def add_post(request):
    post_id = request.POST.get('post_id')
    form = AddForm(request.POST)
    form.is_valid()
    if post_id:
        post = Post.objects.get(id=post_id)
        post.content = form.cleaned_data['new_post']
        post.save()
        return HttpResponse(form.cleaned_data['new_post'])
    else:
        Post.objects.create(content=form.cleaned_data['new_post'], user=request.user)
        return redirect("/")

def like(request):
    user = request.user
    post = Post.objects.get(id=request.GET.get('post_id'))

    if user in post.likes.all():
        post.likes.remove(user)
        return HttpResponse(json.dumps({'count':len(post.likes.all()), 'is_like': False}))
    else:
        post.likes.add(user)
        return HttpResponse(json.dumps({'count':len(post.likes.all()), 'is_like': True}))

def follow(request):
    target_user = User.objects.get(username=request.GET.get('user'))
    q = Follow.objects.filter(user=request.user, follower=target_user)
    if q.exists():
        q.delete()
    else:
        Follow.objects.create(user=request.user, follower=target_user)
    return redirect(request.META.get('HTTP_REFERER'))

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
