from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create),
    path("categories", views.categories),
    path("watchlist", views.watchlist),
    path("watchlist/<str:id>", views.toggle_watchlist),
    path("category/<str:name>", views.category),
    path("listing/<int:id>", views.listing),
    path("set_bid/<int:id>", views.set_bid),
    path("comment/<int:id>", views.comment),
    path("close/<int:id>", views.close)
]
