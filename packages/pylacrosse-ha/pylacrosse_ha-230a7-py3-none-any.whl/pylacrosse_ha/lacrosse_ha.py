# Copyright (c) 2017 Heiko Thiery
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

from __future__ import unicode_literals
import logging
import re
import threading


_LOGGER = logging.getLogger(__name__)

"""
    Jeelink lacrosse firmware commands
    <n>a     set to 0 if the blue LED bothers
    <n>f     initial frequency in kHz (5 kHz steps, 860480 ... 879515)  (for RFM
    #1)
    <n>F     initial frequency in kHz (5 kHz steps, 860480 ... 879515)  (for RFM
    #2)
    <n>h     altituide above sea level
    <n>m     bits 1: 17.241 kbps, 2 : 9.579 kbps, 4 : 8.842 kbps (for RFM #1)
    <n>M     bits 1: 17.241 kbps, 2 : 9.579 kbps, 4 : 8.842 kbps (for RFM #2)
    <n>r     use one of the possible data rates (for RFM #1)
    <n>R     use one of the possible data rates (for RFM #2)
    <n>t     0=no toggle, else interval in seconds (for RFM #1)
    <n>T     0=no toggle, else interval in seconds (for RFM #2)
       v     show version
       <n>y     if 1 all received packets will be retransmitted  (Relay mode)
"""

