# db_bms
上海大学计算机工程与科学学院 《数据库原理(1)》 课程项目

图书管理系统  

## 项目构建
1. 安装`requirements.txt`配置环境。
2. `config_example.yaml`文件是配置信息的示例文件，复制一份到同级目录并重命名为`config.yaml`，
将`database`中的`password`修改为自己数据库的密码，其他信息可根据需要自定义。
3. 运行`init.py`，创建数据库bms并创建相关表格。
4. 运行`run_server.py`，运行web服务器。
5. 更新应用相关代码时，需要运行`update.py`。