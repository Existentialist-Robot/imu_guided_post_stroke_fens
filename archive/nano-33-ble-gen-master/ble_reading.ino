#include <ArduinoBLE.h>

#define DEBUG false
//#define TDCS_PIN 13
//connect pin 13 to the relay coil pin


// These UUIDs have been randomly generated. - they must match between the Central and Peripheral devices
// Any changes you make here must be suitably made in the Python program as well

BLEService nanoService("13012F00-F8C3-4F4A-A8F4-15CD926DA146"); // BLE Service

// BLE Characteristics - custom 128-bit UUID, read and writable by central device
BLEByteCharacteristic tdcsCharacteristic("00001101-0000-1000-8000-00805f9b34fb", BLERead | BLEWrite);

// Have a Characteristics of each of the the 9-axis - then iterate through all of them 






void setup() {
  Serial.begin(9600);
  
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);  // will turn the circuit off
  
  if (DEBUG) {
    while(!Serial);
  }

  // begin initialization
  if (!BLE.begin()) {
      Serial.println("Starting BLE failed!");
      while (1);
  }

  // set advertised local name and service UUID:
  BLE.setLocalName("Arduino Nano 33 BLE Sense");
  BLE.setAdvertisedService(nanoService);

  // add the characteristic to the service
  nanoService.addCharacteristic(tdcsCharacteristic);

  // add service
  BLE.addService(nanoService);

  // set the initial value for the characeristic:
  tdcsCharacteristic.writeValue(0);

  // start advertising
  BLE.advertise();
  delay(100);
  Serial.println("Arduino Nano BLE TDCS Peripheral Service Started");

  String address = BLE.address();
  Serial.print("Arduino Local address is: ");
  Serial.println(address);
}

void loop() {

  // listen for BLE centrals to connect:
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    // while the central is still connected to peripheral:
    while (central.connected()) {
      
      // if the remote device wrote to the characteristic,
      // use the value to control the tdcs circuit:
      if (tdcsCharacteristic.written()) {
        
        if (tdcsCharacteristic.value()) {   // any non-zero value
            Serial.println("TDCS circuit on!");
            digitalWrite(LED_BUILTIN, LOW);          // LOW will turn the circuit on
        } else {                              // a zero value
            Serial.println(F("TDCS circuit off!"));
            digitalWrite(LED_BUILTIN, HIGH);          // HIGH will turn the circuit off
        }
      }
    }

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
}