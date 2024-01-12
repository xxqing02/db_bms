from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.urls import reverse
from datetime import datetime, timedelta
from django.core.mail import send_mail

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
        if search:
            books = models.Book.objects.filter(isbn__icontains=search)| \
                    models.Book.objects.filter(title__icontains=search) | \
                    models.Book.objects.filter(author__icontains=search)
            context['search'] = search
        else:
            books = models.Book.objects.all()

        context['books'] = books
        return render(request, 'reader/book_list.html', context)


class ReaderBookInfo(View):
    def get(self, request, book_id):
        book = models.Book.objects.filter(id=book_id).first()
        copies = models.BookCopy.objects.filter(isbn=book).all()
        context = {
            'copies': copies,
            'book': book,
        }
        return render(request, 'reader/book_info.html', context)

class ReaderBorrow(View):
    @method_decorator(require_POST)
    def post(self, request):
        reader_id = request.session.get('reader_id')
        book_id = request.POST.get('book-id')
        copy_id = request.POST.get('copy-id')
        copy = models.BookCopy.objects.filter(id=copy_id).first()

        active_records = models.BorrowRecord.objects.filter(reader_id=reader_id, return_time=None)
        if active_records.filter(copy_id__isbn__id=book_id).exists():
            return JsonResponse({
                'status': 'error',
                'error': '您已借阅该书籍！',
            })
        elif active_records.filter(due_time__lt=datetime.now()).exists():
            return JsonResponse({
                'status': 'error',
                'error': '您有超时未还的书籍，无法借阅！',
            })
        else:
            models.BorrowRecord.objects.create(
                reader_id=models.Reader.objects.filter(id=reader_id).first(),
                copy_id=models.BookCopy.objects.filter(id=copy_id).first(),
            )
            copy.save()
            return JsonResponse({
                'status': 'success',
                'message': '借阅成功！',
            })
        
# class ReaderReserve(View):
#     @method_decorator(require_POST)
#     def post(self, request):
#         reader_id = request.session.get('reader_id')
#         book_id = request.POST.get('book-id')
#         copy_id = request.POST.get('copy-id')
#         copy = models.BookCopy.objects.filter(id=copy_id).first()

#         active_records = models.ReserveRecord.objects.filter(reader_id=reader_id, return_time=None)
#         if active_records.filter(copy_id__isbn__id=book_id).exists():
#             return JsonResponse({
#                 'status': 'error',
#                 'error': '您已借阅该书籍！',
#             })
#         elif active_records.filter(due_time__lt=datetime.now()).exists():
#             return JsonResponse({
#                 'status': 'error',
#                 'error': '您有超时未还的书籍，无法预约！',
#             })
#         else:
#             start_time = datetime.now()
#             duration = timedelta(seconds=10)
#             due_time = start_time + duration
#             models.ReserveRecord.objects.create(
#                 reader_id=models.Reader.objects.filter(id=reader_id).first(),
#                 copy_id=models.BookCopy.objects.filter(id=copy_id).first(),
#                 start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 due_time=due_time.strftime("%Y-%m-%d %H:%M:%S"),
#             )
#             copy.state = 4
#             copy.save()
#             return JsonResponse({
#                 'status': 'success',
#                 'message': '预约成功！',
#             })

class ReaderReturn(View):
    @method_decorator(require_POST)
    def post(self, request):
        borrow_id = request.POST.get('borrow-id')
        return_time = datetime.now()

        record = models.BorrowRecord.objects.filter(id=borrow_id).first()
        record.return_time = return_time.strftime("%Y-%m-%d %H:%M:%S")

        copy = models.BookCopy.objects.filter(id=record.copy_id.id).first()
        copy.state = 1
        copy.save()

        if return_time.timestamp() > record.due_time.timestamp():
            # 罚金计算公式为：罚金 =（归还时间-应还时间）* fine 元/天,不足一天按一天计算
            fine = 2  # 罚金：元/天
            bill = (return_time.timestamp() - record.due_time.timestamp()) * fine
            print(bill)
            record.bill = bill

        record.save()
        return JsonResponse({
            'status': 'success',
            'message': '归还成功！',
        })

class ReaderReserve(View):
    @method_decorator(require_POST)
    def post(self, request):
        """
        可预约书籍符合:
          1. 已借出
          2. 借阅人不是当前用户
        """
        return JsonResponse({
            'status': 'success',
            'message': '预约成功！',
        })

class ReaderBorrowList(View):
    def get(self, request):
        reader_id = request.session.get('reader_id')
        records = models.BorrowRecord.objects.filter(reader_id=reader_id).all()
        return render(request, 'reader/borrow_list.html', {'borrow_list': records})

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

class LibrarianProcess(View):
    def get(self, request):
        context = {'borrow_list': models.BorrowRecord.objects.all()}
        return render(request, 'librarian/process.html', context)
    
class LibrarianApproveBorrow(View):
    @method_decorator(require_POST)
    def post(self, request):
        borrow_id = request.POST.get('borrow-id')

        start_time = datetime.now()
        duration = timedelta(seconds=10)
        due_time = start_time + duration

        record = models.BorrowRecord.objects.filter(id=borrow_id).first()
        record.start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        record.due_time = due_time.strftime("%Y-%m-%d %H:%M:%S")
        record.is_checked = True
        copy = models.BookCopy.objects.filter(id=record.copy_id.id).first()
        copy.state = 2
        copy.save()
        record.save()
        return JsonResponse({
            'status': 'success',
        })

class LibrarianRefuseBorrow(View):
    @method_decorator(require_POST)
    def post(self, request):
        borrow_id = request.POST.get('borrow-id')
        record = models.BorrowRecord.objects.filter(id=borrow_id).first()
        record.is_checked = True
        record.save()
        return JsonResponse({
            'status': 'success',
        })

# cron function
def print_time():
    print(datetime.now())

def delete_reserve():
    reserve_list = models.ReserveRecord.objects.all()
    for record in reserve_list:
        if record.book_arrive_time:
            # 当前时间晚于最晚领取时间
            if (record.book_arrive_time + timedelta(seconds=record.reserve_days)
                < datetime.now()
            ):
                copy = models.BookCopy.objects.filter(id=record.copy_id.id).first()
                copy.state = "未借出"
                copy.save()
                record.delete()

def expire_notice():
    borrow_list = models.BorrowRecord.objects.all()
    for copy in borrow_list:
        if copy.due_time < datetime.now() and not copy.return_time:
            reader_email = models.Reader.objects.get(id=copy.reader_id.id).email
            send_mail(
                subject="书籍归还提醒",
                message="您好,您借阅的书籍已逾期,请尽快归还并缴纳罚金,谢谢!",
                from_email="gzy500699@163.com",
                recipient_list=[reader_email],
            )