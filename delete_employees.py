import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Employee

# Delete all employees
Employee.objects.all().delete()
print("تم حذف جميع سجلات الموظفين بنجاح")
