from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from app import models
from django.core.mail import send_mail
import hashlib
import time


COMMON_PATH = "./common/"
READER_PATH = "./reader/"
LIBRARIAN_PATH = "./librarian/"

# 可以用session来处理数据传递问题
search_ISBN = ""
states = ["未借出", "已借出", "不外借", "已预约"]
book_position = ["图书流通室", "图书阅览室"]


def password_encryption(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


#####################################################
# Common
#####################################################


def help(request):
    return render(request, "help.html")


def login(request):
    if request.method == "POST" and request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_encrypted = password_encryption(password)
        # password_encrypted = password

        user_found = models.reader.objects.filter(email=email).first()
        if user_found:
            if password_encrypted == user_found.password:
                response = HttpResponseRedirect("/reader_page/")
                response.set_cookie("user_id", user_found.id)
                response.set_cookie("username", user_found.name)
                return response

        user_found = models.librarian.objects.filter(email=email).first()
        if user_found:
            if password_encrypted == user_found.password:
                response = HttpResponseRedirect("/librarian_page/")
                response.set_cookie("user_id", user_found.id)
                response.set_cookie("username", user_found.name)
                return response

    return render(request, f"{COMMON_PATH}login.html")


def register(request):
    if request.method == "POST" and request.POST:
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        identity = request.POST.get("identity")
        password_encrypted = password_encryption(password)

        if identity == "reader":
            objects = models.reader.objects
        elif identity == "librarian":
            objects = models.librarian.objects

        user_found = objects.filter(email=email).first()
        if user_found:
            return render(request, f"{COMMON_PATH}register.html", {"error": "该邮箱已被注册！"})
        else:
            objects.create(
                name=name,
                phone=phone,
                email=email,
                password=password_encrypted,
            )
            return HttpResponseRedirect("/login/")

    return render(request, f"{COMMON_PATH}register.html")


#####################################################
# Librarian
#####################################################


def librarian_page(request):
    return render(request, f"{LIBRARIAN_PATH}librarian_page.html")


def book_list(request):
    book = models.book.objects.all()
    book_info = models.book_info.objects.all()
    list = {"book": book, "book_info": book_info}
    return render(request, f"{LIBRARIAN_PATH}book_list.html", list)


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
    return render(request, f"{LIBRARIAN_PATH}book_put_in.html")


def book_add(request):
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
    return render(request, f"{LIBRARIAN_PATH}book_add.html")


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
        if position == book_position[0]:
            s = states[0]
        if position == book_position[1]:
            s = states[2]
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
    return render(request, f"{LIBRARIAN_PATH}book_info_add.html")


def del_book(request):
    drop_id = request.GET.get("id")
    drop_object = models.book.objects.get(id=drop_id)
    drop_object.delete()
    return redirect("/book_list/")


def book_edit(request):
    edit_id = request.GET.get("id")
    edit_object = models.book.objects.get(id=edit_id)
    if request.method == "POST":
        edit_object.name = request.POST.get("name")
        edit_object.author = request.POST.get("author")
        edit_object.publisher = request.POST.get("publisher")
        edit_object.isbn = request.POST.get("ISBN")
        edit_object.date = request.POST.get("date")
        edit_object.number = request.POST.get("number")
        edit_object.save()
        return redirect("/book_list/")
    return render(request, f"{LIBRARIAN_PATH}book_edit.html", {"book": edit_object})


def book_process(request):
    borrow = models.borrow.objects.all()
    return render(
        request, f"{LIBRARIAN_PATH}book_process.html", {"borrow_list": borrow}
    )


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


#####################################################
# Reader
#####################################################


def reader_page(request):
    return render(request, f"{READER_PATH}reader_page.html")


def borrow_book(request):
    books = []
    list = []
    global search_ISBN
    reader_id = request.COOKIES.get("user_id")
    reader = models.reader.objects.filter(id=reader_id).first()
    if request.method == "POST" and request.POST:
        ISBN = request.POST.get("ISBN")
        saved_info = models.book.objects.filter(isbn=ISBN).first()
        if not saved_info:
            return render(
                request, f"{READER_PATH}borrow_book.html", {"error": "本书未入库！"}
            )  # 不可以预约没有入库的书籍
        else:
            # 可借书籍应该符合: 1.position=图书流通室 2.未借出
            # 将图书流通室的书籍加入列表,可借显示借阅,不可借显示预约
            books = models.book_info.objects.filter(
                isbn=ISBN, position=book_position[0]
            ).all()
            # 自己借阅过的书不显示在列表中
            for book in books:
                if models.borrow.objects.filter(
                    book_id=book.book_id, reader_id=reader_id
                ).first():
                    books = books.exclude(book_id=book.book_id)
            list = {"books": books}
            return render(request, f"{READER_PATH}borrow_book.html", list)

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
            due_time=time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 15 * 24 * 60 * 60)
            ),
        )
        borrow_record = models.borrow.objects.filter(book_id=book_id).first()
        list = {"books": books, "borrow_record": borrow_record}
        return render(request, f"{READER_PATH}borrow_book.html", list)

    return render(request, f"{READER_PATH}borrow_book.html")


