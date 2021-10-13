from django.contrib import admin

from .models import Users

admin.site.register(Users)


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'genre', 'category')
    search_fields = ('name', 'genre', 'category')
    list_filter = ('category',)
    empty_value_display = '-пусто-'
