from django.contrib import admin

from .models import *


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "p_code", "name", "level", "is_delete", "spell")
    search_fields = ("id", "code", "p_code", "name", "spell")
    fields = ("id", "code", "p_code", "name", "level", "is_delete", "spell")
    readonly_fields = ['id']
    list_per_page = 20


@admin.register(NoticeType)
class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "value", "name", "description",)
    search_fields = ("id", "value", "name")
    fields = ("id", "value", "name", "description",)
    readonly_fields = ['id']
    list_per_page = 20


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "notice_type", "notice_title", "notice_content", "link", "files", "status",
        "created_time", "read_time", "expire_time", "thread_id", "from_user_id", "to_user_id", "to_role_id",
    )
    search_fields = ("id", "notice_type", "from_user_id", "to_user_id", "to_role_id")
    fields = (
        "id", "notice_type", "notice_title", "notice_content", "link", "files", "status",
        "created_time", "read_time", "expire_time", "thread_id", "from_user_id", "to_user_id", "to_role_id"
    )
    readonly_fields = ['id', "created_time"]
    list_per_page = 20


@admin.register(AccessLevel)
class AccessLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "access_code", "access_level", "name", "description")
    search_fields = ("id", "access_code", "access_level",)
    fields = ("id", "access_code", "access_level", "name", "description")
    readonly_fields = ['id']
    list_per_page = 20


@admin.register(Encyclopedia)
class EncyclopediaAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "question", "created_time", "updated_time")
    search_fields = ("id", "user_id", "question", "created_time", "updated_time")
    fields = ("id", "user_id", "question", "created_time", "updated_time")
    readonly_fields = ['id']
    list_per_page = 20
