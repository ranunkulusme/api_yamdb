from django.contrib import admin

from .models import Categories, Genres, Titles, Users, Reviews, Comments


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'genre', 'category')
    search_fields = ('name', 'genre', 'category')
    list_filter = ('category',)
    empty_value_display = '-пусто-'


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review_id', 'author', 'text')
    empty_value_display = '-пусто-'


admin.site.register(Users)
admin.site.register(Titles, TitlesAdmin)
admin.site.register(Categories)
admin.site.register(Genres)
admin.site.register(Reviews)
