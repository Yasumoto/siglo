#!/usr/bin/python3

import datetime

import dbus
import gatt

manager = gatt.DeviceManager(adapter_name='hci0')

class PineTime(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def characteristic_write_value_succeeded(self, characteristic):
        super().characteristic_write_value_succeeded(characteristic)
        print(f"Woo! wrote correctly: {characteristic}")

    def characteristic_write_value_failed(self, error):
        super().characteristic_write_value_failed(error)
        print(f"Bad news, write failed: {error}")

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))

        current_time_service = next(
            s for s in self.services
            if s.uuid == '00001805-0000-1000-8000-00805f9b34fb')

        current_time_characteristic = next(
            c for c in current_time_service.characteristics
            if c.uuid == '00002a2b-0000-1000-8000-00805f9b34fb')

        current_time = current_time_characteristic.read_value()

        print(f"Current time in bytes: {current_time}")
        year = int.from_bytes(current_time[:2], "little")
        month = int(current_time[2])
        day = int(current_time[3])
        hour = int(current_time[4])
        minute = int(current_time[5])
        seconds = int(current_time[6])
        weekday = int(current_time[7])
        fractions_1_256th_of_a_second = int(current_time[8])

        ints = [int(v) for v in current_time[2:]]


        watch_current_time = datetime.datetime(year, month, day, hour, minute, seconds)

        print(f"Current time on the watch: {watch_current_time}")

        now = datetime.datetime.now()

        def year_to_bytes(year):
            byte_list = year.to_bytes(2, "little")
            now_year = dbus.Array([dbus.Byte(byte) for byte in byte_list])
            return now_year

        assert dbus.Array([dbus.Byte(178), dbus.Byte(7)]) == year_to_bytes(1970)

        now_bytes = year_to_bytes(now.year) + dbus.Array([dbus.Byte(now.month), dbus.Byte(now.day), dbus.Byte(now.hour), dbus.Byte(now.minute), dbus.Byte(now.second), dbus.Byte(now.isoweekday()), 0])
        print(now_bytes)

        current_time_characteristic.write_value(now_bytes)


#  <lsb of year> <msb of year> <month (1-12)> <day (1-31)> <hour (0-23)> <minute (0-59)> <seconds (0-59)> <weekday (1-7 where 1=Monday)> <fractions (1/256th of second)>
# https://wiki.pine64.org/wiki/PineTime_FAQ#How_do_I_set_the_time_on_PineTime.3F

#Primary Service (Handle 0x1920)
#	/org/bluez/hci0/dev_F9_E1_91_0F_B8_11/service0017
#	00001805-0000-1000-8000-00805f9b34fb
#	Current Time Service

# select-attribute /org/bluez/hci0/dev_F9_E1_91_0F_B8_11/service0017/char0018
#Characteristic (Handle 0xf004)
#	/org/bluez/hci0/dev_F9_E1_91_0F_B8_11/service0017/char0018
#	00002a2b-0000-1000-8000-00805f9b34fb
#	Current Time


device = PineTime(mac_address='F9:E1:91:0F:B8:11', manager=manager)
device.connect()

manager.run()
