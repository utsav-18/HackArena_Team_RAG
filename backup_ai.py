def backup_analysis(text):

    text = text.lower()

    if "ambulance" in text:
        return {
            "severity":"Critical",
            "type":"Medical Emergency",
            "location":"Detected",
            "hospital":"Apollo Hospital",
            "route":["A","B"],
            "corridor_required":True,
            "citizen_alert":"Emergency ambulance approaching."
        }

    if "accident" in text:
        return {
            "severity":"Critical",
            "type":"Road Accident",
            "location":"Detected",
            "hospital":"Narayana Hospital",
            "route":["A","B"],
            "corridor_required":True,
            "citizen_alert":"Accident corridor activated."
        }

    if "fire" in text:
        return {
            "severity":"High",
            "type":"Fire Emergency",
            "location":"Detected",
            "hospital":"Emergency Response Unit",
            "route":["A"],
            "corridor_required":True,
            "citizen_alert":"Fire services en route."
        }

    return {
        "severity":"Medium",
        "type":"General Emergency",
        "location":"Unknown",
        "hospital":"Nearest Hospital",
        "route":["A"],
        "corridor_required":False,
        "citizen_alert":"Stay alert."
    }