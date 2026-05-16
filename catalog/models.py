from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название') 
    slug = models.SlugField(unique=True, verbose_name='Слаг') 

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2 ,verbose_name='Цена')
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='Изображение')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.name
    
    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum( rate.rating for rate in reviews ) / len(reviews)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Review(models.Model):
    RATING_CHOICES = [ (1, 'Очень плохо'), (2, 'Плохо'), (3, 'Нормально'), (4, 'Хорошо'), (5, 'Отлично') ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.author} - {self.product} {self.rating}★'
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('product', 'author')

class Order(models.Model):
    STATUS_CHOICES = [('new', 'Новый'), ('processing', 'В обработке'),
                      ('shipped', 'Отправлен'), ('delivered', 'Доставлен')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    total_price = models.DecimalField(max_digits=10, decimal_places=2 ,verbose_name='Итоговая цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Заказ #{self.id} от {self.user}'
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кол-во')
    price = models.DecimalField(max_digits=10, decimal_places=2 ,verbose_name='Цена')

    def __str__(self):
        return f'{self.product} x{self.quantity}'
    
    def total(self):
        return self.price * self.quantity
