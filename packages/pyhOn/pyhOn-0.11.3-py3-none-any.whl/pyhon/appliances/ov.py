class Appliance:
    def __init__(self, appliance):
        self.parent = appliance

    def data(self, data):
        if data["attributes"]["lastConnEvent"]["category"] == "DISCONNECTED":
            data["attributes"]["parameters"]["temp"] = "0"
            data["attributes"]["parameters"]["onOffStatus"] = "0"
            data["attributes"]["parameters"]["remoteCtrValid"] = "0"
            data["attributes"]["parameters"]["remainingTimeMM"] = "0"

        data["active"] = data["attributes"]["parameters"]["onOffStatus"] == "1"

        if program := int(data["attributes"]["parameters"]["prCode"]):
            ids = self.parent.settings["startProgram.program"].ids
            data["programName"] = ids.get(program, "")

        return data

    def settings(self, settings):
        return settings
