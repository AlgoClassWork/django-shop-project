from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *

def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        form.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    search_result = request.GET.get('search')
    if search_result:
        products = products.filter(name__icontains=search_result)

    context = {'products': products, 'categories': categories}
    return render(request, 'product_list.html', context)