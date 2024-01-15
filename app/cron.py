from datetime import datetime, timedelta
from django.core.mail import send_mail
from . import models

def print_time():
    print(datetime.now())

def delete_reserve():
    reserve_list = models.ReserveRecord.objects.all()
    for record in reserve_list:
        # 系统在清除超出预约期限的记录时解除该图书的“已预约”状态；否则，将该图书的状态修改为“未借出”。
        if record.copy_id and \
            record.arrive_time + timedelta(minutes=record.available_days) < datetime.now():  # 当前时间晚于最晚领取时间
                copy = models.BookCopy.objects.filter(id=record.copy_id.id).first()
                copy.state = 1  # 未借出
                copy.save()
                record.delete()

def expire_notice():
    borrow_records = models.BorrowRecord.objects.all()
    for copy in borrow_records:
        if copy.due_time < datetime.now() and not copy.return_time:
            reader_email = models.Reader.objects.get(id=copy.reader_id.id).email
            send_mail(
                subject="书籍归还提醒",
                message="您好，您借阅的书籍已逾期，请尽快归还并缴纳罚金，谢谢!",
                from_email="gzy500699@163.com",
                recipient_list=[reader_email],
            )