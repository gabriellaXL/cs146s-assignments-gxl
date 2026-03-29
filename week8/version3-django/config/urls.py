from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect("notes:list"), name="home"),
    path("admin/", admin.site.urls),
    path("notes/", include("notes.urls")),
]