class LaCrosse_ha(object):

    _registry = {}
    _callback = None
    _serial = None
    _stopevent = None
    _thread = None

    def __init__(self, port, baud, timeout=2):
        """Initialize the Lacrosse device."""
        self.sensors = dict()
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._serial = SerialPortFactory().create_serial_port(port)
        self._callback_data = None

    def open(self):
        """Open the device."""
        self._serial.port = self._port
        self._serial.baudrate = self._baud
        self._serial.timeout = self._timeout
        self._serial.open()
        self._serial.flushInput()
        self._serial.flushOutput()

    def close(self):
        """Close the device."""
        self._stop_worker()
        self._serial.close()

    def start_scan(self):
        """Start scan task in background."""
        self._start_worker()

    def _write_cmd(self, cmd):
        """Write a cmd."""
        self._serial.write(cmd.encode())

    @staticmethod
    def _parse_info(line):
        """
        The output can be:
        - [LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]
        - [LaCrosseITPlusReader.10.1s (RFM12B f:0 t:10~3)]
        """
        re_info = re.compile(
            r'\[(?P<name>\w+).(?P<ver>.*) ' +
            r'\((?P<rfm1name>\w+) (\w+):(?P<rfm1freq>\d+) ' +
            r'(?P<rfm1mode>.*)\)\]')

        info = {
            'name': None,
            'version': None,
            'rfm1name': None,
            'rfm1frequency': None,
            'rfm1datarate': None,
            'rfm1toggleinterval': None,
            'rfm1togglemask': None,
        }
        match = re_info.match(line)
        if match:
            info['name'] = match.group('name')
            info['version'] = match.group('ver')
            info['rfm1name'] = match.group('rfm1name')
            info['rfm1frequency'] = match.group('rfm1freq')
            values = match.group('rfm1mode').split(':')
            if values[0] == 'r':
                info['rfm1datarate'] = values[1]
            elif values[0] == 't':
                toggle = values[1].split('~')
                info['rfm1toggleinterval'] = toggle[0]
                info['rfm1togglemask'] = toggle[1]

        return info

    def get_info(self):
        """Get current configuration info from 'v' command."""
        re_info = re.compile(r'\[.*\]')

        self._write_cmd('v')
        while True:
            line = self._serial.readline()
            try:
                line = line.encode().decode('utf-8')
            except AttributeError:
                line = line.decode('utf-8')

            match = re_info.match(line)
            if match:
                return self._parse_info(line)

    def led_mode_state(self, state):
        """Set the LED mode.

        The LED state can be True or False.
        """
        self._write_cmd('{}a'.format(int(state)))

    def set_frequency(self, frequency, rfm=1):
        """Set frequency in kHz.

        The frequency can be set in 5kHz steps.
        """
        cmds = {1: 'f', 2: 'F'}
        self._write_cmd('{}{}'.format(frequency, cmds[rfm]))

    def set_datarate(self, rate, rfm=1):
        """Set datarate (baudrate)."""
        cmds = {1: 'r', 2: 'R'}
        self._write_cmd('{}{}'.format(rate, cmds[rfm]))

    def set_toggle_interval(self, interval, rfm=1):
        """Set the toggle interval."""
        cmds = {1: 't', 2: 'T'}
        self._write_cmd('{}{}'.format(interval, cmds[rfm]))

    def set_toggle_mask(self, mode_mask, rfm=1):
        """Set toggle baudrate mask.

        The baudrate mask values are:
          1: 17.241 kbps
          2 : 9.579 kbps
          4 : 8.842 kbps
        These values can be or'ed.
        """
        cmds = {1: 'm', 2: 'M'}
        self._write_cmd('{}{}'.format(mode_mask, cmds[rfm]))

    def _start_worker(self):
        if self._thread is not None:
            return
        self._stopevent = threading.Event()
        self._thread = threading.Thread(target=self._refresh, args=())
        self._thread.daemon = True
        self._thread.start()

    def _stop_worker(self):
        if self._stopevent is not None:
            self._stopevent.set()
        if self._thread is not None:
            self._thread.join()

    def _refresh(self):
        """Background refreshing thread."""

        while not self._stopevent.isSet():
            line = self._serial.readline()
            #this is for python2/python3 compatibility. Is there a better way?
            try:
                line = line.encode().decode('utf-8')
            except AttributeError:
                line = line.decode('utf-8')
            if LaCrosseSensor_ha.can_parse(line):
                
                sensor = LaCrosseSensor_ha(line)
                if sensor.sensorid in self.sensors:
                    self.sensors[sensor.sensorid].update_from(sensor)
                    sensor = self.sensors[sensor.sensorid]
                else:
                    self.sensors[sensor.sensorid] = sensor

                if self._callback:
                    self._callback(sensor, self._callback_data)

                if sensor.sensorid in self._registry:
                    for cbs in self._registry[sensor.sensorid]:
                        cbs[0](sensor, cbs[1])

    def register_callback(self, sensorid, callback, user_data=None):
        """Register a callback for the specified sensor id."""
        if sensorid not in self._registry:
            self._registry[sensorid] = list()
        self._registry[sensorid].append((callback, user_data))

    def register_all(self, callback, user_data=None):
        """Register a callback for all sensors."""
        self._callback = callback
        self._callback_data = user_data


