from django.urls import path
from .views import *

urlpatterns = [
    path('menu-items', menuitems),
    path('menu-items/<int:pk>', menuitem),
    path('groups/manager/users', managers),
    path('groups/manager/users/<int:pk>', manager_removal),
    path('groups/delivery-crew/users', delivery_crew),
    path('groups/delivery-crew/users/<int:pk>', delivery_crew_removal),
    path('cart/menu-items', cart),
    path('orders', Orders.as_view()),
    path('orders/<int:pk>', order),
]