from django.contrib import admin

from account.models import LilyProfile


class LilyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'lily_password', 'last_session']


admin.site.register(LilyProfile, LilyProfileAdmin)

