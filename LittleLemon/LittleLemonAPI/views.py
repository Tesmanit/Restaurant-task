from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from django.core.paginator import Paginator, EmptyPage


@api_view(['GET', 'POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def menuitems(request):
    if request.method == 'GET':
        queryset = MenuItem.objects.select_related('category')
        category_name = request.query_params.get('category')
        if category_name:
            queryset = queryset.filter(category__title=category_name)
        price = request.query_params.get('price')
        if price:
            queryset = queryset.filter(price__iexact=price)
        ordering = request.query_params.get('ordering')
        if ordering:
            ordering_items = ordering.split(',')
            queryset = queryset.order_by(*ordering_items)
        perpage = request.query_params.get('perpage', default=2)
        if perpage > 2:
            perpage = 2
        page = request.query_params.get('page', default=1)
        paginated_data = Paginator(queryset, per_page=perpage)
        try:
            queryset=paginated_data.page(number=page)
        except EmptyPage:
            queryset = []
        serialized_data = MenuItemSerializer(queryset, many=True)
        return Response(serialized_data.data, status=200)
    else:
        if request.user.groups.filter(name='Manager').exists():
            instance = MenuItemSerializer(data=request.data) 
            if instance.is_valid():
                instance.save()
                return Response(instance.data, status=201)  
            return Response('Data is not valid', status=400) 
        return Response('You are not allowed to perform this action', status=403)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def menuitem(request, pk):
    queryset = MenuItem.objects.get(pk=pk)
    if request.method == 'GET':
        serialized_data = MenuItemSerializer(queryset)
        return Response(serialized_data.data, status=200)
    if request.user.groups.filter(name='Manager').exists():
        if request.method == 'DELETE':
            queryset.delete()
            return Response('Object was successfully deleted', status=200)
        else:
            partial = request.method == 'PATCH'
            instance = MenuItemSerializer(queryset, data=request.data, partial=partial) 
            if instance.is_valid():
                instance.save()
                return Response(instance.data, status=201)  
            return Response('Data is not valid', status=400) 
    return Response('You are not allowed to perform this action', status=403)


@api_view(['GET', 'POST'])
def managers(request):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            queryset = User.objects.filter(groups__name__iexact='Manager').prefetch_related('groups')
            serialized_data = UserSerializer(queryset, many=True)
            return Response(serialized_data.data, status=200)
        elif request.method == 'POST':
            username = request.data.get('username')
            if username:
                user = get_object_or_404(User, username=username)
                if not user.groups.filter(name='Manager').exists():
                    managers = Group.objects.get(name='Manager')
                    managers.user_set.add(user)
                    return Response('User was successfully added to the managers group', status=200)
                return Response('User is already in managers group')
            return Response('Username was not provided', status=400)
    return Response('you do not have access to this urls methods', status=403)


@api_view(['DELETE'])
def manager_removal(request, pk):
    if request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User, pk=pk)
        if user.groups.filter(name='Manager').exists():
            managers = Group.objects.get(name='Manager')
            managers.user_set.remove(user)
            return Response('User was successfully removed from managers group', status=200)
        return Response('This user is already not in manager group', status=400)
    return Response('you do not have access to this urls methods', status=403)


@api_view(['GET', 'POST'])
def delivery_crew(request):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            queryset = User.objects.filter(groups__name__iexact='Delivery crew').prefetch_related('groups')
            serialized_data = UserSerializer(queryset, many=True)
            return Response(serialized_data.data, status=200)
        elif request.method == 'POST':
            username = request.data.get('username')
            if username:
                user = get_object_or_404(User, username=username)
                if not user.groups.filter(name='Delivery crew').exists():
                    managers = Group.objects.get(name='Delivery crew')
                    managers.user_set.add(user)
                    return Response('User was successfully added to the delivery crew group', status=200)
                return Response('User is already in delivery crew group')
            return Response('Username was not provided', status=400)
    return Response('you do not have access to this urls methods', status=403)


@api_view(['DELETE'])
def delivery_crew_removal(request, pk):
    if request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User, pk=pk)
        if user.groups.filter(name='Delivery crew').exists():
            managers = Group.objects.get(name='Delivery crew')
            managers.user_set.remove(user)
            return Response('User was successfully removed from delivery crew group', status=200)
        return Response('This user is already not in delivery crew group', status=400)
    return Response('you do not have access to this urls methods', status=403)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    if request.method == 'GET':
        queryset = Cart.objects.filter(user=request.user).select_related('menuitem')
        serialized_data = CartGetSerializer(queryset, many=True)
        return Response(serialized_data.data, status=200)
    if request.method == 'POST':
        data = request.data.copy()
        data['user_id'] = request.user.pk
        cart_menuitem = MenuItem.objects.get(id=request.data['menuitem_id'])
        try:
            cart_object = Cart.objects.get(user=request.user, menuitem=cart_menuitem)
            cart_object.quantity += int(request.data['quantity'])
            cart_object.price = cart_object.unit_price * cart_object.quantity
            cart_object.save()
            return Response('Menuitem quantity was successfully increased', status=200)
        except:
            instance = CartSerializer(data=data)
            if instance.is_valid():
                instance.save()
                return Response(['Item was added', instance.data], status=201)
    if request.method == 'DELETE':
        queryset = Cart.objects.filter(user=request.user)
        queryset.delete()
        return Response('Deleted', status=200)
    

