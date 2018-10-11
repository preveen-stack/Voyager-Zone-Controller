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
    timeToStow = db.FloatField()


class Led(db.EmbeddedDocument):
    power = db.StringField()
    comm = db.StringField()
    motor = db.StringField()
    mode = db.StringField()
    master = db.StringField()

class Event(db.EmbeddedDocument):
    time = db.FloatField()
    desc = db.StringField()

class Stow(db.EmbeddedDocument):
    snowStow = db.FloatField()
    windStow = db.FloatField()
    nightStow = db.FloatField()
    cleanStow = db.FloatField()

class Limits(db.EmbeddedDocument):
    east = db.FloatField()
    west = db.FloatField()

class Position(db.EmbeddedDocument):
    lat = db.FloatField()
    lng = db.FloatField()
    alt = db.FloatField()
    azimuthDeviation = db.FloatField()
    pitch_east = db.FloatField()
    pitch_west = db.FloatField()
    rowWidth = db.FloatField()

class Motor(db.EmbeddedDocument):
    trackingResolution = db.FloatField()

class ControllerInfo(db.EmbeddedDocument):
    siteName = db.StringField()
    siteID = db.StringField()
    zoneID = db.StringField()
    firmwareVersion = db.StringField()
    macID = db.StringField()
    boardSerialNo = db.StringField()
    threshold_wind_speed = db.FloatField()
    table_length = db.FloatField()
    table_width = db.FloatField()
    stow = db.EmbeddedDocumentField(Stow)
    limits = db.EmbeddedDocumentField(Limits)
    position = db.EmbeddedDocumentField(Postion)

class UpdateData(db.Document):
    trackerID = db.StringField()
    timeStamp = db.FloatField()
    motor = db.EmbeddedDocumentField(MotorUpdate)
    battery = db.EmbeddedDocumentField(Battery)
    pv = db.EmbeddedDocumentField(PV)
    tracking = db.EmbeddedDocumentField(Tracking)
    misc = db.EmbeddedDocumentField(Misc)
    led = db.EmbeddedDocumentField(Led)
    events = db.ListField(db.EmbeddedDocumentField(Event))

class SimpleUpdate(db.Document):
    angle = db.FloatField()
    pvVoltage = db.FloatField()
    batteryVoltage = db.FloatField()

class StaticData(db.Document):
    trackerID = db.StringField()
    controllerInfo = db.EmbeddedDocumentField(ControllerInfo)
    motor = db.EmbeddedDocumentField(Motor)

class XbeeDevices(db.Document):
    deviceID = db.StringField()                 #TODO will XbeeDevices collection contain only deviceID?


