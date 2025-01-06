from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import datetime, time
def validate_file(value):
    # Check file extension
    valid_extensions = ['.pdf', '.png', '.jpeg', '.jpg']
    extension = value.name.split('.')[-1].lower()
    
    if f'.{extension}' not in valid_extensions:
        raise ValidationError(f"File extension not allowed. Allowed extensions are: {', '.join(valid_extensions)}")

    # Check file size (4MB limit)
    max_size = 4 * 1024 * 1024  # 4 MB in bytes
    if value.size > max_size:
        raise ValidationError("File size exceeds 4 MB limit.")


class Student_Masterfile(models.Model):
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
    ]
    # BRANCH_CHOICES = [
    #     ('1', 'MCA'),
    #     ('2', 'MBA'),
    #     ('3', 'B.TECH'),
    #     ('4', 'BCA')
    #     # (5, 'Semester 5'),
    #     # (6, 'Semester 6'),
    #     # (7, 'Semester 7'),
    #     # (8, 'Semester 8'),
    # ]
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    batch = models.CharField(max_length=10)
    branch = models.CharField(max_length=20)
    # brach = models.IntegerField(choices=BRANCH_CHOICES)
    admission_date = models.PositiveIntegerField()
    create_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    aadhar_card = models.FileField(upload_to='aadhar_cards/', null=True, blank=True, validators=[validate_file])
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    username = models.CharField(max_length=150, unique=True)
    mobile   = models.CharField(max_length=10)
    
    def save(self, *args, **kwargs):
        if not self.username:
            # Generate username based on first name, last name and registration number
            self.username = f"{self.first_name[:3].lower()}{self.registration_number[-4:]}"
        super().save(*args, **kwargs)
    
    def set_initial_password(self):
        temp_password = get_random_string(length=8)  # Create a random password
        self.set_password(temp_password)  # Hash the password and set it
        return temp_password
    
    class Meta:
        db_table = 'Student_Masterfile'
    
class Category(models.Model):
    CATEGORY_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]

    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True, default="Unknown")  # Add default value here
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES,default='')

    class Meta:
        db_table = 'Category'

    def __str__(self):
        return f"{self.category_name} ({self.get_category_type_display()})"

class Items(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    
    # Only use auto_now_add=True to set the timestamp when the record is created
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Items'

    def __str__(self):
        return self.item_name



class ItemPrice(models.Model):
    price_id = models.AutoField(primary_key=True)
    item = models.OneToOneField(Items, on_delete=models.CASCADE, related_name='item_price')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Item_Price'

    def __str__(self):
        return f"{self.item.item_name} - {self.price}"

class Transaction(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    student = models.ForeignKey(Student_Masterfile, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES)
    meal_type = models.CharField(max_length=10, choices=Category.CATEGORY_TYPES, blank=True)
    payment_done = models.BooleanField(default=False)  # New field
    item_id = models.IntegerField()
    price   = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'Transaction'

    # def save(self, *args, **kwargs):
    #     # Determine meal type based on the system's current time
    #     current_time = timezone.now().time()

    #     if time(6, 0) <= current_time < time(12, 0):  # 6:00 AM to 11:59 AM
    #         self.meal_type = 'breakfast'
    #     elif time(12, 0) <= current_time < time(18, 0):  # 12:00 PM to 5:59 PM
    #         self.meal_type = 'lunch'
    #     elif time(18, 0) <= current_time <= time(22, 0):  # 6:00 PM to 10:00 PM
    #         self.meal_type = 'dinner'
    #     else:
    #         raise ValidationError("Transactions can only be made during meal times (6 AM to 10 PM).")

    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.student.first_name} {self.student.last_name} - {self.meal_type} ({self.transaction_date.strftime('%Y-%m-%d %H:%M:%S')})"

