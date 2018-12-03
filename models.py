from app import db


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


class ControllerInfo(db.EmbeddedDocument):
    siteName = db.StringField()
    siteID = db.StringField()
    zoneID = db.StringField()
    rowID = db.StringField()
    firmwareVersion = db.StringField()
    boardSerialNo = db.IntField()
    threshold_wind_speed = db.FloatField()
    table_length = db.FloatField()
    table_width = db.FloatField()
    stow = db.EmbeddedDocumentField(Stow)
    limits = db.EmbeddedDocumentField(Limits)
    position = db.EmbeddedDocumentField(Position)

class Coordinates(db.EmbeddedDocument):
    x = db.IntField()
    y = db.IntField()

class Parameter(db.EmbeddedDocument):
    name = db.StringField()
    coordinates = db.EmbeddedDocumentListField(Coordinates)

class Trackers(db.EmbeddedDocument):
    trackerId = db.StringField()
    parameters = db.EmbeddedDocumentListField(Parameter)

class TrendsData(db.EmbeddedDocument):
        zoneId = db.StringField()
        numberOfTrackers = db.StringField()
        trackers = db.EmbeddedDocumentListField(Trackers)
        operationalNo = db.StringField()
"""
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
    meta = {'collection': 'update_data'}
"""
class PowerTable(db.Document):
    trackerID = db.StringField()
    timeStamp = db.StringField()
    pvCurrent = db.StringField()
    pvVoltage = db.StringField()
    batteryCurrent = db.StringField()
    batteryVoltage = db.StringField()
    meta = {'collection': 'powerTable'}

class StatusTable(db.Document):
    trackerID = db.StringField()
    timeStamp = db.StringField()
    currentMode = db.StringField()
    currentAngle = db.FloatField()
    motor = db.StringField()
    errorCode = db.StringField()
    calculatedAngle = db.FloatField()
    meta = {'collection': 'statusTable'}

class SimpleUpdate(db.Document):
    angle = db.FloatField()
    pvVoltage = db.FloatField()
    batteryVoltage = db.FloatField()

class StaticData(db.Document):
    trackerID = db.StringField(unique=True)
    deviceID = db.StringField(unique=True)
    controllerInfo = db.EmbeddedDocumentField(ControllerInfo)
    discovered = db.BooleanField(default=False)
    meta = {'collection': 'static_data'}

class XbeeDevices(db.Document):
    deviceID = db.StringField()
    trackerID = db.StringField()
    meta = {'collection': 'xbeeDevices'}

class Trends(db.Document):
    trendsData = db.EmbeddedDocumentListField(TrendsData)
    meta = {'collection': 'trends'}

class Wifi(db.Document):
    ssid = db.StringField()
    password = db.StringField()
    meta = {'max_documents': 1, 'max_size': 200}