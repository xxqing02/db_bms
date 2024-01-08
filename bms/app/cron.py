import datetime
from django.core.mail import send_mail
import models

def delete_reserve():
    reserve_list = models.reserve.objects.all()
    for i in reserve_list:
        if (
            i.book_arrive_time + datetime.timedelta(days=i.reserve_days)
            < datetime.datetime.now()
        ):
            book_info = models.book_info.objects.filter(
                book_id=i.book_id.book_id
            ).first()
            book_info.state = "未借出"
            book_info.save()
            i.delete()


def expire_notice():
    borrow_list = models.borrow.objects.all()
    for i in borrow_list:
        if i.due_time < datetime.datetime.now():
            reader_email = models.reader.objects.get(id=i.reader_id.id).email
            send_mail(
                subject="书籍归还提醒",
                message="您好,您借阅的书籍已逾期,请尽快归还并缴纳罚金,谢谢!",
                from_email="gzy500699@163.com",
                recipient_list=[reader_email],
            )

def print_hello():
    print('hello')