from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/clear/', views.clear_employees, name='clear_employees'),
    path('employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),
    path('employee/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('employee/<int:employee_id>/upload/', views.upload_document, name='upload_document'),
    path('document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('employee/import/', views.import_employees, name='import_employees'),
    path('reports/', views.reports, name='reports'),
    path('logout/', views.logout_view, name='logout'),
]
