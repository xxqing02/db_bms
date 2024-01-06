from django.db import models
import time


class Reader(models.Model):
    id = models.AutoField(primary_key=True, unique=True, null=False)
    username = models.CharField(verbose_name='用户名', max_length=80, null=False)
    password = models.CharField(max_length=80, null=False)
    phone = models.CharField(verbose_name='手机号', max_length=20, unique=True, null=False)
    email = models.EmailField(verbose_name='邮箱', max_length=80, unique=True, null=False)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'reader'
        verbose_name = '读者'
        verbose_name_plural = verbose_name


class Librarian(models.Model):
    id = models.AutoField(primary_key=True, unique=True, null=False)
    username = models.CharField(max_length=80, null=False)
    password = models.CharField(max_length=80, null=False)
    phone = models.CharField(max_length=20, unique=True, null=True)
    email = models.EmailField(max_length=80, unique=True, null=True)
    bill = models.IntegerField(default=0)

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'librarian'
        verbose_name = '图书管理员'
        verbose_name_plural = verbose_name


class Book(models.Model):
    id = models.AutoField(primary_key=True, null=False, unique=True)
    title = models.CharField(max_length=20, null=False)
    author = models.CharField(max_length=20, null=False)
    publisher = models.CharField(max_length=20, null=False)
    isbn = models.CharField(max_length=25, unique=True, null=False)
    date = models.CharField(max_length=20, null=False)
    number = models.PositiveIntegerField(null=False, default=0)
    operator = models.ForeignKey(Librarian, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    class Meta:
        db_table = 'book'
        verbose_name = '书目'
        verbose_name_plural = verbose_name


class BookInfo(models.Model):
    book_id = models.CharField(primary_key=True, max_length=20, null=False, unique=True)
    isbn = models.ForeignKey(to=Book, to_field="isbn", on_delete=models.CASCADE)
    position = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    operator = models.ForeignKey(Librarian, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.isbn} {self.book_id}"
    
    class Meta:
        db_table = 'book_info'
        verbose_name = '图书信息'
        verbose_name_plural = verbose_name


class Borrow(models.Model):
    id = models.AutoField(primary_key=True)
    reader_id = models.ForeignKey(to=Reader, on_delete=models.CASCADE)
    book_id = models.ForeignKey(to=BookInfo, on_delete=models.CASCADE)
    borrow_time = models.DateTimeField(default="2000-01-01 00:00:00")
    due_time = models.DateTimeField(default="2000-01-01 00:00:00")
    return_time = models.DateTimeField(default="2000-01-01 00:00:00")
    is_check = models.BooleanField(default=False)
    is_return = models.BooleanField(default=False)

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'borrow'
        verbose_name = '借阅记录'
        verbose_name_plural = verbose_name


class Reserve(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    reader_id = models.ForeignKey(to=Reader, to_field=id, on_delete=models.CASCADE)
    book_id = models.ForeignKey(
        BookInfo, on_delete=models.CASCADE, default=None, null=True
    )
    isbn = models.ForeignKey(to=Book, to_field="isbn", on_delete=models.CASCADE)
    reserve_time = models.DateTimeField(null=True, default=time.localtime())
    reserve_days = models.PositiveIntegerField(default=10)
    book_arrive_time = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return f"{self.reader_id} {self.book_id}"
    
    class Meta:
        db_table = 'reserve'
        verbose_name = '预约记录'
        verbose_name_plural = verbose_name
