import logging

import PyATEMMax
from PyATEMMax.ATEMProtocolEnums import ATEMVideoModeFormats

VIDEO_FORMATS = {
    f[1:]
    for f in dir(ATEMVideoModeFormats)
    if f.startswith('f')
}


class PyATEMSwitcher:
    def __init__(self, config):
        self.atem = PyATEMMax.ATEMMax()
        self.config = config.get('atem', {})
        self.log = logging.getLogger('Switcher')

        self._connect_subscribers = []
        self._connect_attempt_subscribers = []
        self._disconnect_subscribers = []

        self._validate_config()

        self.atem.registerEvent(
            self.atem.atem.events.connect,
            self._on_connect,
        )
        self.atem.registerEvent(
            self.atem.atem.events.connectAttempt,
            self._on_connect_attempt,
        )
        self.atem.registerEvent(
            self.atem.atem.events.disconnect,
            self._on_disconnect,
        )

    def _on_connect(self, params):
        logging.debug(f'_on_connect({repr(params)})')
        self._push_config()
        for callback in self._connect_subscribers:
            callback(params)

    def _on_connect_attempt(self, params):
        logging.debug(f'_on_connect_attempt({repr(params)})')
        for callback in self._connect_attempt_subscribers:
            callback(params)

    def _on_disconnect(self, params):
        logging.debug(f'_on_disconnect({repr(params)})')
        for callback in self._disconnect_subscribers:
            callback(params)

    def _push_config(self):
        conf = self.config.get('settings', {})

        # TODO setInputLongName
        # TODO setInputShortName
        # TODO media upload to MP1

        if 'video_mode' in self.config:
            video_mode = getattr(
                ATEMVideoModeFormats,
                'f'+self.config['video_format'],
            )
            if self.atem.videoMode.format != video_mode:
                self.atem.setVideoModeFormat(video_mode)

    def _validate_config(self):
        if 'ip' not in self.config:
            raise KeyError('Please set ATEM IP in config!')
        if (
            'video_mode' in self.config
            and self.config['video_mode'] not in VIDEO_FORMATS
        ):
            raise ValueError(
                f'ATEM video_mode {self.config["video_mode"]} '
                'is not a valid video mode, must be one of: '
                f'{", ".join(sorted(VIDEO_FORMATS))}'
            )

    def connect(self):
        self.log.info('Initiating connection to switcher')
        self.atem.connect(self.config['ip'])

    def disconnect(self):
        raise NotImplementedError

    def on_connect(self, callback):
        self._connect_subscribers.append(callback)

    def on_connect_attempt(self, callback):
        self._connect_attempt_subscribers.append(callback)

    def on_disconnect(self, callback):
        self._disconnect_subscribers.append(callback)

    def trans(self, input):
        self.log.debug(f'hehehehe trans({repr(input)})')
        self.atem.setProgramInputVideoSource(
            # TODO mixEffect,
            input,
        )
