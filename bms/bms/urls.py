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
    # Debug
    re_path(r"^help/", views.help, name="help"),

    # Common
    re_path(r"^$", views.login, name="login"),
    re_path(r"^login/", views.login, name="login"),
    re_path(r"^register/", views.register, name="register"),

    # Reader
    re_path(r"^reader_page/", views.reader_page, name="reader_page"),
    re_path(r"^borrow_book/", views.borrow_book, name="borrow_book"),
    re_path(r"^return_book/", views.return_book, name="return_book"),
    re_path(r"^bill/", views.bill, name="bill"),
    re_path(r"^reserve_book/", views.reserve_book, name="reserve_book"),
    re_path(r"^get_reserve_book/", views.get_reserve_book, name="get_reserve_book"),

    # Librarian
    re_path(r"^librarian_page/", views.librarian_page, name="librarian_page"),
    re_path(r"^book_list/", views.book_list, name="book_list"),
    re_path(r"^book_put_in/", views.put_in, name="book_put_in"),
    re_path(r"^book_add/", views.book_add, name="book_add"),
    re_path(r"^book_info_add/", views.book_info_add, name="book_info_add"),
    re_path(r"^book_process/", views.book_process, name="book_process"),
    re_path(r"^book_edit/", views.book_edit, name="book_edit"),
    re_path(r"^book_del/", views.del_book, name="book_del"),
    re_path(r"^approve_borrow/", views.approve_borrow, name="approve_borrow"),
    re_path(r"^refuse_borrow/", views.refuse_borrow, name="refuse_borrow"),
]
