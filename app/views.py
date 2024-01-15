from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.urls import reverse
from datetime import datetime, timedelta

from . import models

##################################################################################
# Common
##################################################################################

class EntryView(View):
    def get(self, request):
        return render(request, 'common/entry.html')


class LoginView(View):
    template_name = 'common/login.html'

    def get(self, request, user_type):
        if user_type not in ['reader', 'librarian']:
            return redirect(reverse('entry'))
        else:
            return render(request, self.template_name, {'user_type': user_type})
    
    def post(self, request, user_type):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({
                'status': 'error',
                'error': '用户名或密码不能为空！'
            })

        users = self._filter(user_type=user_type, username=username)
        if not users.exists():
            # 用户不存在
            return JsonResponse({
                'status': 'error',
                'error': '用户名或密码错误！'
            })

        user = users.first()
        if user.password != password:
            # 密码错误
            return JsonResponse({
                'status': 'error',
                'error': '用户名或密码错误！'
            })

        # Login success
        request.session[f'{user_type}_id'] = user.id
        request.session[f'{user_type}_name'] = user.username

        home_url = f'/{user_type}/home'
        return JsonResponse({
            'status': 'success',
            'message': '登录成功！',
            'redirect': home_url, 
        })
    
    def _filter(self, user_type, *args, **kwargs):
        if user_type == 'reader':
            return models.Reader.objects.filter(*args, **kwargs)
        elif user_type == 'librarian':
            return models.Librarian.objects.filter(*args, **kwargs)
        else:
            raise NotImplementedError


class RegisterView(View):
    def get(self, request, user_type):
        if user_type not in ['reader', 'librarian']:
            return redirect(reverse('entry'))
        else:
            return render(request, 'common/register.html', {'user_type': user_type})
    
    def post(self, request, user_type):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if not username or not password or not password_confirm:
            return JsonResponse({
                'status': 'error',
                'error': '用户名或密码不能为空！'
            })
        elif password != password_confirm:
            return JsonResponse({
                'status': 'error',
                'error': '两次输入的密码不一致！'
            })
        elif self._filter(user_type=user_type, username=username).exists():
            return JsonResponse({
                'status': 'error',
                'error': '用户名已存在！'
            })
        elif self._filter(user_type=user_type, email=email).exists():
            return JsonResponse({
                'status': 'error',
                'error': '邮箱已被注册！'
            })
        elif self._filter(user_type=user_type, phone=phone).exists():
            return JsonResponse({
                'status': 'error',
                'error': '手机号已被注册！'
            })
        else:
            self._create_user(
                user_type=user_type,
                username=username,
                password=password,
                email=email,
                phone=phone,
            )
            return JsonResponse({
                'status': 'success',
                'message': '注册成功！',
                'redirect': f'/login/{user_type}'
            })
    
    def _filter(self, user_type, *args, **kwargs):
        if user_type == 'reader':
            return models.Reader.objects.filter(*args, **kwargs)
        elif user_type == 'librarian':
            return models.Librarian.objects.filter(*args, **kwargs)
        else:
            raise NotImplementedError
    
    def _create_user(self, user_type, *args, **kwargs):
        if user_type == 'reader':
            models.Reader.objects.create(*args, **kwargs)
        elif user_type == 'librarian':
            models.Librarian.objects.create(*args, **kwargs)
        else:
            raise NotImplementedError

##################################################################################
# Reader
##################################################################################

class ReaderHome(View):
    def get(self, request):
        return render(request, 'reader/home.html')
    
class ReaderBookList(View):
    def get(self, request):
        context = dict()
        search = request.GET.get('search')
        books = models.Book.objects.filter(number__gt=0)  # 有库存的书籍
        if search:
            books = books.filter(isbn__icontains=search) | \
                    books.filter(title__icontains=search) | \
                    books.filter(author__icontains=search)
            context['search'] = search

        context['books'] = books
        return render(request, 'reader/book_list.html', context)


class ReaderBookInfo(View):
    def get(self, request, book_id):
        book = models.Book.objects.filter(id=book_id, number__gt=0).first()
        if not book:
            return redirect(reverse('reader_book_list'))

        copies = models.BookCopy.objects.filter(isbn=book).all()
        context = {
            'copies': copies,
            'book': book,
        }
        # 若不存在未借出的书籍，则提供预约功能
        if not copies.filter(state=1).exists():
            context['reserve'] = True
        return render(request, 'reader/book_info.html', context)
        
