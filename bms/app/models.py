from django.db import models


# Create your models here.
class librarian(models.Model):
    id = models.AutoField(primary_key=True, unique=True, default=1000)
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class reader(models.Model):
    id = models.AutoField(primary_key=True, unique=True, default=2000)
    name = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class book(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=20)
    author = models.CharField(max_length=20)
    publisher = models.CharField(max_length=20)
    isbn = models.CharField(max_length=25, unique=True)
    date = models.CharField(max_length=20)
    number = models.IntegerField(default=0)
    operator = models.ForeignKey(librarian, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class book_info(models.Model):
    book_id = models.CharField(max_length=20, primary_key=True, unique=True)
    isbn = models.ForeignKey(to="book",to_field="isbn", on_delete=models.CASCADE)
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
    # 是否应该修改?如果使用外键,则要求需要预约的书籍必须存在,否则会报错
    isbn = models.ForeignKey(book, to_field="isbn", on_delete=models.CASCADE)
    reserve_time = models.DateTimeField(default="2000-01-01 00:00:00")

    def __str__(self):
        return self.id
