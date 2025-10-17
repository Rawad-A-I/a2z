# Generated manually to remove Razorpay fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_orderitem_product_price_alter_orderitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='razorpay_order_id',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='razorpay_payment_id',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='razorpay_payment_signature',
        ),
    ]
