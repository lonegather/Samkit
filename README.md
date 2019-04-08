# Django, uWSGI and Nginx in a container, using Supervisord

### Build and run locally 
* `docker build -f Dockerfile_Local -t image_name .`
* `docker run -d -p 80:80 image_name`
* go to 127.0.0.1 to see if works


### Database initialization
* `docker exec -it container_name /bin/bash`
* `cd /home/docker/code/app`
* `python3 manage.py collectstatic`
* `python3 manage.py makemigrations --empty app_name`
* `python3 manage.py makemigrations`
* `python3 manage.py migrate`
* `python3 manage.py createsuperuser`

This docker image build refers to [dockerfiles/django-uwsgi-nginx](https://github.com/dockerfiles/django-uwsgi-nginx), replacing all download sources with Chinese websites to solve connection issues (local build). For DockerHub Autobuild, use the original Dockerfile.
