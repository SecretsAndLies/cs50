from django.contrib import admin

# Register your models here.
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(Subscribe)
