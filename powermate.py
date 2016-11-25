"""
Control Home Assistant using a Griffin PowerMate Bluetooth controller
"""
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.service import call_from_config
from homeassistant.const import ATTR_BATTERY_LEVEL
import powermate

DOMAIN = 'powermate'
_LOGGER = logging.getLogger(__name__)

CONF_ADDRESS = "address"


class PowermateController(Entity, powermate.PowermateDelegate):
    def __init__(self, hass, name, addr, actions):
        self.hass = hass
        self._name = name
        self._state = False
        self.p = powermate.Powermate(addr, self)
        self.actions = actions
        self.battery = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def should_poll(self):
        return False

    @property
    def device_state_attributes(self):
        return {ATTR_BATTERY_LEVEL: self.battery}

    def call(self, action):
        if action not in self.actions:
            return
        call_from_config(self.hass, self.actions[action], blocking=True)

    def on_connect(self):
        self._state = True
        self.update_ha_state()

    def on_disconnect(self):
        self._state = False
        self.update_ha_state()

    def on_press(self):
        self.call('press')

    def on_clockwise(self):
        self.call('clockwise')

    def on_counterclockwise(self):
        self.call('counterclockwise')

    def on_press_clockwise(self):
        self.call('press_clockwise')

    def on_press_counterclockwise(self):
        self.call('press_counterclockwise')

    def on_long_press(self, t):
        self.call('long_press_' + str(t))

    def on_battery_report(self, val):
        self.battery = val
        self.update_ha_state()


def setup(hass, config):
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    entities = []

    for name, cfg in config[DOMAIN].items():
        ent = PowermateController(hass, name, cfg['address'], cfg['actions'])
        entities.append(ent)

    if not entities:
        return False

    component.add_entities(entities)

    return True
