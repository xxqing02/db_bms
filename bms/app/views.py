from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from app import models
import hashlib
import time

# 可以用session来处理数据传递问题
search_ISBN = ""
states = ["未借出", "已借出", "不外借", "已预约"]


def password_encryption(password):
    hashed_password = hashlib.sha256(password).hexdigest()
    return hashed_password


def help(request):
    return render(request, "help.html")


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


def librarian_page(request):
    return render(request, "librarian_page.html")


def reader_page(request):
    return render(request, "reader_page.html")


def book_list(request):
    book = models.book.objects.all()
    book_info = models.book_info.objects.all()
    list = {"book": book, "book_info": book_info}
    return render(request, "book_list.html", list)


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
            number=0,
            operator=librarian,
        )
        return redirect("/book_info_add/")
    return render(request, "book_add.html")


def book_info_add(request):
    global search_ISBN
    global states
    print(search_ISBN)
    if request.method == "POST" and request.POST:
        librarian_id = request.COOKIES.get("user_id")
        librarian = models.librarian.objects.get(id=librarian_id)
        book_id = request.POST.get("book_id")
        isbn = models.book.objects.get(isbn=search_ISBN)
        position = request.POST.get("position")
        if position == "图书阅览室":
            s = states[2]
        if position == "图书流通室":
            s = states[0]
        operator = request.POST.get("operator")
        models.book_info.objects.create(
            book_id=book_id,
            isbn=isbn,
            position=position,
            state=s,
            operator=librarian,
        )
        isbn.number += 1
        isbn.save()
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


def borrow_book(request):
    books = []
    list = []
    global search_ISBN
    reader_id = request.COOKIES.get("user_id")
    reader = models.reader.objects.filter(id=reader_id).first()
    if request.method == "POST" and request.POST:
        ISBN = request.POST.get("ISBN")
        saved_info = models.book.objects.filter(isbn=ISBN).first()
        # !!!!!!!!!
        if not saved_info:
            search_ISBN = ISBN
            return redirect("/reserve_book/")
        else:
            books = models.book_info.objects.filter(isbn=ISBN).all()
            list = {"books": books}
            return render(request, "borrow_book.html", list)
    if request.method == "GET" and request.GET:
        book_id = request.GET.get("id")
        id = models.book_info.objects.filter(book_id=book_id).first()
        if id:
            print(id)
        else:
            print("error")
        models.borrow.objects.create(
            book_id=id,
            reader_id=reader,
            borrow_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        )
        borrow_record = models.borrow.objects.filter(book_id=book_id).first()
        list = {"books": books, "borrow_record": borrow_record}
        return render(request, "borrow_book.html", list)

    return render(request, "borrow_book.html")


def book_process(request):
    borrow = models.borrow.objects.all()
    return render(request, "book_process.html", {"borrow_list": borrow})


def approve_borrow(request):
    id = request.GET.get("id")
    record = models.borrow.objects.filter(id=id).first()
    record.is_check = True
    record.save()
    book_info = models.book_info.objects.filter(book_id=record.book_id_id).first()
    book_info.state = states[1]
    book_info.save()
    return redirect("/book_process/")


def refuse_borrow(request):
    id = request.GET.get("id")
    record = models.borrow.objects.get(id=id)
    record.delete()
    return redirect("/book_process/")


#############未实现###############
def reserve_book(request):
    global search_ISBN
    if request.method == "POST" and request.POST:
        reader_id = request.COOKIES.get("user_id")
        reader = models.reader.objects.filter(id=reader_id).first()
        book = models.book.objects.filter(isbn=search_ISBN).first()
        day = request.POST.get("day")
        models.reserve.objects.create(
            reader_id=reader,
            isbn=book,
            reserve_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            reserve_days=day,
        )
    return render(request, "reserve_book.html")


def return_book(request):
    return render(request, "return_book.html")
