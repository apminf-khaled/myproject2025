from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Employee, EmployeeDocument
from .forms import EmployeeForm, DocumentUploadForm, ExcelUploadForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import pandas as pd
from dateutil import parser
import json

# Create your views here.
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Login attempt - Username: {username}")  # Debug print
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print("User authenticated successfully")  # Debug print
            login(request, user)
            return redirect('dashboard')  # You'll need to create this view
        else:
            print("Authentication failed")  # Debug print
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'index.html')

@login_required
def dashboard(request):
    # إحصائيات عامة
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='active').count()
    on_leave_employees = Employee.objects.filter(status='on_leave').count()
    total_documents = EmployeeDocument.objects.count()

    # بيانات الوحدات التنظيمية للرسم البياني
    org_units = Employee.objects.values('organizational_unit').distinct()
    org_unit_names = [unit['organizational_unit'] for unit in org_units if unit['organizational_unit']]
    org_unit_counts = [
        Employee.objects.filter(organizational_unit=unit['organizational_unit']).count() 
        for unit in org_units if unit['organizational_unit']
    ]

    # بيانات النشاط للرسم البياني
    today = timezone.now()
    last_30_days = [(today - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(29, -1, -1)]
    activity_data = []
    
    for date in last_30_days:
        date_obj = parser.parse(date)
        count = Employee.objects.filter(created_at__date=date_obj.date()).count()
        activity_data.append(count)

    # آخر النشاطات (آخر الموظفين المضافين والمستندات المرفوعة)
    recent_employees = Employee.objects.order_by('-created_at')[:3]
    recent_documents = EmployeeDocument.objects.order_by('-uploaded_at')[:3]
    
    # تجميع النشاطات في قائمة واحدة
    recent_activities = []
    
    for emp in recent_employees:
        recent_activities.append({
            'type': 'new_employee',
            'description': f'تم إضافة موظف جديد: {emp.name}',
            'created_at': emp.created_at,
            'url': reverse('employee_detail', args=[emp.id])
        })
    
    for doc in recent_documents:
        recent_activities.append({
            'type': 'document',
            'description': f'تم إضافة مستند جديد: {doc.title}',
            'created_at': doc.uploaded_at,
            'url': '#'
        })
    
    # ترتيب النشاطات حسب التاريخ
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:5]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_count': on_leave_employees,
        'total_documents': total_documents,
        'departments': json.dumps(org_unit_names),
        'department_counts': json.dumps(org_unit_counts),
        'activity_labels': json.dumps(last_30_days),
        'activity_data': json.dumps(activity_data),
        'recent_activities': recent_activities,
    }

    return render(request, 'dashboard.html', context)

@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الموظف بنجاح')
            return redirect('dashboard')
    else:
        form = EmployeeForm()
    
    return render(request, 'add_employee.html', {'form': form})

@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    document_form = DocumentUploadForm()
    
    context = {
        'employee': employee,
        'document_form': document_form
    }
    return render(request, 'employee_detail.html', context)

@login_required
def upload_document(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee
            document.save()
            messages.success(request, 'تم رفع المستند بنجاح')
            return redirect('employee_detail', employee_id=employee_id)
        else:
            messages.error(request, 'حدث خطأ أثناء رفع المستند')
    else:
        form = DocumentUploadForm()
    
    context = {
        'employee': employee,
        'form': form
    }
    return render(request, 'upload_document.html', context)

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(EmployeeDocument, id=document_id)
    employee_id = document.employee.id
    
    try:
        # حذف الملف الفعلي من نظام الملفات
        if document.document:
            document.document.delete(save=False)
        # حذف السجل من قاعدة البيانات
        document.delete()
        messages.success(request, 'تم حذف المستند بنجاح')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف المستند: {str(e)}')
    
    return redirect('employee_detail', employee_id=employee_id)

@login_required
def employee_list(request):
    # تحضير الاستعلام الأساسي
    queryset = Employee.objects.all()
    
    # البحث
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(employee_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(organizational_unit__icontains=search_query)
        )
    
    # فلتر الوحدة التنظيمية
    organizational_unit = request.GET.get('organizational_unit', '')
    if organizational_unit:
        queryset = queryset.filter(organizational_unit=organizational_unit)
    
    # فلتر الحالة
    status = request.GET.get('status', '')
    if status:
        queryset = queryset.filter(status=status)
    
    # الترتيب
    sort = request.GET.get('sort', 'name')
    if sort == 'employee_number':
        queryset = queryset.order_by('employee_number')
    elif sort == 'start_date':
        queryset = queryset.order_by('start_date')
    elif sort == 'evaluation_date':
        queryset = queryset.order_by('evaluation_date')
    else:
        queryset = queryset.order_by('name')
    
    # التصفح
    paginator = Paginator(queryset, 10)  # 10 موظفين في كل صفحة
    page = request.GET.get('page')
    employees = paginator.get_page(page)
    
    # الوحدات التنظيمية الفريقة للفلتر
    organizational_units = Employee.objects.values('organizational_unit').distinct()
    
    context = {
        'employees': employees,
        'organizational_units': organizational_units,
        'search_query': search_query,
    }
    
    return render(request, 'employee_list.html', context)

@login_required
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات الموظف بنجاح')
            return redirect('employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'edit_employee.html', {
        'form': form,
        'employee': employee
    })

@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    # حذف جميع المستندات المرتبطة بالموظف
    for document in employee.documents.all():
        document.document.delete()  # حذف الملف الفعلي
    
    employee.delete()
    messages.success(request, 'تم حذف الموظف وجميع مستنداته بنجاح')
    return redirect('employee_list')

