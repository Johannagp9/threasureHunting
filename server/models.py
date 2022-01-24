from django.db import models
from mongoengine import *
import datetime
# Create your models here.

def valid_date(date):
    if date > datetime.date.today():
        raise ValidationError("Invalid date.")

class User(Document):
    google_id = StringField()
    email = EmailField()
    name = StringField(max_length=40)
    birth_date = DateField(validation=valid_date)
    admin = BooleanField()

    def __str__(self):
        return self.email