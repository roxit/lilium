# -*- coding: utf-8 -*-
import json

from django.contrib.auth import login as auth_login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import direct_to_template

from lilysvc.lilybbs import Lily
from lilysvc.lilybbs.error import *
from lilysvc.mobile.forms import LoginForm

def index(request):
    if request.user.is_authenticated():
        lily = Lily()
        lily.load_session(request.user.get_profile().last_session)
        try:
            fav = lily.fetch_favorites()
            fav = [(i, lily.board_manager.board_text(i)) for i in fav]
        except Error:
            fav = None
    else:
        fav = None
    return render_to_response('mobile/index.html', dict(favorites=fav), context_instance=RequestContext(request))

def boardlist(request):
    lily = Lily()
    brd_mgr = lily.board_manager
    return render_to_response('mobile/boardlist.html', dict(board_manager=brd_mgr))

def board(request, board, start=None):
    return render_to_response('mobile/board.html', dict(board=board, start=start))

def topic(request, board, pid):
    return render_to_response('mobile/topic.html', dict(board=board, pid=pid))

def top10(request):
    lily = Lily()
    page = lily.fetch_top10()
    return render_to_response('mobile/top10.html', dict(page=page))

def hot(request):
    lily = Lily()
    page = lily.fetch_hot()
    return render_to_response('mobile/hot.html', dict(page=page, board_manager=lily.board_manager))

def build_response(result=None, exc=None):
    JSON_MIME = 'application/json'
    if exc:
        return HttpResponse(json.dumps(str(e)), status=400, mimetype=JSON_MIME)
    return HttpResponse(json.dumps(result), mimetype=JSON_MIME)

def api_board(request, board, start=None):
    lily = Lily()
    try:
        page = lily.fetch_page(board, start)
    except Exception as e:
        return build_response(exc=e)
    return build_response(page.json())

def api_topic(request, board, pid, start=None):
    lily = Lily()
    try:
        topic = lily.fetch_topic(board, pid, start)
    except Exception as e:
        return build_response(exc=e)
    return build_response(topic.json())

def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            store_password = form.cleaned_data.get('store_password', False)
            auth_login(request, form.get_user())
            return HttpResponseRedirect('/')
    else:
        form = LoginForm()
    return render_to_response('mobile/login.html', dict(form=form), context_instance=RequestContext(request))

def logout(request):
    pass

def about(request):
    pass

