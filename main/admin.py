from django.contrib import admin
from django.utils.safestring import mark_safe
import os
from .models import ModelFile, MinMaxFile


@admin.register(ModelFile)
class ModelFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_file', 'draft', 'datetime']
    list_editable = ['draft']
    fields = ['file', 'description', 'draft', 'datetime']
    readonly_fields = ['datetime']

    def get_file(self, obj):
        return mark_safe(f'<a href={obj.file.url}>{os.path.basename(obj.file.name)}</a>')

    get_file.short_description = 'Модель'


@admin.register(MinMaxFile)
class MinMaxFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_file', 'datetime']
    fields = ['file', 'description', 'datetime']
    readonly_fields = ['datetime']

    def get_file(self, obj):
        return mark_safe(f'<a href={obj.file.url}>{os.path.basename(obj.file.name)}</a>')

    get_file.short_description = 'Модель'
