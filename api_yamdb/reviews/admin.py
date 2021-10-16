from django.contrib import admin

from .models import Category, Comments, Genre, Review, Title, User


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    empty_value_display = '-пусто-'


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review_id', 'author', 'text')
    empty_value_display = '-пусто-'


admin.site.register(User)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Review)