class Orders(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderGetSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            queryset = Order.objects.all().prefetch_related(Prefetch\
            ('order_item', queryset=OrderItem.objects.prefetch_related('menuitem')))
        elif user.groups.filter(name='Delivery crew').exists():
            queryset = Order.objects.filter(delivery_crew=user).prefetch_related(Prefetch\
            ('order_item', queryset=OrderItem.objects.prefetch_related('menuitem')))
        else:
            queryset = Order.objects.filter(user=user).prefetch_related(Prefetch\
            ('order_item', queryset=OrderItem.objects.prefetch_related('menuitem')))
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status__iexact=status)
        total = self.request.query_params.get('total')
        if total:
            queryset = queryset.filter(total__iexact=total)
        if user.groups.filter(name='Manager').exists() or user.groups.filter(name='Delivery crew').exists():
            customer_id = self.request.query_params.get('customer_id')
            if customer_id:
                queryset = queryset.filter(user__id__iexact=customer_id)
        ordering = self.request.query_params.get('ordering')
        if ordering:
            ordering_items = ordering.split(',')
            queryset = queryset.order_by(*ordering_items)
        perpage = self.request.query_params.get('perpage', default=2)
        if perpage > 2:
            perpage = 2
        page = self.request.query_params.get('page', default=1)
        paginated_data = Paginator(queryset, per_page=perpage)
        try:
            queryset=paginated_data.page(number=page)
        except EmptyPage:
            queryset = []
        return queryset
        
    def post(self, request):
        order_data = {}
        order_data['user_id'] = request.user.id
        carts = Cart.objects.filter(user=request.user)
        order_data['total'] = 0
        for item in carts:
            order_data['total'] += item.price
        order_instance = OrderSerializer(data=order_data)
        if order_instance.is_valid():
            order_instance.save()
        order_item_data = {}
        for item in carts:
            order_item_data['order_id'] = order_instance.data['id']
            order_item_data['menuitem_id'] = item.menuitem_id
            order_item_data['quantity'] = item.quantity
            order_item_data['unit_price'] = item.unit_price
            order_item_data['price'] = item.price
            items_instance = OrderItemSerializer(data=order_item_data)
            if items_instance.is_valid():
                items_instance.save()
        return Response(order_instance.data, status=201)
    

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order(request, pk):
    user = request.user
    order = Order.objects.get(pk=pk)

    if request.method == 'GET':
        if order.user != request.user:
            return Response('You do not have access to this order', status=403)
        order_data = OrderGetSerializer(order)
        return Response(order_data.data, status=200)
    
    if request.method == 'PATCH':
        if user.groups.filter(name='Manager').exists():
            response = []

            if request.data.get('status'):
                if order.status == int(request.data['status']):
                    response = ['This status is already applied to this order']
                else:
                    order.status = request.data['status']
                    order.save()
                    response = ['Order status has been succesfully changed']

            if request.data.get('delivery_crew_id'):

                if order.delivery_crew.id == int(request.data['delivery_crew_id']):
                    response.append('This delivery crew is already applied to this order')
                else:
                    user = User.objects.get(id=request.data['delivery_crew_id'])

                    if not user.groups.filter(name='Delivery crew').exists():
                        response.append('This user is not delivery crew')
                    else:
                        id = {}
                        id['delivery_crew_id'] = request.data['delivery_crew_id']
                        instance = OrderDeliverySerializer(order, data=id, partial=True)
                        if instance.is_valid():
                            instance.save()
                            response.append('Order delivery crew has been succesfully changed')
            return Response(', '.join(response)) if response else Response('Invalid data')
        
        else:
            if user.groups.filter(name='Delivery crew').exists() or order.user==user:
                
                if order.status == int(request.data['status']):
                    return Response('This status is already applied to this order')
                order.status = request.data['status']
                order.save()
                return Response('Order status has been succesfully changed')
            return Response('You do not have permissions to change thus orders status')
        
    if user.groups.filter(name='Manager').exists():
        if request.method == 'DELETE':
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response('You have succesfully deleted this order', status=200)