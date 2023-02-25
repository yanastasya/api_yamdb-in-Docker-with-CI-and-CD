from django.contrib import admin

from .models import Categorie, Comment, Genre, Review, Title, TitleGenre


class TitlesAdmin(admin.ModelAdmin):

    list_display = (
        'pk', 'name', 'year', 'description',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Title, TitlesAdmin)
admin.site.register(Genre)
admin.site.register(Categorie)
admin.site.register(TitleGenre)
admin.site.register(Review)
admin.site.register(Comment)
