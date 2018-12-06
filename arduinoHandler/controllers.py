from flask import *
from models.Parking_Model import Parking
import time
import json


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
    #TODO Creare Handler per settare lo stato di un parcheggio
    return 0

@arduino.route('/test_attuatore', methods=['POST'])
def test_attuatore():
    #TODO Creare Handler per settare lo stato di un parcheggio
    time.sleep(5)
    return json.dumps({'controllore': 'YES', 'sensori': 'YES'})
