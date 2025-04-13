from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'username']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']

    def create(self, validated_data):
        menuitem_id = validated_data['menuitem_id']
        menuitem = MenuItem.objects.get(id=menuitem_id)
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * validated_data['quantity']
        return super().create(validated_data)
    
class OrderItemsSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'unit_price', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2)
    order_item = OrderItemsSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_id', 'delivery_crew', 'status', 'total', 'date', 'order_item']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'


class MenuitemGetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'title', 'price', 'featured']
        model = MenuItem

class CartGetSerializer(serializers.ModelSerializer):
    menuitem = MenuitemGetSerializer(read_only=True)
    class Meta:
        fields = ['id', 'menuitem', 'quantity', 'price']
        model = Cart

class OrderItemGetSerializer(serializers.ModelSerializer):
    menuitem = MenuitemGetSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'price']


class OrderGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)
    order_item = OrderItemGetSerializer(read_only=True, many=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'date', 'delivery_crew', 'order_item']

class OrderDeliverySerializer(serializers.ModelSerializer):
    delivery_crew_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Order
        fields = ['delivery_crew_id']