from django.contrib import admin
from .models import Repository, Star

admin.site.register(Repository)
admin.site.register(Star)