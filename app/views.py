from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View

from . import models

##################################################################################
# Common
##################################################################################

class EntryView(View):
    def get(self, request):
        return render(request, 'common/entry.html')


class LoginView(View):
    def get(self, request, user_type):
        context = {
            'user_type': user_type
        }
        return render(request, 'common/login.html', context)
    
    def post(self, request, user_type):
        username = request.POST.get('username')
        password = request.POST.get('password')

        context = {
            'user_type': user_type
        }
        users = self._filter(user_type=user_type, username=username)
        if not users.exists():
            # User not found
            context['error'] = '用户名或密码错误！'
            return render(request, 'common/login.html', context)

        user = users.first()
        if user.password != password:
            # Password mismatch
            context['error'] = '用户名或密码错误！'
            return render(request, 'common/login.html', context)

        # Login success
        request.session[f'{user_type}_id'] = user.id
        request.session[f'{user_type}_name'] = user.username
        return redirect(f'/{user_type}/home')
    
    def _filter(self, user_type, *args, **kwargs):
        if user_type == 'reader':
            return models.Reader.objects.filter(*args, **kwargs)
        elif user_type == 'librarian':
            return models.Librarian.objects.filter(*args, **kwargs)
        else:
            raise NotImplementedError


class RegisterView(View):
    def get(self, request, user_type):
        context = {'user_type': user_type}
        return render(request, 'common/register.html', context)
    
    def post(self, request, user_type):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        context = {
            'user_type': user_type,
            'username': username,
            'email': email,
            'phone': phone,
        }
        if not username or not password or not password_confirm:
            context['error'] = '用户名或密码不能为空！'
        elif password != password_confirm:
            context['error'] = '两次输入的密码不一致！'
        elif self._filter(user_type=user_type, username=username).exists():
            context['error'] = '用户名已存在！'
        elif self._filter(user_type=user_type, email=email).exists():
            context['error'] = '邮箱已被注册！'
        elif self._filter(user_type=user_type, phone=phone).exists():
            context['error'] = '手机号已被注册！'

        if context.get('error'):
            return render(request, 'common/register.html', context)
        
        # Register success
        self._create_user(
            user_type=user_type,
            username=username,
            password=password,
            email=email,
            phone=phone,
        )
        return redirect(f'/login/{user_type}')
    
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

class ReaderHomeView(View):
    @method_decorator(never_cache)
    def get(self, request):
        return render(request, 'reader/home.html')
    
class ReaderBookListView(View):
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


class ReaderBorrowView(View):
    def get(self, request, book_id):
        book = models.Book.objects.filter(id=book_id).first()
        copies = models.BookCopy.objects.filter(isbn=book).all()
        context = {
            'copies': copies,
            'book': book,
        }

        # 可借书籍应该符合:
        # 1.position=图书流通室
        # 2.未借出
        return render(request, 'reader/borrow.html', context)

#             # 将图书流通室的书籍加入列表,可借显示借阅,不可借显示预约
#             books = models.book_info.objects.filter(
#                 isbn=ISBN, position=book_position[0]
#             ).all()



#         now_time = datetime.now()
#         after_time =  (now_time + timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
#         now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         models.borrow.objects.create(
#             book_id=id,
#             reader_id=reader,
#             borrow_time=now_time,
#             due_time=after_time,
#         )
#         borrow_record = models.borrow.objects.filter(book_id=book_id).first()
#         list = {"books": books, "borrow_record": borrow_record}
#         return render(request, f"{READER_PATH}borrow_book.html", list)

#     return render(request, f"{READER_PATH}borrow_book.html")     


class ReaderBorrowListView(View):
    def get(self, request):
        return render(request, 'reader/borrow_list.html')


##################################################################################
# Librarian
##################################################################################

class LibrarianHomeView(View):
    @method_decorator(never_cache)
    def get(self, request):
        return render(request, 'librarian/home.html')

class LibrarianBookEditView(View):
    def get(self, request, book_id):
        book = models.Book.objects.filter(id=book_id).first()
        copies = models.BookCopy.objects.filter(isbn=book).all()
        context = {
            'copies': copies,
            'book': book,
        }

        # 可借书籍应该符合:
        # 1.position=图书流通室
        # 2.未借出
        return render(request, 'librarian/edit.html', context)

class LibrarianBookListView(View):
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
