# -*- coding: utf-8 -*-
import json
from urllib import quote, unquote

from django.conf import settings
from django import forms
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import pylibmc

from account import get_active_connection
from lilybbs import Lily
from lilybbs.models import BoardManager
from lilybbs.error import *
from mobile.forms import LoginForm, ComposeForm

mc = pylibmc.Client(['127.0.0.1'])


def home(request):
    if request.user.is_authenticated():
        c = mc.get('fav.{0}'.format(request.user.id))
        lily = Lily(request.user.get_profile().last_session)
        if c:
            fav = [(i, lily.board_manager.board_text(i)) for i in c.split('|')]
        else:
            try:
                fav = lily.fetch_favorites()
                mc.set('fav.{0}'.format(request.user.id), '|'.join(fav), time=900)
                fav = [(i, lily.board_manager.board_text(i)) for i in fav]
            except Error:
                fav = None
    else:
        fav = None
    board_manager = BoardManager()
    return render_to_response('home.html',
            dict(favorites=fav, board_manager=board_manager),
            context_instance=RequestContext(request))


def section(request, sid):
    lily = Lily()
    sec = lily.board_manager[int(sid)]
    return render_to_response('section.html',
            dict(section_text=unicode(sec), board_list=sec.board_list))


def hot(request):
    lily = Lily()
    page = lily.fetch_hot()
    return render_to_response('hot.html', dict(page=page, board_manager=lily.board_manager))


def top10(request):
    lily = Lily()
    page = lily.fetch_top10()
    return render_to_response('top10.html', dict(page=page))


def board(request, board):
    return render_to_response('board.html', dict(board=board))


def topic(request, board, pid):
    return render_to_response('topic.html', dict(board=board, pid=pid))


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
        return build_response(exc=e)
    return build_response(topic.json())


def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            redir = unquote(form.cleaned_data.get('next', settings.LOGIN_REDIRECT_URL))
            auth_login(request, form.get_user())
            return HttpResponseRedirect(redir)
        else:
            # invalid, no cleaned_data
            redir = unquote(request.POST.get('next', settings.LOGIN_REDIRECT_URL))
    else:
        form = LoginForm()
        redir = unquote(request.GET.get('next', settings.LOGIN_REDIRECT_URL))
    form.fields['next'].widget.attrs['value'] = quote(redir)
    return render_to_response('login.html',
            dict(form=form),
            context_instance=RequestContext(request))


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


def about(request):
    return render_to_response('about.html')


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
                    return HttpResponseRedirect('/topic/{0}/{1}'.format(board, pid))
                else:
                    return HttpResponseRedirect('/board/{0}'.format(board))
            else:
                # XXX
                form._errors['__all__'] = u'发送失败'
    else:
        params = request.GET
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

    return render_to_response('compose.html',
            dict(form=form, board=board, is_reply=is_reply, post=post),
            context_instance=RequestContext(request))

