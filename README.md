# Smart Home with Domoticz and Raspberry Pi

## Introduction

This repository is a software and hardware source for smart home project I was working on during one month of practical training at Erasmus+, at Gut Wehlitz in Schkeuditz, Leipzig, Germany. My mentor Aran Talboys gave me a project to control the relay board with Raspberry Pi and Domoticz. The final version works through MQTT. Raspberry uses docker compose to run three services: Mosquitto MQTT broker, Domoticz smart home system and a python hardware client. Hardware client listens on Domoticz's topic and controls the GPIOs which are connected to relays on the relay board. In the current version GPIOs are not fully synced with Domoticz - if ...

## Technologies Used

- **Domoticz** (smart home system)
- **Mosquitto MQTT Broker**
- **Docker**
- **KiCad** (PCB design)

## Local setup

To run this software locally, follow these steps:

1. Clone this repository `git clone [repo url]`
2. Move to the software directory `cd software`
3. Copy .env.template file to the .env file and edit variables
4. Run `docker compose build`
