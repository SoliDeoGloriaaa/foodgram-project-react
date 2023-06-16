from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Follow, User


class UserAdmin(ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email', 'first_name',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
