from django.db import models

# Create your models here.

import django
from django.conf import settings


from django.db import models
from datetime import date

from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

    class Meta:
        app_label = 'test_app'
        
        
class Publisher(models.Model):
    name = models.CharField(max_length=300)

    class Meta:
        app_label = 'test_app'
        
        
class Book(models.Model):
    name = models.CharField(max_length=300)
    pages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    pubdate = models.DateField()

    class Meta:
        app_label = 'test_app'
        
        
class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)
    
    class Meta:
        app_label = 'test_app'
        