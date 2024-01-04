# db_bms
上海大学计算机工程与科学学院 《数据库原理(1)》 课程项目

图书管理系统  

## 项目构建
1. 安装`requirements.txt`配置环境。
2. `config_example.yaml`文件是数据库用户配置信息的示例文件，复制一份到同级目录并重命名为`config.yaml`，将`password`修改为自己的密码。
3. 运行init.py，创建数据库bms
4. 在终端中输入python manage.py migrate
5. 在终端中输入python manage.py makemigrations app
6. 在终端中输入python manage.py migrate app
7. 在终端中输入python manage.py runserver 0.0.0.0:8000
8. 在浏览器地址栏输入127.0.0.1/login