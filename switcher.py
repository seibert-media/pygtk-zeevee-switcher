import logging

import paho.mqtt.client as mqtt


class ZeeveeSwitcher:
    def __init__(self, config):
        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.config = config.get("mqtt", {})
        self.log = logging.getLogger("ZeeVee")

        self._connect_subscribers = []
        self._disconnect_subscribers = []
        self._receive_subscribers = []

        self.mqtt.on_connect = self._on_connect
        self.mqtt.on_disconnect = self._on_disconnect
        self.mqtt.on_message = self._on_receive

    def _on_connect(self, client, userdata, flags, rc, properties):
        self.log.debug(f'_on_connect({client!r}, {userdata!r}, {flags!r}, {rc!r}, {properties!r})')
        self.mqtt.subscribe(self.config['state_topic'])
        for callback in self._connect_subscribers:
            callback(rc)

    def _on_disconnect(self, client, userdata, flags, rc, properties):
        self.log.debug(f'_on_disconnect({client!r}, {userdata!r}, {flags!r}, {rc!r}, {properties!r})')
        for callback in self._disconnect_subscribers:
            callback(rc)

    def _on_receive(self, client, userdata, msg):
        self.log.debug(f'_on_receive({client!r}, {userdata!r}, {msg!r})')
        for callback in self._receive_subscribers:
            callback(msg.payload.decode().strip())

    def connect(self):
        self.log.info("initiating connection to MQTT server")
        if self.config.get('username') and self.config.get('password'):
            self.mqtt.username_pw_set(self.config['username'], self.config['password'])
        self.mqtt.connect(self.config['host'], self.config.get('port', 1883), 60)
        self.mqtt.loop_start()
        self.log.info('connection active')

    def disconnect(self):
        self.log.info('got disconnect info')
        self.mqtt.loop_stop()
        self.mqtt.disconnect()

    def on_connect(self, callback):
        self._connect_subscribers.append(callback)

    def on_disconnect(self, callback):
        self._disconnect_subscribers.append(callback)

    def on_receive(self, callback):
        self._receive_subscribers.append(callback)

    def trans(self, input):
        self.log.debug(f"trans({repr(input)})")
        try:
            self.mqtt.publish(self.config['command_topic'], input)
        except Exception:
            self.log.exception('could not change input')
