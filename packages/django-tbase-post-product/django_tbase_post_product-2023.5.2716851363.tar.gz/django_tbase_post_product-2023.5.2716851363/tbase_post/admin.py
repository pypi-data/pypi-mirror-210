from django.contrib import admin
from django.db import models
# Register your models here.
from .models import Post,AmazonSettings
# from markdownx.admin import MarkdownxModelAdmin
# from markdownx.widgets import AdminMarkdownxWidget
from martor.widgets import AdminMartorWidget
from solo.admin import SingletonModelAdmin
from django.utils.safestring import mark_safe

class PostAdmin(admin.ModelAdmin):
    list_display = ('image_data','title', 'created_on','product_name','product_id')
    list_filter = (['created_on']) # 过滤字段
    search_fields =('title', 'product_name','product_id')  # 设置搜索字段
    ordering = ('-created_on','product_name','product_id' )
    # formfield_overrides = {
    #     models.TextField: {'widget': AdminMarkdownxWidget},
    # }
    readonly_fields=('image_data',)

    def image_data(self, obj):
        return mark_safe(f'<img width="100px" class="list_img_article_img" src="{obj.article_img}">')
    formfield_overrides = {
        models.TextField: {
            'widget': AdminMartorWidget
        },
    }

    # pass


admin.site.register(Post, PostAdmin)

class AmazonSettingsAdmin(SingletonModelAdmin):
    # form = ConfigurationForm):
    # form = ConfigurationForm
    # list_display = ('site_title', 'maintenance_mode')
    # 编辑页面字段定制
    fieldsets = [
        ("Base information", {
            'fields': [
                'store_id'
            ]
        }),
       
    ]
    pass
# 注册配置页面
admin.site.register(AmazonSettings, AmazonSettingsAdmin)













# class PostAdmin(MarkdownxModelAdmin):
#     list_display = ('title', 'created_on')
#     pass
# # admin.site.register(Post, PostAdmin)
# admin.site.register(Post, PostAdmin)