@login_required
def import_employees(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # قراءة ملف Excel
                df = pd.read_excel(request.FILES['excel_file'])
                
                # طباعة أسماء الأعمدة الموجودة في الملف للتشخيص
                print("=== بداية أسماء الأعمدة ===")
                for i, col in enumerate(df.columns):
                    print(f"{i+1}. '{col}'")
                print("=== نهاية أسماء الأعمدة ===")
                
                # تنظيف أسماء الأعمدة
                df.columns = [str(col).strip().lower() for col in df.columns]
                
                print("=== أسماء الأعمدة بعد التنظيف ===")
                for i, col in enumerate(df.columns):
                    print(f"{i+1}. '{col}'")
                print("=== نهاية أسماء الأعمدة بعد التنظيف ===")
                
                # تعريف الأعمدة المطلوبة
                required_columns = {
                    'employee_number',
                    'name',
                    'educational_level',
                    'position',
                    'education_date',
                    'specialization',
                    'organizational_unit',
                    'job_class',
                    'level'
                }
                
                # التحقق من وجود الأعمدة المطلوبة وطباعة الأعمدة المفقودة
                missing_columns = []
                for col in required_columns:
                    if col not in df.columns:
                        missing_columns.append(col)
                        print(f"العمود المفقود: '{col}'")
                
                if missing_columns:
                    print("الأعمدة الموجودة في الملف:", df.columns.tolist())
                    raise ValueError(f"الأعمدة التالية غير موجودة في الملف: {', '.join(missing_columns)}")
                
                # تنظيف البيانات وتعيين قيم افتراضية للحقول الفارغة
                df = df.replace({pd.NA: None, 'nan': None, '': None})
                
                # معالجة رقم الموظف - تحويله إلى رقم صحيح
                df['employee_number'] = df['employee_number'].apply(lambda x: str(int(float(x))) if pd.notnull(x) else None)
                
                # تعيين قيم افتراضية للحقول الإلزامية إذا كانت فارغة
                df['organizational_unit'] = df['organizational_unit'].fillna('غير محدد')
                df['position'] = df['position'].fillna('غير محدد')
                df['job_class'] = df['job_class'].fillna('غير محدد')

                # تحويل التواريخ
                for date_column in ['education_date', 'evaluation_date']:
                    if date_column in df.columns:
                        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                
                # إضافة الموظفين
                success_count = 0
                error_count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        # تحضير بيانات الموظف
                        employee_data = {
                            'employee_number': str(row['employee_number']),
                            'name': row['name'],
                            'educational_level': row['educational_level'],
                            'education_date': row['education_date'].date() if pd.notna(row['education_date']) else None,
                            'position': row['position'],
                            'specialization': row['specialization'],
                            'organizational_unit': row['organizational_unit'],
                            'job_class': row['job_class'],
                            'level': str(row['level']),
                            'status': 'active'
                        }
                        
                        # إضافة الحقول الاختيارية إذا كانت موجودة
                        optional_fields = {
                            'evaluation_date': 'evaluation_date',
                            'evaluation_month': 'evaluation_month',
                            'phone': 'phone',
                            'notes': 'notes'
                        }
                        
                        for model_field, excel_field in optional_fields.items():
                            if excel_field in df.columns and pd.notna(row[excel_field]):
                                if model_field == 'evaluation_date' and pd.notna(row[excel_field]):
                                    employee_data[model_field] = pd.to_datetime(row[excel_field]).date()
                                elif model_field == 'phone':
                                    employee_data[model_field] = str(row[excel_field])
                                else:
                                    employee_data[model_field] = row[excel_field]
                        
                        # التأكد من وجود القيم الأساسية
                        if pd.isna(employee_data['employee_number']) or pd.isna(employee_data['name']):
                            raise ValueError(f"الصف {index + 2}: رقم الموظف والاسم مطلوبان")
                        
                        # إنشاء الموظف
                        Employee.objects.create(**employee_data)
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"خطأ في الصف {index + 2}: {str(e)}")
                
                # إعداد رسالة النجاح
                messages.success(request, 
                    f"تم استيراد {success_count} موظف بنجاح. "
                    f"فشل استيراد {error_count} موظف."
                )
                
                # إضافة رسائل الخطأ
                for error in errors:
                    messages.error(request, error)
                
                return redirect('employee_list')
                
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء معالجة الملف: {str(e)}")
    else:
        form = ExcelUploadForm()
    
    return render(request, 'import_employees.html', {'form': form})

@login_required
def clear_employees(request):
    if request.method == 'POST':
        try:
            # حذف جميع سجلات الموظفين
            Employee.objects.all().delete()
            messages.success(request, 'تم حذف جميع سجلات الموظفين بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف السجلات: {str(e)}')
    return redirect('employee_list')

@login_required
def reports(request):
    # إحصائيات عامة
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='active').count()
    on_leave_employees = Employee.objects.filter(status='on_leave').count()
    inactive_employees = Employee.objects.filter(status='inactive').count()
    
    # إحصائيات حسب المستوى التعليمي
    education_stats = Employee.objects.values('educational_level').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # إحصائيات حسب الوحدة التنظيمية
    unit_stats = Employee.objects.values('organizational_unit').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # إحصائيات حسب الفئة الوظيفية
    job_class_stats = Employee.objects.values('job_class').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave_employees': on_leave_employees,
        'inactive_employees': inactive_employees,
        'education_stats': education_stats,
        'unit_stats': unit_stats,
        'job_class_stats': job_class_stats,
    }
    
    return render(request, 'reports.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('login')
