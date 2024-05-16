from django.db import models
import time


class Reader(models.Model):
    id = models.AutoField(verbose_name='读者编号', primary_key=True, unique=True)
    username = models.CharField(verbose_name='用户名', unique=True, max_length=80)
    password = models.CharField(verbose_name='密码', max_length=80)
    phone = models.CharField(verbose_name='手机号', unique=True, max_length=20)
    email = models.EmailField(verbose_name='邮箱', unique=True, max_length=80)
    fine = models.FloatField(verbose_name='罚金', default=0)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'readers'
        verbose_name = '读者'
        verbose_name_plural = verbose_name


class Librarian(models.Model):
    id = models.AutoField(verbose_name='图书管理员编号', primary_key=True, unique=True)
    username = models.CharField(verbose_name='用户名', unique=True, max_length=80)
    password = models.CharField(verbose_name='用户密码', max_length=80)
    phone = models.CharField(verbose_name='手机号', unique=True, null=True, max_length=20)
    email = models.EmailField(verbose_name='邮箱', unique=True, null=True, max_length=80)

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'librarians'
        verbose_name = '图书管理员'
        verbose_name_plural = verbose_name


class Book(models.Model):
    id = models.AutoField(verbose_name='书目编号', primary_key=True, unique=True)
    title = models.CharField(verbose_name='书名', max_length=200)
    author = models.CharField(verbose_name='作者', max_length=50)
    publisher = models.CharField(verbose_name='出版商', max_length=50)
    isbn = models.CharField(verbose_name='ISBN', unique=True, max_length=25)
    date = models.CharField(verbose_name='出版年月', max_length=7)
    number = models.PositiveIntegerField(verbose_name='册数', default=0)
    operator = models.ForeignKey(verbose_name='经办人', to=Librarian, to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    class Meta:
        db_table = 'books'
        verbose_name = '书目'
        verbose_name_plural = verbose_name


class BookCopy(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    copyNO = models.CharField(verbose_name='书册编号', unique=True, max_length=20)
    isbn = models.ForeignKey(verbose_name='ISBN', to=Book, to_field='isbn', on_delete=models.CASCADE)
    position_choices = (
        (1, "图书流通室"),
        (2, "图书阅览室"),
    )
    position = models.SmallIntegerField(verbose_name='位置', choices=position_choices, default=1)
    state_choices = (
        (1, "未借出"),
        (2, "已借出"),
        (3, "不外借"),
        (4, "已预约"),
    )
    state = models.SmallIntegerField(verbose_name='借阅状态', choices=state_choices, default=1)
    operator = models.ForeignKey(verbose_name='经办人', to=Librarian, to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.isbn} {self.id}"
    
    class Meta:
        db_table = 'book_copies'
        verbose_name = '书册'
        verbose_name_plural = verbose_name


class BorrowRecord(models.Model):
    id = models.AutoField(verbose_name='借阅记录编号', primary_key=True, unique=True)
    reader_id = models.ForeignKey(verbose_name='读者编号', to=Reader, to_field='id', on_delete=models.CASCADE)
    copy_id = models.ForeignKey(to=BookCopy, to_field='id', on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name='借阅时间')
    due_time = models.DateTimeField(verbose_name='应还时间')
    return_time = models.DateTimeField(verbose_name='归还时间', null=True, blank=True, default=None)
    fine = models.IntegerField(verbose_name='账单金额', null=False, default=0)

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'borrow_records'
        verbose_name = '借阅记录'
        verbose_name_plural = verbose_name


class ReserveRecord(models.Model):
    id = models.AutoField(verbose_name='预约记录编号', primary_key=True, unique=True)
    reader_id = models.ForeignKey(verbose_name='读者编号', to=Reader, to_field='id', on_delete=models.CASCADE)
    isbn = models.ForeignKey(verbose_name='ISBN', to=Book, to_field='isbn', on_delete=models.CASCADE)
    reserve_time = models.DateTimeField(verbose_name='预约时间', null=True)
    available_days = models.PositiveIntegerField(verbose_name='预约有效天数', default=10)
    copy_id = models.ForeignKey(verbose_name='书册编号', to=BookCopy, to_field='id', on_delete=models.CASCADE, null=True)
    arrive_time = models.DateTimeField(verbose_name='到书时间', null=True)

    def __str__(self):
        return f"{self.reader_id} {self.isbn}"
    
    class Meta:
        db_table = 'reserve_records'
        verbose_name = '预约记录'
        verbose_name_plural = verbose_name

