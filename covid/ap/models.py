from django.db import models

# Create your models here.
class District(models.Model):

    name = models.CharField(max_length=100)
    count = models.IntegerField()
    date = models.DateField()
    lcount = models.IntegerField(default=0)
    active = models.IntegerField(default=0)
    recovered = models.IntegerField(default=0)
    deceased = models.IntegerField(default=0)

class Person(models.Model):
    pid = models.IntegerField()
    age = models.IntegerField()
    gender = models.TextChoices
    locality = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    notes = models.CharField(max_length=300)
    rdate = models.DateField()

