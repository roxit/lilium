# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):

    username = forms.CharField(label=u'帐号', min_length=2, max_length=12)
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput,
            min_length=4, max_length=12)
    store_password = forms.BooleanField(label=u'记住密码', required=False, initial=False, help_text=u'密码')
    next = forms.CharField(required=False, widget=forms.HiddenInput)

    error_messages = {
        'invalid_login': u'用户名或密码错误'
    }

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
        return self.cleaned_data

    def get_user(self):
        return self.user