def reserve_book(request):
    if request.method == "GET" and request.GET:
        reader_id = request.COOKIES.get("user_id")
        reader = models.reader.objects.filter(id=reader_id).first()
        book_id = request.GET.get("id")
        book_info = models.book_info.objects.filter(book_id=book_id).first()
        ISBN = models.book.objects.filter(isbn=book_info.isbn_id).first()
        models.reserve.objects.create(
            reader_id=reader,
            isbn=ISBN,
            reserve_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            reserve_days=10,
        )
    return render(request, f"{READER_PATH}borrow_book.html")


def return_book(request):
    # 展示还书列表
    reader_id = request.COOKIES.get("user_id")
    reader = models.reader.objects.filter(id=reader_id).first()
    borrow_record = models.borrow.objects.filter(reader_id=reader_id).all()
    list = {"borrow_record": borrow_record}
    # 处理还书业务
    if request.method == "GET" and request.GET:
        id = request.GET.get("id")
        record = models.borrow.objects.filter(id=id).first()
        return_time = time.localtime()
        record.return_time = time.strftime("%Y-%m-%d %H:%M:%S", return_time)
        record.is_return = True
        record.save()
        # 罚金计算公式为：罚金=（归还时间-应还时间）* fine 元/天,不足一天按一天计算
        now = time.time()
        due_time = record.due_time.timestamp()
        fine = 2  # 罚金/天
        if now > due_time:
            bill = (now - due_time) / (24 * 60 * 60) * fine
            reader.bill += bill
            reader.save()
        # 修改图书状态,系统同时自动查询预约reserve(ISBN)其他读者预约该书(book_id)的记录，
        # 则将该图书的状态修改为“已预约”，并将该图书ID写入相应的预约记录中
        # 系统在清除超出预约期限的记录时解除该图书的“已预约”状态；否则，将该图书的状态修改为“未借出”。
        # 根据id找到borrow表中的book_id,根据book_id找到book_info表中的isbn,根据isbn找到reserve表
        book_info = models.book_info.objects.filter(book_id=record.book_id).first()
        # 保证reserve的isbn不同,这要求被预约的书不能重复预约
        reserve_book = models.reserve.objects.filter(isbn=book_info.isbn).first()
        if reserve_book:
            reserve_book.book_id = book_info
            reserve_book.book_arrive_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", return_time
            )
            reserve_book.save()
            book_info.state = states[3]
            book_info.save()

            reader_id = int(reserve_book.reader_id.id)
            reservation = models.reader.objects.filter(id=reader_id).first()
            send_mail(
                subject="预约书籍可借通知",
                message="您好,您预约的书籍现在可以借阅了,请在10日内完成借阅手续,否则预约无效.",
                from_email="gzy500699@163.com",
                recipient_list=[reservation.email],
            )
        else:
            book_info.state = states[0]
            book_info.save()

        return redirect("/reader_page/")
    return render(request, f"{READER_PATH}return_book.html", list)


def get_reserve_book(request):
    # 读者取书,问题是book_info里的经办人不知道是谁
    reader_id = request.COOKIES.get("user_id")
    reader = models.reader.objects.filter(id=reader_id).first()
    reserve_book = models.reserve.objects.filter(reader_id=reader_id).all()
    if request.method == "GET":
        for book in reserve_book:
            if book.book_arrive_time:
                book_info = models.book_info.objects.filter(
                    book_id=book.book_id
                ).first()
                book_info.state = states[1]
                book_info.save()
                models.borrow.objects.create(
                    book_id=book_info,
                    reader_id=reader,
                    borrow_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    due_time=time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(time.time() + 15 * 24 * 60 * 60),
                    ),
                )
                book.delete()

    return render(
        request, f"{READER_PATH}get_reserve_book.html", {"reserve_record": reserve_book}
    )


def bill(request):
    reader_id = request.COOKIES.get("user_id")
    reader = models.reader.objects.filter(id=reader_id).first()
    list = {"reader": reader}
    return render(request, f"{READER_PATH}bill.html", list)
