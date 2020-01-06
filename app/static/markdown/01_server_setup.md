# 服务器搭建

####<b style="color:red">以下文档仅供系统管理员参考使用</b>

登录 DSM， 在控制面板中选择 <b>终端机和SNMP</b>。
如果找不到该选项，请点击右上角切换至高级模式：

![](/static/images/01_001.png)

请确保勾选了 <b>启动 SSH 功能</b>，并注意端口号（一般为22）<br>
请使用 SSH 客户端登录 NAS 主机（推荐使用 [PuTTY](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.73-installer.msi)）

### Server Builds (Docker Container)

```shell
docker build -f Dockerfile_Local -t samkit .
docker run -d -p 80:80 samkit
```

### Django Admin Setup
```shell
docker exec -it container_name /bin/bash

cd /home/docker/code/app
python3 manage.py collectstatic
python3 manage.py createsuperuser
```

### Data Setup
Save `/app/setup_template.csv` as `/app/setup.csv` and fill in the data
```shell
docker exec -it container_name /bin/bash

cd /home/docker/code/app
python3 manage.py makemigrations --empty main
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py setup
```

### SVN Server Setup

如果还未在 DSM 中安装 SVN Server，请在套件中心搜索并安装。