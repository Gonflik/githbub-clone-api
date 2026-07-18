from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=40)
    name =  models.CharField(max_length=40)
    email = models.EmailField()
    bio = models.TextField()

    #passwords, idk 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


