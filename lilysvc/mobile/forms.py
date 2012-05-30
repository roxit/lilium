# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):

    username = forms.CharField(label=u'帐号', min_length=2, max_length=12)
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput,
            min_length=4, max_length=12)
    save_password = forms.BooleanField(label=u'记住密码', required=False, initial=False, help_text=u'记住密码后服务器会自动登陆小百合')
    next = forms.CharField(required=False, widget=forms.HiddenInput)

    error_messages = {
        'invalid_login': u'用户名或密码错误'
    }

    def clean(self):
        if self.errors:
            return
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        save_password = self.cleaned_data['save_password']
        if username and password:
            self.user = authenticate(username=username, password=password,
                    save_password=save_password)
            if self.user is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
        return self.cleaned_data

    def get_user(self):
        return self.user


class ComposeForm(forms.Form):

    title = forms.CharField(label=u'标题', min_length=1)
    body = forms.CharField(label=u'正文', min_length=1, max_length=2048, widget=forms.Textarea)
    pid = forms.CharField(required=False, widget=forms.HiddenInput)
    gid = forms.CharField(required=False, widget=forms.HiddenInput)

