# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django import forms
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import direct_to_template

from lilysvc.account import get_active_connection
from lilysvc.lilybbs import Lily
from lilysvc.lilybbs.models import BoardManager
from lilysvc.lilybbs.error import *
from lilysvc.mobile.forms import LoginForm, ComposeForm

def home(request):
    if request.user.is_authenticated():
        lily = Lily(request.user.get_profile().last_session)
        try:
            fav = lily.fetch_favorites()
            fav = [(i, lily.board_manager.board_text(i)) for i in fav]
        except Error:
            fav = None
    else:
        fav = None
    board_manager = BoardManager()
    return render_to_response('mobile/home.html',
            dict(favorites=fav, board_manager=board_manager),
            context_instance=RequestContext(request))

def section(request, sid):
    lily = Lily()
    sec = lily.board_manager[int(sid)]
    return render_to_response('mobile/section.html',
            dict(section_text=unicode(sec), board_list=sec.board_list))

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
        return HttpResponse(json.dumps(str(exc)), status=400, mimetype=JSON_MIME)
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
        raise
        return build_response(exc=e)
    return build_response(topic.json())

def login(request):
    redir = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            store_password = form.cleaned_data.get('store_password', False)
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redir)
    else:
        form = LoginForm()
    return render_to_response('mobile/login.html',
            dict(form=form, redir=redir),
            context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

def about(request):
    return render_to_response('mobile/about.html')

@login_required
def compose(request, board):
    is_reply = False
    post = None
    pid = None
    num = None
    if request.method == 'POST':
        # it's unlikely the session is expired
        lily = get_active_connection(request.user.username)
        form = ComposeForm(data=request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            pid = form.cleaned_data.get('pid', None)
            gid = form.cleaned_data.get('gid', None)
            ret = lily.compose(board, title, body, pid, gid)
            if ret:
                if pid is not None:
                    return HttpResponseRedirect('/board/{0}/{1}'.format(board, pid))
                else:
                    return HttpResponseRedirect('/board/{0}'.format(board))
            else:
                # XXX
                form._errors['__all__'] = u'发送失败'
    else:
        params = request.GET;
        pid = params.get('pid', None)
        num = params.get('num', None)
        form = ComposeForm()
    if pid is not None:
        is_reply = True
        lily = Lily()
        post = lily.fetch_post(board, pid, num)
        form.fields['title'].widget = forms.HiddenInput()
        form.fields['title'].widget.attrs['value'] = 'Re: {0}'.format(post.title.encode('utf-8'))
        form.fields['pid'].widget.attrs['value'] = post.pid
        form.fields['gid'].widget.attrs['value'] = post.gid

    return render_to_response('mobile/compose.html',
            dict(form=form, board=board, is_reply=is_reply, post=post),
            context_instance=RequestContext(request))

