from __future__ import annotations


class SmartDevice:
    def __init__(self, name, device_type):
        self.name = name
        self.device_type = device_type
        self.is_on = False

    def toggle(self):
        self.is_on = not self.is_on
        status = "ON" if self.is_on else "OFF"
        print(f"{self.name} is now {status}.")


# Creating 'Instances' of our class
kitchen_light = SmartDevice("Kitchen Main", "Light")
living_room_ac = SmartDevice("Living Room AC", "Climate Control")

# Interacting with them
kitchen_light.toggle()  # Output: Kitchen Main is now ON.
