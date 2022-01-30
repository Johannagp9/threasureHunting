from sqlite3.dbapi2 import Date

from mongoengine import *
import datetime

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

class TreasureInstance(EmbeddedDocument):
    picture_found = StringField(max_length=2083)
    validated = BooleanField()

class Treasure(EmbeddedDocument):
    picture = StringField(max_length=2083)
    coordinates = StringField(max_length=1000)
    clue = StringField(max_length=5000)
    instances = ListField(EmbeddedDocumentField(TreasureInstance))

class GameInstance(Document):
    complete = BooleanField()
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)

class Game(Document):
    title = StringField(max_length=255)
    description = StringField(max_length=5000)
    picture = StringField(max_length=2083)
    location = StringField(max_length=1000)
    restart_date = DateField()
    #coordinates = ListField(FloatField)
    instances = ListField(ReferenceField(GameInstance))
    treasures = ListField(EmbeddedDocumentField(Treasure))
    creator = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    active = BooleanField()
    winner = ReferenceField(User, required=False)

class Message(EmbeddedDocument):
    message = StringField()
    sender = BooleanField()
    date = DateTimeField()
    read = BooleanField()

class Chat(Document):
    sender = ReferenceField(User, required=True)
    receiver = ReferenceField(User, required=True)
    messages = ListField(EmbeddedDocumentField(Message))


