# ������ά��

####<b style="color:red">�����ĵ�����ϵͳ����Ա�ο�ʹ��</b>

��
### ���ʹ���ն˿��� NAS ������

��¼ DSM�� �ڿ��������ѡ�� <b>�ն˻���SNMP</b>��
����Ҳ�����ѡ��������Ͻ��л����߼�ģʽ<br>
��ȷ����ѡ�� <b>���� SSH ����</b>����ע��˿ںţ�һ��Ϊ22��<br>
��ʹ�� SSH �ͻ��˵�¼ NAS �������Ƽ�ʹ�� [PuTTY](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.73-installer.msi)��

### ���� Docker Image

��¼��ʹ�� `cd` ������� samkit ����Ŀ¼��ͨ�� DSM �� File Station ���õ�Ŀ¼һ��λ�� `/volume#`��

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

�����δ�� DSM �а�װ SVN Server�������׼�������������װ��<br>
��Ӧÿ��UE���̣�������һ��SVN�⣬����¼��ַ��