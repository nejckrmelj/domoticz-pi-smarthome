import json
import os
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt # type: ignore
from gpiozero import LED

# env variables
load_dotenv()
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")

# hardware dictionary for domoticz
def load_hardware():
    with open("hardware.json") as file:
        return json.load(file)
    
hardware = load_hardware()

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe("domoticz/out")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)

    match msg.topic:
        case "domoticz/out":

            if ("switchType" not in data):
                return
            
            match data["switchType"]:

                case "On/Off":
                    pin = hardware[data["hwid"]]["gpio"]
                    led = LED(pin)
                    led.value = data["nvalue"]
                    print(f"switching pin {pin} to {led.value}")


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
