from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import Category, Listing, User, Comment, Bid


def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {'listings': listings})

@login_required(login_url='/login')
def create(request):
    if request.method == 'POST':
        listing = Listing.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            image_url=request.POST.get('image_url'),
            category=Category.objects.get(name=request.POST.get('category')),
            start_bid=request.POST.get('start_bid'),
            owner=request.user
        )
        return HttpResponseRedirect(f'/listing/{listing.id}')
    
    return render(request, "auctions/create.html",{'categories': Category.objects.all()})

def categories(request):
    return render(request, "auctions/categories.html", {'categories': Category.objects.all()})

def category(request, name):
    listings = Listing.objects.filter(is_active=True, category__name=name)
    return render(request, "auctions/index.html", {'listings': listings})

def listing(request, id):
    return render(request, "auctions/listing.html", {
        'l': Listing.objects.get(id=id),
        'comments': Comment.objects.filter(listing_id=id),
        'bid': Bid.objects.filter(listing_id=id).order_by('-amount').first(),
        'error': request.GET.get('error')
    })

def watchlist(request):
    return render(request, "auctions/index.html", {'listings': request.user.watchlist.all()})

def toggle_watchlist(request, id):
    listing = Listing.objects.get(id=id)
    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)
    
    return HttpResponseRedirect(f'/listing/{id}')

def close(request, id):
    l = Listing.objects.get(id=id)
    l.is_active = not l.is_active
    l.save()
    return HttpResponseRedirect(f'/listing/{id}')

def set_bid(request, id):
    amount = int(request.GET.get('amount'))
    listing = Listing.objects.get(id=id)
    current_bid = Bid.objects.filter(listing_id=id).order_by('-amount').first()
    if amount <= listing.start_bid or current_bid and amount <= current_bid.amount:
        return HttpResponseRedirect(f'/listing/{id}?error=The bid should be larger than the current price')

    Bid.objects.create(amount=request.GET.get('amount'), owner=request.user, listing_id=id)
    return HttpResponseRedirect(f'/listing/{id}')

def comment(request, id):
    Comment.objects.create(listing=Listing.objects.get(id=id), owner=request.user, content=request.GET.get('content'))
    return HttpResponseRedirect(f'/listing/{id}')

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
