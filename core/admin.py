from django.contrib import admin
from .models import Block, Image

class BlockAdmin(admin.ModelAdmin):
    pass

admin.site.register(Block, BlockAdmin)

class ImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Image, ImageAdmin)