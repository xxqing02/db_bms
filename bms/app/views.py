from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from app import models
import hashlib

search_ISBN = ""
# 可以用session来处理ISBN传递问题


def password_encryption(password):
    hashed_password = hashlib.sha256(password).hexdigest()
    return hashed_password


# 做读者和管理员界面的区分
def login(request):
    if request.method == "POST" and request.POST:
        account = request.POST.get("id")
        pwd = request.POST.get("password")
        # password = password_encryption(password)
        saved_info = models.librarian.objects.filter(id=account).first()
        if saved_info:
            if pwd == saved_info.password:
                response = HttpResponseRedirect("/librarian_page/")
                response.delete_cookie("username")
                response.set_cookie("user_id", saved_info.id)
                return response

        saved_info = models.reader.objects.filter(id=account).first()
        if saved_info:
            if pwd == saved_info.password:
                response = HttpResponseRedirect("/reader_page/")
                response.delete_cookie("username")
                response.set_cookie("user_id", saved_info.id)
                return response

    return render(request, "login.html")


# 未写
def register(request):
    return render(request, "login.html")


def librarian_page(request):
    return render(request, "librarian_page.html")


def reader_page(request):
    return render(request, "reader_page.html")


def book_list(request):
    book = models.book.objects.all()
    return render(request, "book_list.html", {"book_list": book})


def book_process(request):
    return render(request, "book_process.html")


# 书籍入库
# 根据ISBN号判断是否已经存在该书籍
def put_in(request):
    global search_ISBN
    if request.method == "POST" and request.POST:
        ISBN = request.POST.get("ISBN")
        search_ISBN = ISBN
        saved_info = models.book.objects.filter(isbn=ISBN).first()
        if saved_info:
            return redirect("/book_info_add/")
        else:
            return redirect("/book_add/")
    return render(request, "book_put_in.html")


# ISBN不存在,先添加书目信息
def add_book(request):
    global search_ISBN
    if request.method == "POST" and request.POST:
        librarian_id = request.COOKIES.get("user_id")
        librarian = models.librarian.objects.get(id=librarian_id)
        name = request.POST.get("name")
        author = request.POST.get("author")
        publisher = request.POST.get("publisher")
        date = request.POST.get("date")
        models.book.objects.create(
            name=name,
            author=author,
            publisher=publisher,
            isbn=search_ISBN,
            date=date,
            number=1,
            operator=librarian,
        )
        return redirect("/book_info_add/")
    return render(request, "book_add.html")

def book_info_add(request):
    global search_ISBN
    print(search_ISBN)
    if request.method == "POST" and request.POST:
        librarian_id = request.COOKIES.get("user_id")
        librarian = models.librarian.objects.get(id=librarian_id)
        book_id = request.POST.get("book_id")
        ISBN = models.book.objects.get(isbn=search_ISBN)
        position = request.POST.get("position")
        if position == "图书阅览室":
            s = "不外借"
        if position == "图书流通室":
            s = "未借出"
        operator = request.POST.get("operator")
        models.book_info.objects.create(
            book_id=book_id,
            isbn=ISBN,
            position=position,
            state=s,
            operator=librarian,
        )
        return redirect("/book_list/")

    return render(request, "book_info_add.html")

def del_book(request):
    drop_id = request.GET.get("id")
    drop_object = models.book.objects.get(id=drop_id)
    drop_object.delete()
    return redirect("/book_list/")

def edit_book(request):
    edit_id = request.GET.get("id")
    edit_object = models.book.objects.get(id=edit_id)
    if request.method == "POST":
        edit_object.name = request.POST.get("name")
        edit_object.author = request.POST.get("author")
        edit_object.publisher = request.POST.get("publisher")
        edit_object.ISBN = request.POST.get("ISBN")
        edit_object.date = request.POST.get("date")
        edit_object.number = request.POST.get("num")
        edit_object.operator = request.POST.get("operator")
        edit_object.save()
        return redirect("/book_list/")

    return render(request, "book_edit.html", {"book": edit_object})
