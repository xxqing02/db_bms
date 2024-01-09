from django.urls import path
from . import views 

urlpatterns = [
    path('', views.EntryView.as_view(), name='entry'),
    path('entry/', views.EntryView.as_view(), name='entry'),
    path('login/<str:user_type>', views.LoginView.as_view(), name='login'),
    path('register/<str:user_type>', views.RegisterView.as_view(), name='register'),

    path('reader/home', view=views.ReaderHomeView.as_view(), name='reader_home'),
    path('reader/book_list', view=views.ReaderBookListView.as_view(), name='reader_book_list'),
    path('reader/borrow/<int:book_id>', view=views.ReaderBorrowView.as_view(), name='reader_borrow'),
    path('reader/borrow_list', view=views.ReaderBorrowListView.as_view(), name='reader_borrow_list'),

    path('librarian/home', view=views.LibrarianHomeView.as_view(), name='librarian_home'),
    path('librarian/book_list', view=views.LibrarianBookListView.as_view(), name='librarian_book_list'),
    path('librarian/edit/<int:book_id>', view=views.LibrarianBookEditView.as_view(), name='librarian_edit'),
]
