# Generated by Django 4.2.17 on 2024-12-30 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_transaction_category_transaction_meal_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='item_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
