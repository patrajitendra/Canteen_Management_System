from django.urls import path
from . import views
from .views import get_items


urlpatterns = [
    path('', views.index, name='index'), 
    path('register/', views.student_register, name='student_register'),
    path('success/', views.success, name='success'),
    path('add_meal/',views.add_meal,name='add_meal'),
    path('display_menu/',views.menu,name='menu'),
    path('create/', views.create_item, name='create_item'),
    path('items/', views.item_list, name='item_list'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/list/', views.category_list, name='category_list'),
    path('get-items/', get_items, name='get_items'),
    path('success/', views.success_page, name='success_page'),  # Add a success page URL
    path('items/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('items/delete/<int:item_id>/', views.delete_item, name='delete_item'),

    
    #contact
    path('contact/',views.contact,name='contact')
]
