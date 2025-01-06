from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Student_Masterfile
import os
from .models import Items, Category,ItemPrice,Transaction
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time
import pytz
import json



def index(request):
    return render(request,'Student/home.html')


# Custom file validation for Aadhar Card (server-side)
def validate_file(aadhar_card):
    file_extension = os.path.splitext(aadhar_card.name)[1].lower()
    if file_extension not in ['.pdf', '.png', '.jpeg', '.jpg']:
        raise ValidationError("File must be in PDF, PNG, or JPEG format.")
    if aadhar_card.size > 4 * 1024 * 1024:  # 4 MB size limit
        raise ValidationError("File size must not exceed 4MB.")

def student_register(request):
    if request.method == 'POST':
        registration_number = request.POST['registration_number']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        batch = request.POST['batch']
        branch = request.POST['branch']
        admission_date = request.POST['admission_date']
        semester = request.POST['semester']
        aadhar_card = request.FILES.get('aadhar_card')
        mobile = request.POST['mobile_number']

        # Server-side validation for admission_date
        if len(str(admission_date)) != 4:
            return render(request, 'Student/student_register.html', {'error': 'Admission date must be in year format (e.g., 2024).'})
        print(admission_date)
        
        # Validate the file
        if aadhar_card:
            try:
                validate_file(aadhar_card)
            except ValidationError as e:
                return render(request, 'Student/student_register.html', {'error': str(e)})

        # Save the student record
        student = Student_Masterfile.objects.create(
            registration_number=registration_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            batch=batch,
            branch=branch,
            admission_date=admission_date,
            semester=semester,
            aadhar_card=aadhar_card,
            mobile = mobile
        )
        return redirect('success')  # Redirect to a success page after saving

    return render(request, 'Student/student_register.html')


def success(request):
    return render(request, 'Student/success.html')

def create_category(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        category_type = request.POST['category_type']

        # Create a new category
        Category.objects.create(category_name=category_name, category_type=category_type)

        return redirect('category_list')  # Redirect to a category list page or any relevant page
    categories = Category.objects.all()

    return render(request, 'Meal_Section/create_category.html',{'categories':categories})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'Meal_Section/category_list.html', {'categories': categories})


def create_item(request):
    if request.method == "POST":
        item_code = request.POST.get('item_code')
        item_name = request.POST.get('item_name')
        category_id = int(request.POST.get('category'))
        price = request.POST.get('price')
      
        # Create the new item
        new_item = Items.objects.create(item_code=item_code, item_name=item_name, category_id=category_id)

        # Create the item price
        ItemPrice.objects.create(item=new_item, price=price)

        return redirect('item_list')
  
    categories = Category.objects.all()
 
    return render(request, 'Meal_Section/create_item.html', {'categories': categories})

def item_list(request):
    items = Items.objects.all()
    return render(request, 'Meal_Section/item_list.html', {'items': items})

def menu(request):
    # Fetch all categories with their items
    categories = Category.objects.all().prefetch_related('items__item_price')
    print(categories)
    context = {
        'categories': categories
    }    
    return render(request,'Menu/display_menu.html',context)

# def add_meal(request):
#     if request.method == "POST":
#         # Get data from the form
#         student_id = request.POST.get('student')
#         category_id = request.POST.get('category')
#         item_id = int(request.POST.get('item'))
#         # payment_mode = request.POST.get('payment_mode')
#         # You may also get the price if needed
#         price_item = ItemPrice.objects.get(item_id=item_id)
#         ist = pytz.timezone('Asia/Kolkata')
#         current_time = timezone.now().astimezone(ist).time()
#         print("Time",current_time)

#         if time(6, 0) <= current_time < time(12, 0):  # 6:00 AM to 11:59 AM
#             meal_type = 'breakfast'
#         elif time(12, 0) <= current_time < time(18, 0):  # 12:00 PM to 5:59 PM
#             meal_type = 'lunch'
#         elif time(18, 0) <= current_time <= time(22, 0):  # 6:00 PM to 10:00 PM
#             meal_type = 'dinner'
#         else:
#             raise ValidationError("Transactions can only be made during meal times (6 AM to 10 PM).")
        
