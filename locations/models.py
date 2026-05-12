from django.db import models

class Clinic(models.Model):
    name = models.CharField(max_length=200, default="Медми")
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=200, default="9:00 - 18:00")

    class Meta:
        verbose_name = "Clinic"
        verbose_name_plural = "Clinics"

    def __str__(self):
        return self.name
