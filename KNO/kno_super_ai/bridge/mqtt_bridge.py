"""Simple MQTT bridge to publish/subscribe to local IoT devices.
This is optional and used by the agent to trigger local smart devices.
"""
import json
import os
from typing import Callable, Optional

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))


class MQTTBridge:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def publish(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload))

    def subscribe(self, topic: str, handler: Callable[[str, dict], None]):
        def on_message(client, userdata, message):
            try:
                payload = json.loads(message.payload.decode())
            except Exception:
                payload = message.payload.decode()
            handler(message.topic, payload)

        self.client.subscribe(topic)
        self.client.on_message = on_message
