"""bms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import app.views as views
from django.urls import re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^login/", views.login, name="login"),
    re_path(r"^register/", views.register, name="register"),
    re_path(r"^reader_page/", views.reader_page, name="reader_page"),
    re_path(r"^librarian_page/", views.librarian_page, name="librarian_page"),
    re_path(r"^book_put_in/", views.put_in, name="book_put_in"),
    re_path(r"^book_list/", views.book_list, name="book_list"),
    re_path(r"^book_add/", views.add_book, name="book_add"),
    re_path(r"^book_process/", views.book_process, name="book_process"),
    re_path(r"^book_info_add/", views.book_info_add, name="book_info_add"),
    re_path(r"^book_edit/", views.edit_book, name="book_edit"),
    re_path(r"^book_del/", views.del_book, name="book_del"),
]
