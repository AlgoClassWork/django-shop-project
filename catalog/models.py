from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название') 
    slug = models.SlugField(unique=True, verbose_name='Слаг') 

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(models.Model):
    pass 

class Review(models.Model):
    pass 

class Order(models.Model):
    pass 

class OrderItem(models.Model):
    pass