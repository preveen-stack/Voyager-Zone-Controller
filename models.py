from app import db

class MotorUpdate(db.EmbeddedDocument):
    current = db.IntField()
    status = db.StringField()

class Battery(db.EmbeddedDocument):
    soc = db.FloatField()
    temp = db.FloatField()
    current = db.FloatField()
    voltage = db.FloatField()

class PV(db.EmbeddedDocument):
    voltage = db.FloatField()
    current = db.FloatField()

class Tracking(db.EmbeddedDocument):
    targetAngle = db.FloatField()
    sunAngle = db.FloatField()
    inclinometerAngle = db.FloatField()

class Misc(db.EmbeddedDocument):
    RTC = db.FloatField()
    snowDepth = db.FloatField()
    windSpeed = db.FloatField()
    ambientTemp = db.FloatField()
    boardTemp = db.FloatField()

class Led(db.EmbeddedDocument):
    power = db.StringField()
    comm = db.StringField()
    motor = db.StringField()
    mode = db.StringField()
    master = db.StringField()

class Event(db.EmbeddedDocument):
    time = db.FloatField()
    desc = db.StringField()


class UpdateData(db.Document):
    motorUpdate = db.EmbeddedDocumentField(MotorUpdate)
    battery = db.EmbeddedDocumentField(Battery)
    pv = db.EmbeddedDocumentField(PV)
    tracking = db.EmbeddedDocumentField(PV)
    misc = db.EmbeddedDocumentField(PV)
    led = db.EmbeddedDocumentField(PV)
    events = db.ListField(db.EmbeddedDocumentField(Event))


