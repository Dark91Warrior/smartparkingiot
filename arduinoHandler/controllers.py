from flask import *
from models.Parking_Model import Parking
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
    parking = request.args.get('parking')
    command = request.args.get('command')

    piano = parking[0]
    numero = int(parking[1:])

    park = Parking().query(Parking.piano == piano, Parking.number == numero).fetch(1)[0]

    park.stato = command

    logging.info("Hai ricevuto il comando: " + command + ", dal parcheggio: " + parking.split('/')[1])
    return Response(status=200)


@arduino.route('/test_attuatore', methods=['POST'])
def test_attuatore():
    #TODO Creare Handler per testare lo stato di un parcheggio
    time.sleep(5)
    return json.dumps({'controllore': 'YES', 'sensori': 'YES'})
