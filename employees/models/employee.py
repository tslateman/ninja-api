from django.db import models

from employees.models.department import Department


class Employee(models.Model):
    birthdate = models.DateField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        app_label = "employees"
