class PatientLocation:
    def __init__(self, latitude: float, longitude: float, prefers_delivery: bool):
        self.latitude = latitude
        self.longitude = longitude
        self.prefers_delivery = prefers_delivery