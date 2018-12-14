/*
 * Smart Parking Arduino
 * Luca Puggioninu
 * Claudio Marche
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <PubSubClient.h>
#include <Ultrasonic.h>

// Dati per il collegamento a una rete

const char* ssid = "MacBook Pro di Claudio";     // Identificativo della rete
const char* password = "ciaone92";               // Password della rete
const char* mqtt_server = "34.216.156.87";       //"http://tools.lysis-iot.com";

/*
 * Variabili del sensore a ulrauoni
 */
const int trigPin = 2;  // D4 del NodeMCU. Pin del Trigger 
const int echoPin = 0;  // D3 del NodeMCU. Pin dell'Echo
// Definisco le variabili del tempo di ritorno e della distanza del sensore a ultrasuoni
long duration;
int  distance;
int  tempo = 0;         // Variabile per il controllo dei tempi del parcheggio
char p;                 // Variabile per contenere il carattere di prenotazione o di test

/* 
 * Gestisco il sensore magnetico
 */
int magneticPin = 5 ;  // Pin per il sensore magnetico (D1)
int val;               // Definisco un valore numerico per leggere dal del sensore magnetico

int ledPin      = 14;  // LedPin D5 per segnalare la connessione

/************************************
 * Inizializzo un nuovo client MQTT *
 ************************************/
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

/*****************************************
 * Funzione per la connessione al router *
 *****************************************/
void setup_wifi()
{
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite (ledPin, HIGH);        // Accendo il led per vedere se la connessione è avvenuta con successo
}

/***********************************************************************
 * Gestisco la funzione per ascoltare il server e ricevere la risposta *
 ***********************************************************************/
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
    p = (char)payload[i];                // Ricevo il carattere dal nostro server ('p' indicherà la prenotazione e 't' il test)
  }
  Serial.println();
  Serial.print("Carattere = ");
  Serial.print  (p);  

 // Se il carattere ricevuto è 'p' allora faccio partire la funzione relativa alla prenotazione del parcheggio
  if (p == 'p')
  {
    int counter    = 0;
    int controllo  = 1;     // Controllo per il while che gestirà la prenotazoione del parcheggio
    int controllo2 = 1;
    int flag = 1;           // Controllo per il conteggio dei secondi durante il parcheggio 
  // Inizio il conteggio dei minuti da quando la macchina è ferma
    while(controllo == 1)
    {
      tempo = millis();
      distance = distanza();       // Leggo la distanza dal sensore a ultrasuoni
      val = digitalRead (magneticPin); // Leggo il valore del sensore magnetico
   // Serie di stampe per vedere se va tutto bene
      Serial.println("Sono entrato nel controllo == 1");
      Serial.print("Millisecondi: ");
      Serial.println(millis());
      Serial.print("Distance: ");
      Serial.println(distance);
      Serial.print("Sensore magnetico: ");
      Serial.println(val);
// Controllo dei sensori quando l'auto entra nel parcheggio
      while((distance < 10 || val == LOW) && controllo2 == 1)
      {
        distance = distanza();
        val = digitalRead (magneticPin);
        if (millis() - tempo >= 30000 && flag == 1) // Conto 30 secondi che potrebbero servire per parcheggiare
        {
          Serial.println("Il parcheggio e' stato occupato");
          sendtoServer(topic, "Occupato");          // Invio al server che il parcheggio è occupato
          tempo = millis();                         // Azzero il timer
          flag  = 0;                                // Azzero il flag per inviare una singola risposta al server
        }
        else if (distance >= 10 && val == HIGH && flag == 0) // Vedo se si libera il parcheggio
        { 
          sendtoServer(topic, "Libero");     // Invio al server che il parcheggio è libero
          Serial.println("Il parcheggio e' stato liberato");
          controllo  = 0;                            // Azzero il controllo ed esco dal ciclo
          controllo2 = 0;
        }
        delay(1000);
      }
      delay(1000);
      if (counter > 900)
      {
        sendtoServer(topic, "Libero");     // Invio al server che il parcheggio è libero
        controllo = 0;
      }
        
      counter++;
    }
  }
// Se invece il carattere inviato dal server è 't' allora invio una risposta al server per confermare che l'arduino è acceso e operativo
// Qualora l'arduino fosse spento, l'applicazione web mostrerà un messaggio di errore
  else if (p == 't')
  {
    testToServer(topic);              // Invio al server il topic per il test
  }
}

// Funzione di riconnessione qualora il dispositivo non riesca a connettersi
void reconnect() {
  // Ciclo fino a quando l'arduino non si connette
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // ... and resubscribe
      client.subscribe("smartparking/#");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(ledPin, OUTPUT);      // Definisco il led che segnalerà l'avvenuta connessione
  pinMode(magneticPin, INPUT) ; // Definisco il pin del sensore magnetico come input
  pinMode(trigPin, OUTPUT);     // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);      // Sets the echoPin as an Input
  Serial.begin(9600);
  setup_wifi();                 // Inizializzo la connessione al WiFi
  client.setServer(mqtt_server, 1883);  // Indirizzo e porta del server MQTT
  client.setCallback(callback);         // Callback del server MQTT
}

// Ciclo (cerco di riconnettermi) che il client non è connesso
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  delay(1000);
  client.loop();
}

/**************************************************************************************
 * Funzione per inviare dati al server MQTT. Nel nostro caso invierà l'identificativo * 
 * del parcheggio utilizzato e se questo è stato "occupato" o "liberato"              *
 **************************************************************************************/
void sendtoServer(String parking, String comando)
{
  HTTPClient http;    // Dichiaro l'oggetto della classe HTTPClient

  String postData;    // Conterrà la stringa che manderò al server

  postData = "parking=" + parking + "&command=" + comando;

  http.begin("http://smartparking-iot.appspot.com/arduino/setParking"); // Specifico la destinazione della richiesta...
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");  // ...e il tipo di contenuto

  int httpCode = http.POST(postData);   // Invio la richiesta HTTP (POST)
  Serial.println("Inviata richiesta di modifica parcheggio, con codice: ");
  Serial.println(httpCode);             // Stampo il codice restituito dalla richiesta HTTP  
  Serial.println("");
  
  http.end();                           // Chiudo la connessione
}

/*********************************************************************************
 * Funzione di test per controllare che l'arduino sia connesso. Il funzionamento *
 * è lo stesso della sendtoServer ma in questo caso mando solo "parking"         *
 *********************************************************************************/
void testToServer(String parking)
{
  HTTPClient http;

  String postData;

  postData = "parking=" + parking;

  http.begin("http://smartparking-iot.appspot.com/arduino/test_attuatore");
  http.addHeader("Content-Type", "application/x-www-form-urlencoded"); 

  int httpCode = http.POST(postData);
  Serial.println("Inviata richiesta di modifica parcheggio, con codice: ");
  Serial.println(httpCode);  
  Serial.println("");
  
  http.end();
}

/*************************************
 * Gestione del sensore a ultrasuoni *
 *************************************/
int distanza()
{
  int distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
// Setto il pin del trigger su "HIGH" per 10 microsecondi
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
// Leggo dal pin dell'echo il quale restituisce il tempo di ritorno dell'onda sonora in microsecondi
  duration = pulseIn(echoPin, HIGH);
  
// Calcolo la distanza
  distance = duration*0.034/2;
  return distance;
}
