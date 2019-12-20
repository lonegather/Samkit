# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import markdown

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from main import models


def renderer(func):
    def inner(request, project_id):
        try:
            current_project = models.Project.objects.get(id=project_id)
            request.session['current_project_id'] = str(project_id)
        except ObjectDoesNotExist:
            request.session['current_project_id'] = None
            return HttpResponseRedirect('/')

        context = func(**request.GET)
        context['current_path'] = request.path
        context['current_project'] = current_project
        context['projects'] = models.Project.all()
        context['user'] = request.user
        for key, val in request.GET.items():
            context[key] = val
        return render(request, context['page'], context)
    return inner


@renderer
def index_project(**kwargs):
    return {'page': 'index.html'}


@renderer
def settings(**kwargs):
    return {'page': 'settings.html'}


@renderer
def doc(**kwargs):
    doc_dir = os.path.dirname(os.path.abspath(__file__))
    doc_file = os.path.abspath(os.path.join(doc_dir, '../../docs/README.md'))
    with open(doc_file, 'r') as f:
        return {
            'page': 'help.html',
            'doc': markdown.markdown(f.read(), extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
        }


def index(request):
    if not request.session.get('current_project_id', None):
        request.session['current_project_id'] = str(models.Project.all()[0]['id'])
    return HttpResponseRedirect(request.path + request.session['current_project_id'])


def user_login(request):
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['psw']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        return HttpResponseRedirect(request.GET['next'])


def user_logout(request):
    logout(request)
    tokens = request.GET['next'].split('/')
    if 'settings' in tokens:
        tokens.remove('settings')
        return HttpResponseRedirect('/'.join(tokens))
    return HttpResponseRedirect(request.GET['next'])


def api(request):
    table = request.path.split('/')[-1]
    if not table:
        return HttpResponse('')
    if table == 'auth':
        return api_auth(request)
    if request.method == 'GET':
        return api_get(request, table)
    elif request.method == 'POST':
        return api_set(request, table)


def api_get(request, table):
    flt = {}
    query_dict = {
        'project': models.Project.all,
        'entity': models.Entity.get,
        'stage': models.Stage.get,
        'task': models.Task.get,
        'genus': models.Genus.get,
        'tag': models.Tag.get,
    }
    for key in request.GET:
        flt[key] = request.GET[key]
    return HttpResponse(json.dumps(query_dict[table](**flt)))


def api_set(request, table):
    form = dict(request.POST)
    modify_dict = {
        'project': models.Project.set,
        'entity': models.Entity.set,
        'task': models.Task.set,
    }
    if request.FILES:
        for f in request.FILES:
            form[f] = request.FILES[f]
    modify_dict[table](form)
    return HttpResponse("")


def api_auth(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps(request.user.is_authenticated))
    elif request.method == 'POST':
        response = {}
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response['session'] = request.session.session_key
            response['name'] = user.username
            try:
                response['info'] = user.profile.name
                response['role'] = user.profile.role.name
            except:
                pass

        return HttpResponse(json.dumps(response))
