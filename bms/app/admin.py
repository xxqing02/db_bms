from django.contrib import admin
from .models import Reader, Librarian


class ReaderInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'phone', 'email')
    search_fields = ('username', 'phone', 'email')


class LibrarianInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'phone', 'email')
    search_fields = ('username', 'phone', 'email')


admin.site.register(Reader, ReaderInfoAdmin)
admin.site.register(Librarian, LibrarianInfoAdmin)