# ������ά��

####<b style="color:red">�����ĵ�����ϵͳ����Ա�ο�ʹ��</b>

### ���ʹ���ն˿��� NAS ������

��¼ DSM�� �ڿ��������ѡ�� <b>�ն˻���SNMP</b>��
����Ҳ�����ѡ��������Ͻ��л����߼�ģʽ<br>
��ȷ����ѡ�� <b>���� SSH ����</b>����ע��˿ںţ�һ��Ϊ22��<br>
��ʹ�� SSH �ͻ��˵�¼ NAS �������Ƽ�ʹ�� [PuTTY](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.73-installer.msi)��

### ���� Docker ����
��¼��ʹ�� `cd` ������� samkit ����Ŀ¼��ͨ�� DSM File Station ���õ�Ŀ¼һ��λ�� `/volume#`��

```shell
docker build -f Dockerfile_Local -t samkit .
docker run -d -p 80:80 samkit
```

### ���� Docker ����

```shell
docker restart <id>
```
`restart` ������Ҫ����ID��Ϊ��������ͨ�� `docker container list` ������

### ��ν��� Docker ����������

```shell
docker exec -it <name> /bin/bash
```
`exec` ������Ҫ����������Ϊ��������ͨ�� `docker container list` ������

### Django Admin ��ʼ��

```shell
docker exec -it <name> /bin/bash
cd /home/docker/code/app
python3 manage.py collectstatic
python3 manage.py createsuperuser
```

### Django ���ݿ�����

```shell
docker exec -it <name> /bin/bash
cd /home/docker/code/app
python3 manage.py makemigrations --empty main
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py setup
```

### SVN Server Setup

�����δ�� DSM �а�װ SVN Server�������׼�������������װ��<br>
��Ӧÿ��UE���̣�������һ��SVN�⣬����¼������ַ��

![](/static/images/01_001.png)

���������Ȩ������Ϊ�ɶ�д������Ҫ�κ���Ȩ������ UE ���ύ�����