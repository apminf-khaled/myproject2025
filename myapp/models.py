from django.db import models
import os
from django.utils import timezone

# Create your models here.

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('on_leave', 'في إجازة'),
    ]
    
    # المعلومات الأساسية
    employee_number = models.CharField(max_length=20, verbose_name="رقم الموظف", unique=True)
    name = models.CharField(max_length=200, verbose_name="الاسم")
    educational_level = models.CharField(max_length=100, verbose_name="المستوى التعليمي", null=True, blank=True)
    education_date = models.DateField(verbose_name="تاريخ المؤهل", null=True, blank=True)
    specialization = models.CharField(max_length=100, verbose_name="التخصص", null=True, blank=True)
    
    # معلومات الوظيفة
    position = models.CharField(max_length=100, verbose_name="الوظيفة", null=True, blank=True)
    organizational_unit = models.CharField(max_length=100, verbose_name="الوحدة التنظيمية", null=True, blank=True)
    job_class = models.CharField(max_length=100, verbose_name="الفئة", null=True, blank=True)
    level = models.CharField(max_length=50, verbose_name="المستوى", null=True, blank=True)
    
    # معلومات التقييم
    evaluation_date = models.DateField(verbose_name="تاريخ التقييم", null=True, blank=True)
    evaluation_month = models.CharField(max_length=50, verbose_name="شهر التقييم", null=True, blank=True)
    
    # معلومات الاتصال
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", null=True, blank=True)
    
    # معلومات إضافية
    notes = models.TextField(verbose_name="ملاحظات", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="الحالة")
    
    # حقول النظام
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee_number} - {self.name}"
    
    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"
        ordering = ['name']

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents', verbose_name="الموظف")
    title = models.CharField(max_length=255, verbose_name="عنوان المستند")
    document = models.FileField(upload_to='employee_documents/%Y/%m/%d/', verbose_name="الملف")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")
    
    def __str__(self):
        return f"{self.title} - {self.employee}"
    
    def filename(self):
        return os.path.basename(self.document.name)
    
    class Meta:
        verbose_name = "مستند الموظف"
        verbose_name_plural = "مستندات الموظفين"

class ArchivedFile(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان الملف")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الملف")
    file = models.FileField(upload_to='archives/%Y/%m/%d/', verbose_name="الملف")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='archived_files', verbose_name="الموظف")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")
    file_type = models.CharField(max_length=50, verbose_name="نوع الملف")
    file_size = models.IntegerField(verbose_name="حجم الملف بالبايت")

    class Meta:
        verbose_name = "ملف مؤرشف"
        verbose_name_plural = "الملفات المؤرشفة"
        ordering = ['-upload_date']

    def __str__(self):
        return self.title

    def get_file_size_display(self):
        """تحويل حجم الملف إلى صيغة مقروءة"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
