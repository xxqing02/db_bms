import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    charset="utf8",
)

cursor = conn.cursor()

sql = "drop database bms"
cursor.execute(sql)

sql = "create database if not exists bms default charset utf8"
cursor.execute(sql)

sql = "show databases"
cursor.execute(sql)
result = cursor.fetchall()
for i in result:
    print(i)

sql = "use bms"
cursor.execute(sql)

sql = "show tables"
cursor.execute(sql)

result = cursor.fetchall()
for i in result:
    print(i)
