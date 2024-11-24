import pytest
from django.test import Client
from employees.models import Employee, Department
from django.urls import reverse
from decimal import Decimal


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def department():
    return Department.objects.create(name="Engineering")


@pytest.fixture
def sample_employee(department):
    employee = Employee.objects.create(
        first_name="John",
        last_name="Doe",
        department=department,
        salary=Decimal("75000.00"),
    )
    return employee


@pytest.mark.django_db
class TestEmployeeEndpoints:
    def test_list_employees(self, client, department):
        # Create test employees
        Employee.objects.create(
            first_name="John",
            last_name="Doe",
            department=department,
            salary=Decimal("75000.00"),
        )
        Employee.objects.create(
            first_name="Jane",
            last_name="Smith",
            department=department,
            salary=Decimal("65000.00"),
        )

        response = client.get("/api/employees")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["first_name"] == "John"
        assert data[0]["department"] == department.id
        assert Decimal(data[0]["salary"]) == Decimal("75000.00")
        assert data[1]["first_name"] == "Jane"
        assert data[1]["department"] == department.id
        assert Decimal(data[1]["salary"]) == Decimal("65000.00")

    def test_get_employee(self, client, sample_employee):
        response = client.get(f"/api/employees/{sample_employee.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["department"] == sample_employee.department.id
        assert Decimal(data["salary"]) == Decimal("75000.00")

    def test_get_nonexistent_employee(self, client):
        response = client.get("/api/employees/999")
        assert response.status_code == 404

    def test_create_employee(self, client, department):
        payload = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "department": department.id,
            "salary": "70000.00",
        }
        response = client.post(
            "/api/employees", payload, content_type="application/json"
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["first_name"] == "Alice"
        assert data["last_name"] == "Johnson"
        assert data["department"] == department.id
        assert Decimal(data["salary"]) == Decimal("70000.00")

        # Verify employee was created
        created_employee = Employee.objects.get(id=data["id"])
        assert created_employee.first_name == "Alice"
        assert created_employee.last_name == "Johnson"
        assert created_employee.salary == Decimal("70000.00")

    def test_create_employee_invalid_data(self, client):
        payload = {
            "first_name": "Alice"  # Missing required fields
        }
        response = client.post(
            "/api/employees", payload, content_type="application/json"
        )
        assert response.status_code == 422  # Validation error

    def test_update_employee(self, client, sample_employee, department):
        payload = {
            "first_name": "Johnny",
            "last_name": "Doe",
            "department": department.id,
            "salary": "80000.00",
        }
        response = client.put(
            f"/api/employees/{sample_employee.id}",
            payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Johnny"
        assert Decimal(data["salary"]) == Decimal("80000.00")

        # Verify employee was updated
        updated_employee = Employee.objects.get(id=sample_employee.id)
        assert updated_employee.first_name == "Johnny"
        assert updated_employee.salary == Decimal("80000.00")

    def test_update_nonexistent_employee(self, client, department):
        payload = {
            "first_name": "Johnny",
            "last_name": "Doe",
            "department": department.id,
            "salary": "80000.00",
        }
        response = client.put(
            "/api/employees/999", payload, content_type="application/json"
        )
        assert response.status_code == 404

    def test_delete_employee(self, client, sample_employee):
        response = client.delete(f"/api/employees/{sample_employee.id}")
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify employee was deleted
        assert not Employee.objects.filter(id=sample_employee.id).exists()

    def test_delete_nonexistent_employee(self, client):
        response = client.delete("/api/employees/999")
        assert response.status_code == 404
