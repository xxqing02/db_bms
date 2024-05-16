from django.contrib import admin
from . import models

admin.site.register(models.Reader)
admin.site.register(models.Librarian)
admin.site.register(models.Book)
admin.site.register(models.BookCopy)
admin.site.register(models.BorrowRecord)