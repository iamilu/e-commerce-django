from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class NewUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField (max_length=50)
    phone = models.CharField(max_length=10)
    email=models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email
    
    #to save the data
    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return NewUser.objects.get(email=email)
        except:
            return False

    def isExists(self):
        if NewUser.objects.filter(email =self.email):
            return True
        return False

class Otp(models.Model):
    email=models.EmailField()
    otp = models.IntegerField()

class Sendmail(models.Model):
    send_to = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    email=models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.email

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    is_digital = models.BooleanField(default=False) #if True, no need of shipping else, reuired shipping
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self): #property decorator helps to understand the imageURL as an attribute, not as a method
        try:
            url = self.image.url
        except:
            url = ''
        return url

#customer can have multiple orders
#models.SET_NULL - if a customer is deleted, we don't want to delete the order
#this is for cart
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        items = self.orderitem_set.all()
        for item in items:
            if item.product.is_digital == False:
                shipping = True
        return shipping

    #order = Order.objects.get(customer=customer) #for single customer
    #items = OrderItem.objects.filter(order=order) or items = order.orderitem_set.all()
    #total = sum([item.quantity for item in items])
    @property
    def get_cart_items(self):
        items = self.orderitem_set.all()
        total = sum([item.quantity for item in items])
        return total
    
    #order = Order.objects.get(customer=customer) #for single customer
    #items = OrderItem.objects.filter(order=order) or items = order.orderitem_set.all()
    #total = sum([item.product.price for item in items])
    @property
    def get_cart_total(self):
        items = self.orderitem_set.all()
        total = sum([item.get_total for item in items])
        return total

#cart can have multiple order items
#a single order (cart) can have multiple order items
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
    
    #items = OrderItem.objects.filter(order=order)
    #item = items[0] #for single item
    #total = item.quantity * item.product.price
    @property
    def get_total(self):
        total = self.quantity * self.product.price
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
