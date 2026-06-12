import datetime

from django.db import models

class Customer(models.Model):
    name=models.CharField(max_length=50)
    gender=models.CharField(max_length=6)
    address=models.TextField()
    pincode=models.IntegerField()
    contactno=models.CharField(max_length=15)
    emailaddress=models.EmailField(max_length=50,primary_key=True)
    password = models.CharField(max_length=128, null=True)
    regdate=models.DateTimeField(auto_now_add=True)

    def is_exists(self):
        if Customer.objects.filter(emailaddress=self.emailaddress):
            return True
        else:
            False

    @staticmethod
    def get_customer_by_email(email):
        return Customer.objects.get(emailaddress=email)





class Login(models.Model):
    userid=models.CharField(max_length=50,primary_key=True)
    password = models.CharField(max_length=128, null=True)
    usertype=models.CharField(max_length=30)

class Category(models.Model):
    name= models.CharField(max_length=50)
    def __str__(self):
        return self.name
    @staticmethod
    def get_all_category():
        return Category.objects.all()


class Product(models.Model):
    name= models.CharField(max_length=50)
    price= models.IntegerField(default=0)
    desc =models.CharField(max_length=200)
    category= models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image= models.ImageField(upload_to='newproducts/')

    @staticmethod
    def get_products_by_categoryid(category_id):
        return Product.objects.filter(category=category_id)


    @staticmethod
    def get_all_products():
        return Product.objects.all()
    @staticmethod
    def get_product_by_id(productid):
        return Product.objects.get(id=productid)


class Orders(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.DO_NOTHING)
    product=models.ForeignKey(Product,on_delete=models.DO_NOTHING)
    price=models.IntegerField()
    address=models.CharField(max_length=200)
    pincode=models.CharField(max_length=10)
    quantity= models.IntegerField()
    order_date=models.DateField(default=datetime.datetime.today)
    completed= models.BooleanField(default=False)

class ShoppingCart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()



import hashlib
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    email = models.EmailField()
    code_hash = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()

    def is_valid(self, code):
        # Hash comparison
        h = hashlib.sha256(code.encode()).hexdigest()
        return self.code_hash == h and timezone.now() <= self.valid_until

    def __str__(self):
        return f"OTP for {self.email} valid until {self.valid_until}"
