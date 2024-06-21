# Smart Home with Domoticz and Raspberry Pi

## Introduction

This repository is a software and hardware source for a smart home project I was working on during one month of practical training at Erasmus+, at Gut Wehlitz in Schkeuditz, Leipzig, Germany. My mentor Aran Talboys gave me a project to control the relay board with Raspberry Pi and Domoticz. The final version works through MQTT. Raspberry uses docker compose to run three services: Mosquitto MQTT broker, Domoticz smart home system and a python hardware client. Hardware client listens on Domoticz's topic and controls the GPIOs which are connected to relays on the relay board. In the current version GPIOs are not fully synced with Domoticz - if GPIO is changed by some other program, change is not reflected by the hardware client.

## Technologies Used

- **Domoticz** (smart home system)
- **MQTT**
- **Docker**

## Local setup

To run this software locally, follow these steps:

1. Clone this repository `git clone [repo url]`

2. Move to the software directory `cd software`

3. Copy .env.template file to the .env file and edit variables

4. Build and run app with `docker compose build` and `docker compose up`

5. Go to [http://localhost:8080/](http://localhost:8080/) or [https://localhost:443/](https://localhost:443/)

6. On Domoticz add hardware with type _MQTT Client Gateway with LAN interface_, remote address _mosquitto_ and username and password from you .env file

7. Add new hardware for every useful GPIO on the Raspberry Pi with name _GPIO [pin number]_ and type _Dummy (Does nothing, use for virtual switches only_

8. Add switches with hardware _GPIO [pin number]_ with any type and name
