from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Std, Cat,Customer,Order
from django.contrib.auth import logout

def home(request):
     if request.method == 'GET':
        products = None
        # request.session.get('cart').clear()
        Categories = Cat.get_all_pro()  # Correctly calls the static method
        cat_id = request.GET.get('category')
        
        if cat_id:
            products = Std.get_all_pro_by_category(cat_id)
        else:
            products = Std.get_all_pro()  # Correctly calls the static method
        
        
        data={
            'products':products,
            'categories':Categories
        }
        
        print('you are', request.session.get('customer_email'))
        
        return render(request, 'home.html', data)

     elif request.method == 'POST':
        product = request.POST.get('product')  # Getting the product ID/name   it will check Quantity
        remove=request.POST.get('remove')
        # Get the current cart from session, or create an empty one if not available
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product]  = quantity-1
                else:
                    cart[product]  = quantity+1

            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        
        print(request.session['cart'])  # Debugging: Print the cart contents
        
        return redirect('home')

def home1(request):
    return render(request, 'home1.html')
    
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def add(request):
    return render(request, 'add.html')
from django.shortcuts import render
from django.http import HttpResponse
from .models import Customer

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'values': {}})
    else:
        postData = request.POST
        f_name = postData.get('firstname')  # Corrected to match the form field
        l_name = postData.get('lastname')   # Corrected to match the form field
        phoneno = postData.get('phone')
        Email = postData.get('email')
        Password = postData.get('password')

        # Check if any fields are empty
        if not f_name or not l_name or not phoneno or not Email or not Password:
            return render(request, 'signup.html', {
                'error': 'All fields are required!',
                'values': postData  # Pass the form data back for persistence
            })

        customer_instance = Customer(
            fname=f_name,
            lname=l_name,
            phone=phoneno,
            email=Email,
            password=Password
        )

        # Check if the email already exists
        if customer_instance.is_exit():
            return render(request, 'signup.html', {
                'error': 'Email already exists!',
                'values': postData  # Pass the form data back for persistence
            })

        customer_instance.reg()  # Save the customer to the database

        # Redirect to the home page after successful registration
        return redirect('login')
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Fetch customer by email
        customer_instance = Customer.get_customer_by_email(email)
        
        # Check if customer exists and if the password matches
        if customer_instance and customer_instance.password == password:
           
            # Successful login, store customer details in session
            request.session['customer_id'] = customer_instance.id
            request.session['customer_email'] = customer_instance.email  # Store email in session
            return redirect('home')  
        else:
            # Invalid login, show error message
            return render(request, 'login.html', {
                'error': 'Invalid email or password.'
            })

def signout(request):
    request.session.clear()
    return redirect('login')
def signout1(request):
    return redirect('home')


def cart(request):
    if request.method == 'GET':
        # Ensure 'cart' exists in the session before accessing it
        if 'cart' not in request.session:
            request.session['cart'] = {}  # Initialize the cart if it doesn't exist

        ids = list(request.session['cart'].keys())  # Get cart item IDs from the session
        prod = Std.get_product_by_id(ids)  # Fetch product objects by IDs
        
    return render(request, 'cart.html', {'prod': prod})

def checkout(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        phoneno = request.POST.get('phone')
        Price = request.POST.get('Price')
        cart = request.session.get('cart')
        products = Std.get_product_by_id(list(cart.keys()))

        # Get the customer instance from session
        customer_id = request.session.get('customer_id')
        customer_instance = Customer.objects.get(id=customer_id)

        # Iterate through products and place orders
        for product in products:
            quantity = cart.get(str(product.id))  # Get quantity from cart
            if quantity:  # Ensure quantity is valid
                order = Order(
                    customer=customer_instance,
                    product=product,
                    price=product.price,
                    quantity=quantity,
                    address=address,
                    Phone_no=phoneno,
                    Price=Price
                )
                order.place_order()  # Now this works

        # Clear the cart after placing all orders
        request.session['cart'] = {}
        return redirect('cart')


from middleware.auth import auth_middleware
@auth_middleware
def order(request):
    if request.method == 'GET':
        # Fetch the logged-in customer's ID from the session
        customer_id = request.session.get('customer_id')

       
        
        orders = Order.get_order_by_customer(customer_id).order_by('-date')
        
        # Render the order template with the fetched orders
        return render(request, 'order.html', {'orders': orders})

from .form import CatForm
def addcat(request):
    if request.method == 'POST':
        form = CatForm(request.POST)
        if form.is_valid():
            form.save()
           
            return redirect('home') 
    else:
        form = CatForm()
    return render(request, 'addcat.html', {'form': form})

def listcat(request):
    categories = Cat.objects.all()  
    return render(request, 'listcat.html', {'categories': categories})


def deletecat(request, id):
    remove = get_object_or_404(Cat, id=id)  # Use the Cat model
    remove.delete()
    return redirect('home')  # Ensure 'home' is the correct URL name


def editcat(request, id):
    edit = get_object_or_404(Cat, id=id)  # Use the Cat model
    if request.method == 'POST':
        form = CatForm(request.POST, instance=edit)
        if form.is_valid():
            form.save()
            return redirect('home')  # Ensure 'home' is the correct URL name
    else:
        form = CatForm(instance=edit)
    
    content = {'form': form}
    return render(request, 'editcat.html', content)
from .form import ProductForm

def addpro(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the list of products
    else:
        form = ProductForm()
    return render(request, 'addpro.html', {'form': form})


def listpro(request):
   
    products = Std.objects.all()
    return render(request, 'listpro.html', {'products': products})

def deletepro(request, id):
    product = get_object_or_404(Std, id=id)
    product.delete()
    return redirect('listpro')

def editpro(request, id):
    product = get_object_or_404(Std, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('listpro')  # Redirect after updating the product
    else:
        form = ProductForm(instance=product)

    return render(request, 'editpro.html', {'form': form})


def finalorder(request):
    orders = Order.objects.all()  # Fetch all orders
    return render(request, 'finalorder.html', {'orders': orders})
from .form import OrderForm

def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('finalorder')  # Redirect to the list of orders after editing
    else:
        form = OrderForm(instance=order)

    return render(request, 'edit_order.html', {'form': form})