class LaCrosseSensor_ha(object):
    """The LaCrosse Sensor Base Class"""
    re_tempsensor = re.compile('OK 9( \d+)*')
    re_weathersensor = re.compile('OK WS( \d+)*')

    def __init__(self, line=None) -> None:
        self.measurements = dict()
        if line:
            self.parse(line)

    @staticmethod
    def can_parse(line:str) -> bool:
        return LaCrosseSensor_ha.re_tempsensor.match(line) or LaCrosseSensor_ha.re_weathersensor.match(line)

    def parse(self, line:str):
        self.line = line #TODO: remove (was added just for debugging)
        #try temperature / humidity sensor
        match = self.re_tempsensor.match(line)
        if match:
            #line matches temperature sensor
            msg = [int(c) for c in match.group().split()[2:]]
            self.sensorid = msg[0]
            channel = '' if msg[1] & 0x7F == 1 else str(msg[1] & 0x7F)
            self.sensor_type = msg[1] & 0x7F
            self.new_battery = True if msg[1] & 0x80 else False
            self.low_battery = True if msg[4] & 0x80 else False
            self.update_value('temperature' + channel, float(msg[2] * 256 + msg[3] - 1000) / 10, '°C')
            if msg[4] <= 100:
                self.update_value('humidity' + channel, msg[4] & 0x7F, '%')
        match = self.re_weathersensor.match(line)
        if match:
            #line matches weather station
            msg = [int(c) for c in match.group().split()[2:]]
            msglen = len(msg)
            self.sensorid = msg[0]
            self.sensor_type = msg[1] #1=TX22, 2=NodeSensor, 3=WS1080, 4=LaCrosseGateway, 5=Universal Sensor, 6=FineOffset(WH24, WH65B, HP1000)
            if not (msg[2] == 0xFF and msg[3] == 0xFF):
                self.update_value('temperature',float(msg[2] * 256 + msg[3] - 1000) / 10,'°C')
            if msg[4] != 0xFF:
                self.update_value('humidity', msg[4], '%')
            if not (msg[5] == 0xFF and msg[6] == 0xFF):
                rain = msg[5] * 256 + msg[6]
                if self.sensor_type == 6: rain /= 10
                self.update_value('rain', rain , 'mm')
            if not (msg[7] == 0xFF and msg[8] == 0xFF):
                self.update_value('winddirection', float(msg[7] * 256 + msg[8]) / 10, '°')
            if not (msg[9] == 0xFF and msg[10] == 0xFF):
                self.update_value('windspeed', float(msg[9] * 256 + msg[10]) / 10, 'm/s')
            if not (msg[11] == 0xFF and msg[12] == 0xFF):
                self.update_value('windgust', float(msg[11] * 256 + msg[12]) / 10, 'm/s')
            if self.sensor_type != 6: 
                if msglen > 15 and not (msg[14] == 0xFF and msg[15] == 0xFF):
                    pressure = msg[14] * 256 + msg[15]
                    if pressure > 5000: pressure /= 10
                    self.update_value('pressure', pressure, 'hPa')
            else: #sensor_type = 6
                if msg[14] != 0xFF:
                    uv = msg[14]
                    uv_upper = [432, 851, 1210, 1570, 2017, 2450, 2761, 3100, 3512, 3918, 4277, 4650, 5029]
                    uv_index = 0
                    while uv_index < 13 and uv > uv_upper[uv_index]:
                        uv_index += 1
                    self.update_value('uv_index', uv_index)
                if msg[15] != 0xFF:
                    self.update_value('lux', (msg[15] * 65536 + msg[16] * 256 + msg[17])/10, 'lux')
            if msglen > 18 and not(msg[16] == 0xFF and msg[17] == 0xFF and msg[18]==0xFF):
                self.update_value('gas1', msg[16] * 65536 + msg[17] * 256 +  msg[18]) 
            if msglen > 21 and not(msg[19] == 0xFF and msg[20] == 0xFF and msg[21]==0xFF):
                self.update_value('gas2', msg[19] * 65536 + msg[20] * 256 +  msg[21]) 
            if msglen > 24 and not(msg[22] == 0xFF and msg[23] == 0xFF and msg[24]==0xFF):
                self.update_value('lux', msg[22] * 65536 + msg[23] * 256 +  msg[24], 'lux')
            if self.sensor_type == 5:
                if msglen > 25 and msg[25] != 0xFF:
                    self.update_value('version', msg[25] / 10)
                if msglen > 26 and msg[26] != 0xFF:
                    self.update_value('voltage', msg[26] / 10)
                if msglen > 29 and msg[27] != 0xFF:
                    self.update_value('debug', msg[27]*65536 + msg[28] * 256 + msg[29])
            
            self.low_battery = True if msg[13] & 0x04 else False
            self.new_battery = True if msg[13] & 0x01 else False
    
    def update_value(self, key:str, value, unit:str = '')->None:
        if key in self.measurements:
            self.measurements[key]['value']=value
        else:
            self.measurements.update({key: {'value': value, 'unit': unit}})

    def update_from(self, sensor) -> None:
            self.low_battery = sensor.low_battery
            self.new_battery = sensor.new_battery
            self.measurements.update(sensor.measurements)

    def __repr__(self) -> str:
        return '{}-->id={} type={} new_batt={} low_batt={}: {}'.format(self.line, self.sensorid, self.sensor_type, self.new_battery, self.low_battery, self.measurements)

