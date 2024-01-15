from django.urls import path
from . import views 

urlpatterns = [
    # Common (entry, login, registeration)
    path('', views.EntryView.as_view(), name='entry'),
    path('entry/', views.EntryView.as_view(), name='entry'),
    path('login/<str:user_type>', views.LoginView.as_view(), name='login'),
    path('register/<str:user_type>', views.RegisterView.as_view(), name='register'),

    # Reader
    path('reader/home', view=views.ReaderHome.as_view(), name='reader_home'),
    path('reader/book_list', view=views.ReaderBookList.as_view(), name='reader_book_list'),
    path('reader/book_info/<int:book_id>', view=views.ReaderBookInfo.as_view(), name='reader_book_info'),
    path('reader/reserve', view=views.ReaderReserve.as_view(), name='reader_reserve'),
    path('reader/borrow_list', view=views.ReaderBorrowList.as_view(), name='reader_borrow_list'),
    path('reader/reserve_list', view=views.ReaderReserveList.as_view(), name='reader_reserve_list'),
    path('reader/cancel_reservation', view=views.ReaderCancelReservation.as_view(), name='reader_cancel_reservation'),

    # Librarian
    path('librarian/home', view=views.LibrarianHome.as_view(), name='librarian_home'),
    path('librarian/book_list', view=views.LibrarianBookList.as_view(), name='librarian_book_list'),
    path('librarian/book_info/<int:book_id>', view=views.LibrarianBookInfo.as_view(), name='librarian_book_info'),
    path('librarian/add_book', view=views.LibrarianAddBook.as_view(), name='librarian_add_book'),
    path('librarian/edit_book', view=views.LibrarianEditBook.as_view(), name='librarian_edit_book'),
    path('librarian/delete_book', view=views.LibrarianDeleteBook.as_view(), name='librarian_delete_book'),
    path('librarian/add_copy', view=views.LibrarianAddCopy.as_view(), name='librarian_add_copy'),
    path('librarian/edit_copy', view=views.LibrarianEditCopy.as_view(), name='librarian_edit_copy'),
    path('librarian/delete_copy', view=views.LibrarianDeleteCopy.as_view(), name='librarian_delete_copy'),
    path('librarian/borrow_list', view=views.LibrarianBorrowList.as_view(), name='librarian_borrow_list'),
    path('librarian/borrow', view=views.LibrarianBorrow.as_view(), name='librarian_borrow'),
    path('librarian/return', view=views.LibrarianReturn.as_view(), name='librarian_return'),
    path('librarian/reserve_list', view=views.LibrarianReserveList.as_view(), name='librarian_reserve_list'),
    path('librarian/take_reserved_book', view=views.LibrarianTakeReservedBook.as_view(), name='librarian_take_reserved_book'),
]