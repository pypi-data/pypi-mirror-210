
class RequestData:

    def __init__(self, event):
        json_data = event.json()
        self.data = json_data
        self.input = json_data.get("input")
        self.shots = json_data.get("shots")
        self.device_id = json_data.get("deviceId")
        self.sdk = json_data.get("sdk").lower()
        self.server_url = json_data.get("serverUrl")
