from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View

from . import models


class EntryView(View):
    def get(self, request):
        return render(request, 'common/login_entry.html')


class BaseLoginView(View):
    user_type = None

    def get(self, request):
        return render(request, f'common/login_{self.user_type}.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            context = {'error': '用户名或密码不能为空！'}
            return render(request, f'common/login_{self.user_type}.html', context)

        context = {'error': '用户名或密码错误！'}
        users = self._filter(username=username)
        if not users.exists():
            # User not found
            return render(request, f'common/login_{self.user_type}.html', context)

        user = users.first()
        if not user.password == password:
            # Password mismatch
            return render(request, f'common/login_{self.user_type}.html', context)

        # Login success
        request.session[f'{self.user_type}_id'] = user.id
        request.session[f'{self.user_type}_name'] = user.username
        return redirect(f'/{self.user_type}/home')
    
    def _filter(self, username):
        if self.user_type == 'reader':
            return models.Reader.objects.filter(username=username)
        elif self.user_type == 'librarian':
            return models.Librarian.objects.filter(username=username)

class ReaderLoginView(BaseLoginView):
    user_type = 'reader'

class LibrarianLoginView(BaseLoginView):
    user_type = 'librarian'


class BaseRegisterView(View):
    user_type = None

    def get(self, request):
        return render(request, f'common/register_{self.user_type}.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        context = {
            'username': username,
            'email': email,
            'phone': phone,
        }

        if not username or not password or not password_confirm:
            context['error'] = '用户名或密码不能为空！'
        elif password != password_confirm:
            context['error'] = '两次输入的密码不一致！'
        elif self._filter(username=username).exists():
            context['error'] = '用户名已存在！'
        elif self._filter(email=email).exists():
            context['error'] = '邮箱已被注册！'
        elif self._filter(phone=phone).exists():
            context['error'] = '手机号已被注册！'

        if context.get('error'):
            return render(request, f'common/register_{self.user_type}.html', context)
        
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        self._create_user(
            username=username,
            password=password,
            email=email,
            phone=phone,
        )
        return redirect(f'/login/{self.user_type}')
    
    def _filter(self, *args, **kwargs):
        if self.user_type == 'reader':
            return models.Reader.objects.filter(*args, **kwargs)
        elif self.user_type == 'librarian':
            return models.Librarian.objects.filter(*args, **kwargs)
    
    def _create_user(self, *args, **kwargs):
        if self.user_type == 'reader':
            models.Reader.objects.create(*args, **kwargs)
        elif self.user_type == 'librarian':
            models.Librarian.objects.create(*args, **kwargs)

class ReaderRegisterView(BaseRegisterView):
    user_type = 'reader'

class LibrarianRegisterView(BaseRegisterView):
    user_type = 'librarian'

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
            books = models.Book.objects.filter(isbn__icontains=search) | \
                    models.Book.objects.filter(title__icontains=search) | \
                    models.Book.objects.filter(author__icontains=search)
            context['search'] = search
        else:
            books = models.Book.objects.all()

        context['books'] = books
        return render(request, 'reader/book_list.html', context)


##################################################################################
# Librarian
##################################################################################

class LibrarianHomeView(View):
    @method_decorator(never_cache)
    def get(self, request):
        return render(request, 'librarian/home.html')


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
