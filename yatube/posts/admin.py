"""This code registers the Post and Group models with their respective custom admin classes using the admin.site.register() function.
This makes the models editable through the admin interface, with the customizations specified in their respective admin classes."""
from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    ''' Класс PostAdmin приводит админку к нужному виду.
    The PostAdmin class specifies the following customizations:
    list_display: A tuple of field names to display in the admin list view for Post objects.
    In this case, it includes the primary key (pk), the text of the post, the publication date, the author, and the group that the post belongs to.
    search_fields: A tuple of field names to search when the user enters a query in the admin search box.
    In this case, it includes the text field of the Post model.
    list_filter: A tuple of field names to filter the admin list view by.
    In this case, it includes the pub_date field of the Post model.
    list_editable: A tuple of field names that can be edited directly in the list view for the Post model.
    In this case, it includes the group field.
    empty_value_display: A string to display when the value of a field is empty.'''

    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    ''' Класс GroupAdmin приводит админку по группам к нужному виду.
    The GroupAdmin class specifies the following customizations:

    list_display: A tuple of field names to display in the admin list view for Group objects.
    In this case, it includes the title, slug, and description fields of the Group model.
    search_fields: A tuple of field names to search when the user enters a query in the admin search box.
    In this case, it includes the title field of the Group model.
    empty_value_display: A string to display when the value of a field is empty.'''

    list_display = ('title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
