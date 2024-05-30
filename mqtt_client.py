import json
import os
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt # type: ignore
from gpiozero import LED
import requests
import re

# env variables
load_dotenv()
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
domoticz_username = os.getenv("DOMOTICZ_USERNAME")
domoticz_password = os.getenv("DOMOTICZ_PASSWORD")
domoticz_host = os.getenv("DOMOTICZ_HOST")
domoticz_api = f"http://{domoticz_username}:{domoticz_password}@{domoticz_host}/json.htm"

# Get hardware with gpios from domoticz   
def get_hardware():
    print("Requesting devices from domoticz")
    response = requests.post(domoticz_api, params={
        "type": "command",
        "param": "getdevices"
    })
    hardware = {}
    if (response.ok):
        json = response.json()
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
                
    return hardware
                
hardware = get_hardware()
print("Used hardware: ", hardware)

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe("domoticz/out")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)

    match msg.topic:
        case "domoticz/out":

            if ("switchType" not in data):
                return
            
            try:
                match data["switchType"]:

                    case "On/Off":
                        # pin = hardware[data["hwid"]]["gpio"]
                        # led = LED(pin)
                        # led.value = data["nvalue"]
                        led = hardware[data["hwid"]]
                        led.value = data["nvalue"]
                        print(f"switching pin {led.pin.number} to {led.value}")
            except:
                print("There was an error")


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

mqttc.username_pw_set(mqtt_username, mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

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
