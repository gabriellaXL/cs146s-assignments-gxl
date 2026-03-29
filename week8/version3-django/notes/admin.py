from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "updated_at", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "content")
    ordering = ("-updated_at", "-created_at")
