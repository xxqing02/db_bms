from django.urls import path
from . import views 

urlpatterns = [
    path('', views.EntryView.as_view(), name='entry'),
    path('login/', views.EntryView.as_view(), name='entry'),

    path('login/reader', views.ReaderLoginView.as_view(), name='login_reader'),
    path('login/librarian', views.LibrarianLoginView.as_view(), name='login_librarian'),

    path('register/reader', views.ReaderRegisterView.as_view(), name='register_reader'),
    path('register/librarian', views.LibrarianRegisterView.as_view(), name='register_librarian'),

    path('reader/home', view=views.ReaderHomeView.as_view(), name='reader_home'),
    path('reader/book_list', view=views.ReaderBookListView.as_view(), name='reader_book_list'),
    path('reader/borrow_list', view=views.ReaderBookListView.as_view(), name='reader_borrow_list'),

    path('librarian/home', view=views.LibrarianHomeView.as_view(), name='librarian_home'),
    path('librarian/book_list', view=views.LibrarianBookListView.as_view(), name='librarian_book_list'),
]