class SerialPortFactory(object):
    def create_serial_port(self, port):
        if port.startswith("rfc2217://"):
            from serial.rfc2217 import Serial
            return Serial()
        else:
            from serial import Serial
            return Serial()

#  Temperature Sensor Format
#  
#   OK 9 56 1   4   156 37     ID = 56  T: 18.0  H: 37  no NewBatt
#   OK 9 49 1   4   182 54     ID = 49  T: 20.6  H: 54  no NewBatt
#   OK 9 55 129 4 192 56       ID = 55  T: 21.6  H: 56  WITH NewBatt 
#   OK 9 ID XXX XXX XXX XXX
#   |  | |  |   |   |   |
#   |  | |  |   |   |   --- Humidity incl. WeakBatteryFlag
#   |  | |  |   |   |------ Temp * 10 + 1000 LSB
#   |  | |  |   |---------- Temp * 10 + 1000 MSB
#   |  | |  |-------------- Sensor type (1 or 2) +128 if NewBatteryFlag
#   |  | |----------------- Sensor ID
#   |  |------------------- fix "9"
#   |---------------------- fix "OK"

# Weather Sensor format
#   OK WS 60  1   4   193 52    2 88  4   101 15  20   ID=60  21.7°C  52%rH  600mm  Dir.: 112.5°  Wind:15m/s  Gust:20m/s
#   OK WS ID  XXX TTT TTT HHH RRR RRR DDD DDD SSS SSS GGG GGG FFF PPP PPP
#   |  |  |   |   |   |   |   |   |   |   |   |   |   |   |   |-- Flags *
#   |  |  |   |   |   |   |   |   |   |   |   |   |   |   |------ WindGust * 10 LSB (0.0 ... 50.0 m/s)           FF/FF = none
#   |  |  |   |   |   |   |   |   |   |   |   |   |   |---------- WindGust * 10 MSB
#   |  |  |   |   |   |   |   |   |   |   |   |   |-------------- WindSpeed  * 10 LSB(0.0 ... 50.0 m/s)          FF/FF = none
#   |  |  |   |   |   |   |   |   |   |   |   |------------------ WindSpeed  * 10 MSB
#   |  |  |   |   |   |   |   |   |   |   |---------------------- WindDirection * 10 LSB (0.0 ... 365.0 Degrees) FF/FF = none
#   |  |  |   |   |   |   |   |   |   |-------------------------- WindDirection * 10 MSB
#   |  |  |   |   |   |   |   |   |------------------------------ Rain LSB (0 ... 9999 mm)                       FF/FF = none
#   |  |  |   |   |   |   |   |---------------------------------- Rain MSB
#   |  |  |   |   |   |   |-------------------------------------- Humidity (1 ... 99 %rH)                        FF = none
#   |  |  |   |   |   |------------------------------------------ Temp * 10 + 1000 LSB (-40 ... +60 °C)          FF/FF = none
#   |  |  |   |   |---------------------------------------------- Temp * 10 + 1000 MSB
#   |  |  |   |-------------------------------------------------- Sensor type (1=TX22IT, 2=NodeSensor, 3=WS1080)
#   |  |  |------------------------------------------------------ Sensor ID (1 ... 63)
#   |  |--------------------------------------------------------- fix "WS"
#   |------------------------------------------------------------ fix "OK"

#   * Flags: 128  64  32  16  8   4   2   1
#   |   |   |
#   |   |   |-- New battery
#   |   |------ ERROR
#   |---------- Low battery
#   */

