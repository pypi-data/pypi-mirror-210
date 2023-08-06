from django.db import models

# Create your models here.

from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse

# from markdownfield.models import MarkdownField, RenderedMarkdownField
# from markdownfield.validators import VALIDATOR_STANDARD
# from markdownx.models import MarkdownxField
from martor.models import MartorField
from taggit.managers import TaggableManager


class Post(models.Model):
    title = models.CharField("标题",max_length=255,)
    # slug = models.SlugField(
    #     unique=True,
    #     max_length=255,
    # )
    # content = models.TextField()
    content = MartorField("内容")
    created_on = models.DateTimeField("创建时间",auto_now_add=True)
    tags = TaggableManager("标签")

    # author = models.TextField()
    # text = MarkdownField(rendered_field='text_rendered', use_editor=False, use_admin_editor=True,validator=VALIDATOR_STANDARD)
    # text_rendered = RenderedMarkdownField(default='')

    def get_absolute_url(self):
        return reverse('detail_view', args=[self.pk])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['created_on']

        def __unicode__(self):
            return self.title