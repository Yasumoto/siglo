import gatt

import gi.repository.GLib as glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from .bluetooth import InfiniTimeManager, InfiniTimeDevice, NoAdapterFound
from .config import config


class daemon:
    def __init__(self):
        self.conf = config()
        self.manager = InfiniTimeManager()
        self.device = InfiniTimeDevice(manager=self.manager, mac_address="f9:e1:91:0f:b8:11") #self.conf.get_property("last_paired_device"))
        self.device.connect()

    def scan_for_notifications(self):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus.add_match_string_non_blocking(
            "eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'"
        )
        bus.add_message_filter(self.notifications)
        mainloop = glib.MainLoop()
        mainloop.run()

    def notifications(self, bus, message):
        alert_dict = {}
        print("Got notification, I think!")
        print(message)
        repr(message)
        for arg in message.get_args_list():
            print(f"Printing arg: {arg}")
            repr(f"repr of arg: {arg}")
            if isinstance(arg, dbus.Dictionary):
                print(arg.keys())
                if arg["desktop-entry"] == "sm.puri.Chatty":
                    alert_dict["category"] = "SMS"
                    alert_dict["sender"] = message.get_args_list()[3].split("New message from ")[1]
                    alert_dict["message"] = message.get_args_list()[4]
            else:
                arg_type = type(arg)
                print(f"Type: {arg_type}")
                if str(arg) == "Joe App":
                    print("Creating message to send to watch")
                    alert_dict["category"] = "SMS"
                    alert_dict["sender"] = "Myself"
                    alert_dict["message"] = "gimmeh"
                    print(f"Updated dict: {alert_dict}")
                    break
        print(f"Alert Dict after processing: {alert_dict}")
        if len(alert_dict) > 0:
            print(f"Sending: {alert_dict}")
            self.device.send_notification(alert_dict)
            print("Sent!")
        else:
            print(f"Alert dict was supposedly 0: {alert_dict}")
