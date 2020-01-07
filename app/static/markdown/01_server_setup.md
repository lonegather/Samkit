# 服务器维护

####<b style="color:red">以下文档仅供系统管理员参考使用</b>

### 如何使用终端控制 NAS 服务器

登录 DSM， 在控制面板中选择 <b>终端机和SNMP</b>。
如果找不到该选项，请点击右上角切换至高级模式<br>
请确保勾选了 <b>启动 SSH 功能</b>，并注意端口号（一般为22）<br>
请使用 SSH 客户端登录 NAS 主机（推荐使用 [PuTTY](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.73-installer.msi)）

### 创建 Docker 容器
登录后使用 `cd` 命令进入 samkit 所在目录（通过 DSM File Station 设置的目录一般位于 `/volume#`）

```shell
docker build -f Dockerfile_Local -t samkit .
docker run -d -p 80:80 samkit
```

### 重启 Docker 容器

```shell
docker restart <id>
```
`restart` 命令需要容器ID作为参数，可通过 `docker container list` 命令获得

### 如何进入 Docker 容器命令行

```shell
docker exec -it <name> /bin/bash
```
`exec` 命令需要容器名称作为参数，可通过 `docker container list` 命令获得

### Django Admin 初始化

```shell
docker exec -it <name> /bin/bash
cd /home/docker/code/app
python3 manage.py collectstatic
python3 manage.py createsuperuser
```

### Django 数据库重置

```shell
docker exec -it <name> /bin/bash
cd /home/docker/code/app
python3 manage.py makemigrations --empty main
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py setup
```

### SVN Server Setup

如果还未在 DSM 中安装 SVN Server，请在套件中心搜索并安装。<br>
对应每个UE工程，各创建一个SVN库，并记录访问网址。

![](/static/images/01_001.png)

如果将匿名权限设置为可读写，则不需要任何授权即可在 UE 中提交变更。