#         #based on condition payment mode
#         payment_status = request.POST.get('payment_status')
#         payment_mode = 'unpaid'
#         payment_done = False
#         if payment_status == 'enabled':
#             conditional_payment_mode = request.POST.get('conditional_payment_mode')
#             # print(conditional_payment_mode)
#             payment_mode = conditional_payment_mode
#             payment_done = True            
        
#         # print(payment_status)
        
#         # Save the transaction details
#         meal_transaction = Transaction(
#             student_id=student_id,
#             category_id=category_id,
#             item_id=item_id,
#             payment_mode=payment_mode,
#             price=price_item.price ,
#             meal_type = meal_type,
#             payment_done = payment_done
#             # Assuming there is a price field in ItemPrice model
#         )
#         meal_transaction.save()

#         # Redirect to a success page or back to the form
#         return redirect('success_page')  # Replace with your success page URL

#     # If it's a GET request, show the form with the existing students and categories
#     students = Student_Masterfile.objects.all()
#     categories = Category.objects.all()
#     return render(request, 'Meal_Section/add_meal.html', {'students': students, 'categories': categories})

def add_meal(request):
    if request.method == "POST":
        # Get data from the form
        student_id = request.POST.get('student')
        category_id = request.POST.get('category')
        item_ids = request.POST.getlist('items[]') # List of item IDs
        quantities = request.POST.getlist('quantities[]')
        print("Items Ids",item_ids)
        payment_status = request.POST.get('payment_status')
        payment_mode = 'unpaid'
        payment_done = False

        if payment_status == 'enabled':
            conditional_payment_mode = request.POST.get('conditional_payment_mode')
            payment_mode = conditional_payment_mode
            payment_done = True

        ist = pytz.timezone('Asia/Kolkata')
        current_time = timezone.now().astimezone(ist).time()

        if time(6, 0) <= current_time < time(12, 0):  # 6:00 AM to 11:59 AM
            meal_type = 'breakfast'
        elif time(12, 0) <= current_time < time(18, 0):  # 12:00 PM to 5:59 PM
            meal_type = 'lunch'
        elif time(18, 0) <= current_time <= time(22, 0):  # 6:00 PM to 10:00 PM
            meal_type = 'dinner'
        else:
            raise ValidationError("Transactions can only be made during meal times (6 AM to 10 PM).")

        # Process each item in the transaction
        for item_id, quantity in zip(item_ids, quantities):
            price_item = ItemPrice.objects.get(item_id=item_id)
            print(price_item)
            print(item_id)
            meal_transaction = Transaction(
                student_id=student_id,
                category_id=category_id,
                item_id=item_id,
                payment_mode=payment_mode,
                price=price_item.price * int(quantity),
                meal_type=meal_type,
                payment_done=payment_done,
                quantity = int(quantity)
            )
            meal_transaction.save()

        # Redirect to a success page or back to the form
        return redirect('success_page')  # Replace with your success page URL

    # If it's a GET request, show the form with the existing students and categories
    students = Student_Masterfile.objects.all()
    categories = Category.objects.all()
    return render(request, 'Meal_Section/add_meal.html', {'students': students, 'categories': categories})


def contact(request):
    return render(request,'Student/contact.html')



def get_items(request):
    category_id = request.GET.get('category_id')
    print(category_id)
    items = Items.objects.filter(category_id=category_id).values('item_id', 'item_name')
    
    return JsonResponse({'items': list(items)})

def success_page(request):
    return render(request, 'Meal_Section/success_page.html')


def edit_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('Data',data)
        item = Items.objects.get(item_id=item_id)
        item.item_code = data.get('item_code', item.item_code)
        item.item_name = data.get('item_name', item.item_name)
        category_name = data.get('category')
        if category_name:
            category, _ = Category.objects.get_or_create(category_name=category_name)
            item.category = category
        try:
            item_price_check = ItemPrice.objects.get(item_id=item_id)
        except:
            item_price_check = {}
        if item_price_check:
            item_price_check.price = data.get('item_price', item.item_price)
            item_price_check.save()
        return JsonResponse({'message': 'Item updated successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)



def delete_item(request, item_id):
    if request.method == 'POST':
        item = Items.objects.get(item_id=item_id)
        item.delete()
        return JsonResponse({'message': 'Item deleted successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)



