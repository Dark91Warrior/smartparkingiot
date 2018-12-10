from google.appengine.api import urlfetch
import urllib

def publishMQTT(parking, command):
    url = "http://tools.lysis-iot.com/MqttPublish/publish.php"
    topic = "smartparking/" + parking
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = urllib.urlencode({"topic": topic, "message": command})
    res = urlfetch.fetch(url=url, method=urlfetch.POST, payload=payload, headers=headers)
    if res.status_code == 200:
        return True
    else:
        return False
