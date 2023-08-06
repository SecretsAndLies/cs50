from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("bid", views.bid, name="bid"),
    path("commentItem", views.commentItem, name="commentItem"),
    path("closeItem", views.closeItem, name="closeItem"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category, name="category"),
    path("item/<int:item_id>", views.listing, name="listing"),
]
