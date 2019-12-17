# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import markdown
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from main import models


def context_render(request, project_id, page, **kwargs):
    current_project = models.Project.objects.get(id=project_id)
    context = {
        'current_project': current_project,
        'projects': models.Project.all(),
        'request': request,
        'user': request.user,
    }
    for k, v in kwargs.items():
        context[k] = v
    return render(request, page, context)


# Create your views here.
def index(request):
    prj_id = models.Project.all()[0]['id']
    return HttpResponseRedirect(request.path + prj_id)


def index_project(request, project_id):
    return context_render(
        request,
        project_id,
        'index.html',
    )


def doc(request, project_id):
    doc_dir = os.path.dirname(os.path.abspath(__file__))
    doc_file = os.path.abspath(os.path.join(doc_dir, '../../docs/README.md'))
    with open(doc_file, 'r') as f:
        return context_render(
            request,
            project_id,
            'help.html',
            doc=markdown.markdown(f.read(), extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ]),
        )


def auth(request):
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
    return HttpResponseRedirect(request.GET['next'])


def api(request):
    table = request.path.split('/')[-1]
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
    # Group('global').send({'text': '%s changed' % form['name']})
    return HttpResponse("")
