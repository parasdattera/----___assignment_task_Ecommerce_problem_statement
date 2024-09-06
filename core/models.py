from django.db import models
from django.core.validators import RegexValidator,MinValueValidator,MaxValueValidator
# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=255,unique=True)    
    phone_regex = RegexValidator(
    regex=r'^\+?\d{1,4}?\d{10}$',
    message="Phone number must include the country code and be followed by a 10-digit number."
)
    contact_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField()

class Product(models.Model):
    name = models.CharField(unique=True,max_length=255)
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(0.01),  # Minimum weight should be a positive decimal
            MaxValueValidator(25.00)  # Maximum weight is 25kg
        ],
        help_text="Weight in kg (up to 25kg, positive values only)."
    )

    
class Order(models.Model):
    order_number = models.CharField(max_length=10,unique=True,blank=True)
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    order_date = models.DateField()
    address = models.CharField(max_length=255)

    def save(self,*args, **kwargs):
        if not self.order_number:
            prev_order = Order.objects.all().order_by('id').last()
            if prev_order:
                prev_order_no = prev_order.order_number
                order_int = int(prev_order_no[3:])
                new_order_int = order_int+1
                new_order_number = f'ORD{new_order_int:05d}'
            else:
                new_order_number = 'ORD00001'
            self.order_number = new_order_number
        super(Order,self).save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()