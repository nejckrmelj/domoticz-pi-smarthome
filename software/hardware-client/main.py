import json
import os
import time
import re
from dotenv import load_dotenv
import paho.mqtt.client as mqtt # type: ignore
from gpiozero import LED
import requests

# env variables
load_dotenv()
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
domoticz_username = os.getenv("DOMOTICZ_USERNAME")
domoticz_password = os.getenv("DOMOTICZ_PASSWORD")
domoticz_host = os.getenv("DOMOTICZ_HOST")
domoticz_api = f"https://{domoticz_username}:{domoticz_password}@{domoticz_host}/json.htm"

# Get hardware with gpios from domoticz
hardware = {}

def update_hardware():
    global hardware

    print(f"Requesting devices from domoticz: {domoticz_api}")
    try:
        response = requests.post(domoticz_api, verify=False, params={
            "type": "command",
            "param": "getdevices"
        })
        if (response.ok):
            json = response.json()

            for led in hardware.values():
                led.close()

            for device in json["result"]:
                hardware_name = device["HardwareName"]
                status = device["Status"]
                if (device["SwitchType"] == "On/Off" and re.match(r'^GPIO \d+$', hardware_name)):
                    pin = int(hardware_name.split()[1])
                    led = LED(pin)
                    hardware[str(device["HardwareID"])] = led
                    if (status == "On"):
                        led.on()
                    else:
                        led.off()
        else:
            raise Exception(f"Request failed: {response.status_code}, api: {response.url}")
         
    except Exception as e:
        print(f"Update Hardware Error: {e}")
                
update_hardware()
print("Used hardware: ", hardware)

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe("domoticz/out")

# Handle incoming messages
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)

    match msg.topic:
        case "domoticz/out":

            if ("switchType" not in data):
                return
            
            try:
                match data["switchType"]:

                    case "On/Off":
                        hardware_idx = data["hwid"]
                        # Check if hardware gpio is initialized
                        if (hardware_idx not in hardware):
                            update_hardware()
                            if (hardware_idx not in hardware):
                                raise Exception(f"Switch with hardware idx {hardware_idx} is missing.")

                        # Switch pin state
                        led = hardware[hardware_idx]
                        led.value = data["nvalue"]
                        print(f"switching pin {led.pin.number} to {led.value}")

            except Exception as e:
                print(f"Error: {e}")


def on_log(client, userdata, level, buf):
    print(f"Log: {buf}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
# mqttc.on_log = on_log
mqttc.on_disconnect = on_disconnect

# Authentication
mqttc.username_pw_set(mqtt_username, mqtt_password)
# Connect to broker
try:
    print(f"Connecting to broker {mqtt_host}:{mqtt_port}")
    mqttc.connect(mqtt_host, mqtt_port, 60)
except Exception as e:
    print(f"Connection with broker failed: {e}")
    exit(1)

try:
    while True:
        try:
            mqttc.loop(timeout=1.0)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait before retrying
            # Reconnect if needed
            try:
                mqttc.reconnect()
            except Exception as e:
                print(f"Reconnection failed: {e}")
                time.sleep(5)

except KeyboardInterrupt:
    print("KeyboardInterrupt caught.")
except Exception as e:
    print(f"Unhandled exception: {e}")
finally:
    print("Exiting...")
