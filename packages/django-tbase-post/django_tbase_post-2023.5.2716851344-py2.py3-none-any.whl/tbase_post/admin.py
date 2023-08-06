from django.contrib import admin
from django.db import models
# Register your models here.
from .models import Post
# from markdownx.admin import MarkdownxModelAdmin
# from markdownx.widgets import AdminMarkdownxWidget
from martor.widgets import AdminMartorWidget


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_on')
    ordering = ('-created_on', )
    # formfield_overrides = {
    #     models.TextField: {'widget': AdminMarkdownxWidget},
    # }
    formfield_overrides = {
        models.TextField: {
            'widget': AdminMartorWidget
        },
    }

    # pass


admin.site.register(Post, PostAdmin)

# class PostAdmin(MarkdownxModelAdmin):
#     list_display = ('title', 'created_on')
#     pass
# # admin.site.register(Post, PostAdmin)
# admin.site.register(Post, PostAdmin)