class ReaderReserve(View):
    @method_decorator(require_POST)
    def post(self, request):
        reader_id = request.session.get('reader_id')
        book_id = request.POST.get('book-id')

        active_borrow_records = models.BorrowRecord.objects.filter(reader_id=reader_id, return_time=None)
        if active_borrow_records.filter(copy_id__isbn__id=book_id).exists():
            return JsonResponse({
                'status': 'error',
                'error': '您已借阅该书目！',
            })

        reserve_records = models.ReserveRecord.objects.filter(reader_id=reader_id).all()
        if reserve_records.filter(isbn__id=book_id).exists():
            return JsonResponse({
                'status': 'error',
                'error': '您已预约该书目！',
            })        

        if active_borrow_records.filter(due_time__lt=datetime.now()).exists():
            return JsonResponse({
                'status': 'error',
                'error': '您有超时未还的书籍，无法预约！',
            })

        if active_borrow_records.count() >= 10:  # 最多借阅10本书
            return JsonResponse({
                'status': 'error',
                'error': '您的借阅书籍数量已达上限！',
            })

        reader = models.Reader.objects.filter(id=reader_id).first()
        if reader.fine > 0.0:
            return JsonResponse({
                'status': 'error',
                'error': '您未支付欠款，无法预约！',
            })

        reserve_time = datetime.now()
        models.ReserveRecord.objects.create(
            reader_id=reader,
            isbn=models.Book.objects.filter(id=book_id).first(),
            reserve_time=reserve_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        return JsonResponse({
            'status': 'success',
            'message': '预约成功！',
        })

class ReaderBorrowList(View):
    def get(self, request):
        reader_id = request.session.get('reader_id')
        records = models.BorrowRecord.objects.filter(reader_id=reader_id).all()
        active_records = records.filter(return_time__isnull=True)
        history_records = records.filter(return_time__isnull=False)
        context = {
            'active_records': active_records,
            'history_records': history_records,
        }
        return render(request, 'reader/borrow_list.html', context)

class ReaderReserveList(View):
    def get(self, request):
        reader_id = request.session.get('reader_id')
        records = models.ReserveRecord.objects.filter(reader_id=reader_id).all()
        context = {
            'reserve_records': records,
        }
        return render(request, 'reader/reserve_list.html', context)

class ReaderCancelReservation(View):
    @method_decorator(require_POST)
    def post(self, request):
        reserve_id = request.POST.get('reserve-id')
        reserve_record = models.ReserveRecord.objects.filter(id=reserve_id)
        reserve_record.delete()

        return JsonResponse({
            'status': 'success',
            'message': '已取消预约！',
        })

##################################################################################
# Librarian
##################################################################################

class LibrarianHome(View):
    def get(self, request):
        return render(request, 'librarian/home.html')

class LibrarianBookInfo(View):
    def get(self, request, book_id):
        book = models.Book.objects.filter(id=book_id).first()
        copies = models.BookCopy.objects.filter(isbn=book).all()
        context = {
            'copies': copies,
            'book': book,
        }

        return render(request, 'librarian/book_info.html', context)

class LibrarianBookList(View):
    def get(self, request):
        context = dict()
        search = request.GET.get('search')
        if search:
            books = models.Book.objects.filter(isbn__icontains=search) | \
                    models.Book.objects.filter(title__icontains=search) | \
                    models.Book.objects.filter(author__icontains=search)
            context['search'] = search
        else:
            books = models.Book.objects.all()

        context['books'] = books
        return render(request, 'librarian/book_list.html', context)

class LibrarianAddBook(View):
    @method_decorator(require_POST)
    def post(self, request):
        title = request.POST.get('title').strip()
        author = request.POST.get('author').strip()
        publisher = request.POST.get('publisher').strip()
        isbn = request.POST.get('isbn').strip()
        date = request.POST.get('date').strip()
        number = 0
        operator_id = request.session.get('librarian_id')

        if not title or not author or not publisher or not isbn or not date:
            return JsonResponse({
                'status': 'error', 
                'error': '信息不能为空！'
            })
        elif models.Book.objects.filter(isbn=isbn).exists():
            return JsonResponse({
                'status': 'error', 
                'error': 'ISBN已存在！'
            })
        else:
            models.Book.objects.create(
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                date=date,
                number=number,
                operator_id=operator_id,
            )
        return JsonResponse({
            'status': 'success',
            'message': '添加成功！',
        })

class LibrarianEditBook(View):
    @method_decorator(require_POST)
    def post(self, request):
        book_id = request.POST.get('edit-book-id')
        title = request.POST.get('title').strip()
        author = request.POST.get('author').strip()
        publisher = request.POST.get('publisher').strip()
        isbn = request.POST.get('isbn').strip()
        date = request.POST.get('date').strip()
        operator_id = request.session.get('librarian_id')

        if not title or not author or not publisher or not isbn or not date:
            return JsonResponse({
                'status': 'error', 
                'error': '信息不能为空！'
            })
        elif models.Book.objects.filter(isbn=isbn).exclude(id=book_id).exists():
            return JsonResponse({
                'status': 'error', 
                'error': 'ISBN已存在！'
            })
        else:
            models.Book.objects.filter(id=book_id).update(
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                date=date,
                operator_id=operator_id,
            )
            return JsonResponse({
                'status': 'success',
                'message': '修改成功！',
            })

class LibrarianDeleteBook(View):
    @method_decorator(require_POST)
    def post(self, request):
        delete_book_id = request.POST.get('delete-book-id')
        models.Book.objects.filter(id=delete_book_id).delete()
        return JsonResponse({
            'status': 'success',
            'message': '删除成功！',
        })

class LibrarianAddCopy(View):
    @method_decorator(require_POST)
    def post(self, request):
        book_id = request.POST.get('book-id')
        copyNO = request.POST.get('copy-no')
        position = request.POST.get('position')

        if not copyNO or not position:
            return JsonResponse({
                'status': 'error',
                'error': '信息不能为空！',
            })
        elif models.BookCopy.objects.filter(copyNO=copyNO).exists():
            return JsonResponse({
                'status': 'error', 
                'error': '书册编号已存在！'
            })
        else:
            if position == '1':  # 图书流通室
                state = '1'  # 未借出
            elif position == '2':  # 图书阅览室
                state = '3'  # 不外借

            book = models.Book.objects.filter(id=book_id).first()
            models.BookCopy.objects.create(
                isbn=book,
                copyNO=copyNO,
                position=position,
                state=state,
                operator_id=request.session.get('librarian_id'),
            )
            book.number += 1
            book.save()
            return JsonResponse({
                'status': 'success',
                'message': '添加成功！',
            })

class LibrarianBorrow(View):
    @method_decorator(require_POST)
    def post(self, request):
        reader_name = request.POST.get('reader')
        reader = models.Reader.objects.filter(username=reader_name).first()
        if not reader:
            return JsonResponse({
                'status': 'error',
                'error': '读者不存在！',
            })
        reader_id = reader.id

        book_id = request.POST.get('book-id')
        copy_id = request.POST.get('copy-id')
        copy = models.BookCopy.objects.filter(id=copy_id).first()

        # if not copy:
        #     return JsonResponse({
        #         'status': 'error',
        #         'error': '该书册不存在，请刷新页面！',
        #     })

        # if copy.state != '1':
        #     return JsonResponse({
        #         'status': 'error',
        #         'error': '该书册不可借，请刷新页面！',
        #     })

        active_records = models.BorrowRecord.objects.filter(reader_id=reader_id, return_time=None)
        if active_records.filter(copy_id__isbn__id=book_id).exists():
            return JsonResponse({
                'status': 'error',
                'error': '该读者已借阅该书目！',
            })

        if active_records.filter(due_time__lt=datetime.now()).exists():
            return JsonResponse({
                'status': 'error',
                'error': '该读者有超时未还的书籍，无法借阅！',
            })

        if active_records.count() >= 10:  # 最多借阅10本书
            return JsonResponse({
                'status': 'error',
                'error': '该读者借阅书籍数量已达上限！',
            })

        if reader.fine > 0.0:
            return JsonResponse({
                'status': 'error',
                'error': '该读者未支付欠款，无法借阅！',
            })

        start_time = datetime.now()
        duration = timedelta(minutes=1)
        due_time = start_time + duration

        models.BorrowRecord.objects.create(
            reader_id=models.Reader.objects.filter(id=reader_id).first(),
            copy_id=models.BookCopy.objects.filter(id=copy_id).first(),
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            due_time=due_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        copy = models.BookCopy.objects.filter(id=copy_id).first()
        copy.state = 2
        copy.save()
        return JsonResponse({
            'status': 'success',
            'message': '借阅成功！',
        })

class LibrarianEditCopy(View):
    @method_decorator(require_POST)
    def post(self, request):
        copy_id = request.POST.get('copy-id')
        copy = models.BookCopy.objects.filter(id=copy_id).first()
        copy.copyNO = request.POST.get('copy-no')
        copy.position = request.POST.get('position')

        if not copy.copyNO or not copy.position:
            return JsonResponse({
                'status': 'error',
                'error': '信息不能为空！',
            })
        elif models.BookCopy.objects.filter(copyNO=copy.copyNO).exclude(id=copy_id).exists():
            return JsonResponse({
                'status': 'error', 
                'error': '书册编号已存在！'
            })
        else:
            if copy.position == '1':  # 图书流通室
                copy.state = '1'  # 未借出
            elif copy.position == '2':  # 图书阅览室
                copy.state = '3'  # 不外借
            copy.operator_id = request.session.get('librarian_id')
            copy.save()
            return JsonResponse({
                'status': 'success',
                'message': '修改成功！',
            })

class LibrarianDeleteCopy(View):
    @method_decorator(require_POST)
    def post(self, request):
        book_id = request.POST.get('book-id')
        copy_id = request.POST.get('copy-id')
        book = models.Book.objects.filter(id=book_id).first()
        book.number -= 1
        book.save()
        models.BookCopy.objects.filter(id=copy_id).delete()
        return JsonResponse({
            'status': 'success',
            'message': '删除成功！',
        })

class LibrarianBorrowList(View):
    def get(self, request):
        records = models.BorrowRecord.objects.all()
        active_records = records.filter(return_time__isnull=True)
        history_records = records.filter(return_time__isnull=False)
        context = {
            'active_records': active_records,
            'history_records': history_records,
        }
        return render(request, 'librarian/borrow_list.html', context)

class LibrarianReturn(View):
    @method_decorator(require_POST)
    def post(self, request):
        borrow_id = request.POST.get('borrow-id')
        return_time = datetime.now()

        record = models.BorrowRecord.objects.filter(id=borrow_id).first()
        record.return_time = return_time.strftime("%Y-%m-%d %H:%M:%S")

        copy = models.BookCopy.objects.filter(id=record.copy_id.id).first()
        # 查询是否有其他用户预约该书目
        book = copy.isbn
        reserve_records = models.ReserveRecord.objects.filter(isbn=book, copy_id=None)
        if reserve_records:
            # 修改图书状态，系统同时自动查询其他读者预约该书的记录，
            # 将该图书的状态修改为“已预约”，并写入相应的预约记录。
            copy.state = 4  # 已预约
            reserve_record = reserve_records.first()
            reserve_record.copy_id = copy
            reserve_record.arrive_time = datetime.now()
            reserve_record.save()

            reader_email = reserve_record.reader_id.email
            send_mail(
                subject="预约书籍可借通知",
                message="您好，您预约的书籍现在可以借阅了，请在10日内完成借阅手续，否则预约无效。",
                from_email="gzy500699@163.com",
                recipient_list=[reader_email],
            )
            print("sent")
        else:
            copy.state = 1  # 未借出
        copy.save()

        if return_time.timestamp() > record.due_time.timestamp():
            # 罚金计算公式为：罚金 =（归还时间-应还时间）* 单价，不足一天按一天计算
            price_per_day = 2
            fine = (return_time.minute - record.due_time.minute) * price_per_day
            record.fine = fine
            reader = record.reader_id
            reader.fine += fine
            reader.save()
        record.save()

        return JsonResponse({
            'status': 'success',
            'message': '归还成功！',
        })
    
class LibrarianReserveList(View):
    def get(self, request):
        records = models.ReserveRecord.objects.all()
        context = {
            'reserve_records': records,
        }
        return render(request, 'librarian/reserve_list.html', context)
    
class LibrarianTakeReservedBook(View):
    @method_decorator(require_POST)
    def post(self, request):
        reserve_id = request.POST.get('reserve-id')

        record = models.ReserveRecord.objects.filter(id=reserve_id).first()
        reader = record.reader_id
        if reader.fine > 0.0:
            return JsonResponse({
                'status': 'error',
                'error': '该读者未支付欠款，无法领取！',
            })

        start_time = datetime.now()
        duration = timedelta(minutes=1)
        due_time = start_time + duration

        models.BorrowRecord.objects.create(
            reader_id=record.reader_id,
            copy_id=record.copy_id,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            due_time=due_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        copy = models.BookCopy.objects.filter(id=record.copy_id.id).first()
        copy.state = 2  # 已借出
        copy.save()

        record.delete()

        return JsonResponse({
            'status': 'success',
            'message': '已领取！',
        })