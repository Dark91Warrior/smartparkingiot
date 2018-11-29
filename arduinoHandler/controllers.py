from flask import *

arduino = Blueprint('arduino', __name__)

@arduino.route('/', methods=['GET'])
def index():
    return "Gestore dei parcheggi"


@arduino.route('/addParking', methods=['POST'])
def addParking():
    #TODO Creare Handler per aggiungere i parcheggi dei piani
    return 0


@arduino.route('/setParking', methods=['POST'])
def setParking():
    #TODO Creare Handler per settare lo stato di un parcheggio
    return 0
