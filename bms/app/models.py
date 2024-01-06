from django.db import models
from django.contrib.auth.models import AbstractUser


class librarian(models.Model):
    id = models.AutoField(primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=80, null=False)
    password = models.CharField(max_length=80, null=False)
    phone = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=80, unique=True, null=True)

    def __str__(self):
        return self.name


class reader(models.Model):
    id = models.AutoField(primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=80, null=False)
    password = models.CharField(max_length=80, null=False)
    phone = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=80, unique=True, null=True)
    bill = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class book(models.Model):
    id = models.AutoField(primary_key=True, null=False, unique=True)
    name = models.CharField(max_length=20, null=False)
    author = models.CharField(max_length=20, null=False)
    publisher = models.CharField(max_length=20, null=False)
    isbn = models.CharField(max_length=25, unique=True, null=False)
    date = models.CharField(max_length=20, null=False)
    number = models.IntegerField(null=False, default=0)
    operator = models.ForeignKey(librarian, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class book_info(models.Model):
    book_id = models.CharField(primary_key=True, max_length=20, null=False, unique=True)
    isbn = models.ForeignKey(to="book", to_field="isbn", on_delete=models.CASCADE)
    position = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    operator = models.ForeignKey(librarian, on_delete=models.CASCADE)

    def __str__(self):
        return self.book_id


# 借阅表
class borrow(models.Model):
    id = models.AutoField(primary_key=True)
    reader_id = models.ForeignKey(reader, on_delete=models.CASCADE)
    book_id = models.ForeignKey(book_info, on_delete=models.CASCADE)
    # 借阅时间
    borrow_time = models.DateTimeField(default="2000-01-01 00:00:00")
    # 应还时间
    due_time = models.DateTimeField(default="2000-01-01 00:00:00")
    # 归还时间
    return_time = models.DateTimeField(default="2000-01-01 00:00:00")
    # 是否审核
    is_check = models.BooleanField(default=False)
    # 是否归还
    is_return = models.BooleanField(default=False)

    def __str__(self):
        return self.id


# 预约表
class reserve(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    reader_id = models.ForeignKey(reader, on_delete=models.CASCADE)
    book_id = models.ForeignKey(
        book_info, on_delete=models.CASCADE, default=None, null=True
    )
    isbn = models.ForeignKey(to="book", to_field="isbn", on_delete=models.CASCADE)
    reserve_time = models.DateTimeField(default="2000-01-01 00:00:00")
    # 根据书到达时间判断此预约是否有效
    book_arrive_time = models.DateTimeField(default=None, null=True)
    # 预约有效天数 书到了x天内有效 x<=10
    reserve_days = models.IntegerField(default=10)

    def __str__(self):
        return self.id
