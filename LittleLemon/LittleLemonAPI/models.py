from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return self.title
    

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True, default=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.title
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)

    def __str__(self):
        return 'User: ' + self.user.username + ', cart obect: ' + self.menuitem.title
    
    class Meta:
        unique_together = ['user', 'menuitem']
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew_order', blank=True, null=True, default=None)
    status = models.BooleanField(db_index=True, default=False)
    total = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    date = models.DateField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return 'ORDER: USER: ' + self.user.username + ',delivery crew: ' + self.delivery_crew.username \
        if self.delivery_crew else 'ORDER: USER: ' + self.user.username + ', NO DELIVERY CREW'
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_item')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)

    def __str__(self):
        return self.menuitem.title + ' in the order of ' + self.order.user.username + ' user'
    
    class Meta:
        unique_together = ['order', 'menuitem']