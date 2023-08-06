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
from solo.models import SingletonModel

class Post(models.Model):
    title = models.CharField("标题",max_length=255,)
    # slug = models.SlugField(
    #     unique=True,
    #     max_length=255,
    # )
    # content = models.TextField()
    content = MartorField("内容")
    created_on = models.DateTimeField("创建时间",auto_now_add=True)

    article_img = models.CharField("图片",
                           max_length=255,
                           blank=True,
                           help_text="""
                           可以将图片上传到https://box.maomihezi.com/

                            不要填写?x-oss-process=style/mini_auto，用于后期自动处理图片
                           """
                           )
    product_name = models.CharField("推广产品名字",
                           max_length=255,
                           blank=True,
                           help_text="""
                           产品名 便于
                           """
                           )

    product_id = models.CharField("推广产品id",
                           max_length=255,
                           blank=True,
                           help_text="""填写亚马逊的产品id，用于产生产品链接,
                           比如：https://www.amazon.com/Audio-Wireless-Bluetooth-Earbuds-Charging/dp/B07R7DT3JV/
                           id则为B07R7DT3JV
                           
                           """
                           )
    
    # author = models.TextField()
    # text = MarkdownField(rendered_field='text_rendered', use_editor=False, use_admin_editor=True,validator=VALIDATOR_STANDARD)
    # text_rendered = RenderedMarkdownField(default='')
    tags = TaggableManager("标签")
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
        


class AmazonSettings(SingletonModel):
    """
    亚马逊推广配置页面
    """
    store_id = models.CharField("亚马逊联盟推广id",
                                    max_length=32,
                                    null=True,
                                    blank=True,
                                    default=None,
                                    help_text="""
                                    亚马逊的推广id，用于生成推广链接，可以通过https://affiliate-program.amazon.com/home 注册。
                                    
                                    """)

    def __str__(self):
        return "Amazon Settings"

    class Meta:
        verbose_name = "Amazon Settings"
