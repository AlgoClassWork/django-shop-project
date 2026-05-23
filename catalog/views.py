from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category, Review, Order, OrderItem
from .forms import ReviewForm, CheckoutForm, SearchForm


# --- Регистрация ---

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# --- Каталог ---

def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()
    search_form = SearchForm(request.GET)

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    if search_form.is_valid():
        q = search_form.cleaned_data.get('q')
        if q:
            products = products.filter(name__icontains=q)

    return render(request, 'catalog/product_list.html', {
        'products': products,
        'categories': categories,
        'search_form': search_form,
        'active_category': category_slug,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.select_related('author').all()
    review_form = ReviewForm()
    user_reviewed = request.user.is_authenticated and reviews.filter(author=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated and not user_reviewed:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            return redirect('product_detail', pk=pk)

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'user_reviewed': user_reviewed,
    })


# --- Корзина (в сессии) ---

def cart_get(session):
    return session.setdefault('cart', {})  # {product_id: quantity}


def cart_view(request):
    cart = cart_get(request.session)
    items = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.objects.filter(pk=product_id).first()
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    return render(request, 'catalog/cart.html', {'items': items, 'total': total})


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = cart_get(request.session)
    pid = str(pk)
    cart[pid] = cart.get(pid, 0) + 1
    request.session.modified = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = sum(cart.values())
        return JsonResponse({'count': count})
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def cart_remove(request, pk):
    cart = cart_get(request.session)
    cart.pop(str(pk), None)
    request.session.modified = True
    return redirect('cart')


def cart_update(request, pk):
    cart = cart_get(request.session)
    qty = int(request.POST.get('qty', 1))
    if qty > 0:
        cart[str(pk)] = qty
    else:
        cart.pop(str(pk), None)
    request.session.modified = True
    return redirect('cart')


# --- Оформление заказа ---

@login_required
def checkout(request):
    cart = cart_get(request.session)
    if not cart:
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            total = 0
            order = Order.objects.create(
                user=request.user,
                address=form.cleaned_data['address'],
            )
            for product_id, qty in cart.items():
                product = Product.objects.filter(pk=product_id).first()
                if product and product.stock >= qty:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=product.price,
                    )
                    product.stock -= qty
                    product.save()
                    total += product.price * qty

            order.total_price = total
            order.save()
            request.session['cart'] = {}
            return redirect('order_detail', pk=order.pk)
    else:
        form = CheckoutForm()

    # Посчитаем итог для отображения
    items, total = [], 0
    for product_id, qty in cart.items():
        product = Product.objects.filter(pk=product_id).first()
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'qty': qty, 'subtotal': subtotal})

    return render(request, 'catalog/checkout.html', {'form': form, 'items': items, 'total': total})


# --- Заказы пользователя ---

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'catalog/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'catalog/order_detail.html', {'order': order})
