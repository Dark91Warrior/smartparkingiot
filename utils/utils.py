from google.appengine.api import urlfetch
import urllib

"""
Funzioni varie.
"""

# funzione di publish sul broker (dove staranno in ascolto gli arduino)
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
