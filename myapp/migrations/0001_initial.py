# Generated by Django 5.1 on 2024-12-28 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='الاسم الأول')),
                ('last_name', models.CharField(max_length=50, verbose_name='اسم العائلة')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='البريد الإلكتروني')),
                ('phone', models.CharField(max_length=20, verbose_name='رقم الهاتف')),
                ('gender', models.CharField(choices=[('M', 'ذكر'), ('F', 'أنثى')], max_length=1, verbose_name='الجنس')),
                ('date_of_birth', models.DateField(verbose_name='تاريخ الميلاد')),
                ('address', models.TextField(verbose_name='العنوان')),
                ('hire_date', models.DateField(verbose_name='تاريخ التوظيف')),
                ('department', models.CharField(max_length=100, verbose_name='القسم')),
                ('position', models.CharField(max_length=100, verbose_name='المنصب')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='الراتب')),
                ('status', models.CharField(choices=[('active', 'نشط'), ('inactive', 'غير نشط'), ('on_leave', 'في إجازة')], default='active', max_length=10, verbose_name='الحالة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'موظف',
                'verbose_name_plural': 'الموظفين',
            },
        ),
    ]
