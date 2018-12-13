from flask import *
from models.Parking_Model import Parking
from models.Booking_Model import Booking
from models.Test_Model import Test
from datetime import datetime
from utils.utils import publishMQTT
import time
import json
import logging


arduino = Blueprint('arduino', __name__)

@arduino.route('/', methods=['GET'])
def index():
    return "Gestore dei parcheggi"


@arduino.route('/addParking', methods=['POST'])
def addParking():
    piano = request.args.get('level')
    for i in range(1,41):
        parking = Parking()
        parking.piano = piano
        parking.number = i
        parking.put()
    return "Parcheggi piano " + str(piano) + " inseriti."


@arduino.route('/setParking', methods=['POST'])
def setParking():

    parking = request.form['parking']
    command = request.form['command']

    parking = parking.split('/')[1]
    piano = parking[0]
    numero = int(parking[1:])

    park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)[0]

    park.stato = command
    park.put()

    if command == "Occupato":
        # la prenotazione effettiva parte dal momento dell'occupazione
        prenotazione = Booking.query(Booking.parking == parking).order(-Booking.start).fetch(1)
        if len(prenotazione) > 0:
            fmt = '%Y-%m-%d %H:%M:%S'
            dat_now = datetime.now()
            datetime_str = dat_now.strftime(fmt)
            prenotazione[0].start = datetime.strptime(datetime_str, fmt)
            prenotazione[0].put()

    logging.info("Hai ricevuto il comando: " + command + ", dal parcheggio: " + parking)
    return Response(status=200)


@arduino.route('/test_attuatore', methods=['POST'])
def test_attuatore():
    parking = request.form['parking']
    parking = parking.split('/')[1]

    # se esiste un altro test lo elimino
    test = Test().query(Test.parking == parking).fetch(1)
    if len(test) > 0:
        test[0].key.delete()

    test = Test()
    test.parking = parking
    test.put()
    return Response(status=200)

@arduino.route('/attesa', methods=['POST'])
def attesa():

    parking = request.get_json()['parking']
    publishMQTT(parking, 't')

    time.sleep(5)

    fmt = '%Y-%m-%d %H:%M:%S'
    dat_now = datetime.now()
    datetime_str = dat_now.strftime(fmt)
    now = datetime.strptime(datetime_str, fmt)

    test = Test().query(Test.parking == parking).fetch(1)
    if len(test) > 0:
        if (now - test[0].last_data).total_seconds() < 300:
            return json.dumps({'controllore': 'YES', 'sensori': 'YES'})
    return json.dumps({'controllore': 'NO', 'sensori': 'NO'})
