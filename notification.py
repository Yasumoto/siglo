import gi

gi.require_version('Notify', '0.7')

from gi.repository import Notify


Notify.init("Joe App")

# Create the notification object
summary = "Greetings!"
body = "How you doin?"
notification = Notify.Notification.new(
    summary,
    body, # Optional
)

# Actually show on screen
notification.show()

Notify.uninit()
