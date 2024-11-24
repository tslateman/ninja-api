"""
URL configuration for apidemo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from typing import List
from ninja import NinjaAPI, Schema, ModelSchema
from django.shortcuts import get_object_or_404
from employees.models import Employee, Department
from pydantic import ConfigDict, Field
from decimal import Decimal


api = NinjaAPI()


class EmployeeIn(Schema):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    department: int  # ID of the department
    salary: str  # Accept string for decimal values


class EmployeeOut(Schema):
    class Config:
        from_attributes = True

    id: int
    first_name: str
    last_name: str
    department: int = Field(serialization_alias="department_id")
    salary: str


@api.post("/employees", response=EmployeeOut)
def create_employee(request, payload: EmployeeIn):
    department = get_object_or_404(Department, id=payload.department)
    employee_data = payload.dict()
    employee_data["department"] = department
    employee_data["salary"] = Decimal(employee_data["salary"])  # Convert to Decimal
    employee = Employee.objects.create(**employee_data)
    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": employee.department.id,
        "salary": str(employee.salary),
    }


@api.get("/employees/{employee_id}", response=EmployeeOut)
def get_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": employee.department.id,
        "salary": str(employee.salary),
    }


@api.get("/employees", response=List[EmployeeOut])
def list_employees(request):
    employees = Employee.objects.all()
    return [
        {
            "id": employee.id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "department": employee.department.id,
            "salary": str(employee.salary),
        }
        for employee in employees
    ]


@api.put("/employees/{employee_id}", response=EmployeeOut)
def update_employee(request, employee_id: int, payload: EmployeeIn):
    employee = get_object_or_404(Employee, id=employee_id)
    department = get_object_or_404(Department, id=payload.department)
    employee_data = payload.dict()
    employee_data["department"] = department
    employee_data["salary"] = Decimal(employee_data["salary"])  # Convert to Decimal
    for attr, value in employee_data.items():
        setattr(employee, attr, value)
    employee.save()
    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": employee.department.id,
        "salary": str(employee.salary),
    }


@api.delete("/employees/{employee_id}")
def delete_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return {"success": True}


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
]
