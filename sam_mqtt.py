#sam_mqtt.py

import paho.mqtt.client as mqtt
import time

class Publisher(mqtt.Client):

	def __init__(self):
		mqtt.Client.__init__(self)
		self.connect("172.16.0.1", 1883, 60)

	def push_estimate(self, kaff, wate, cola):
		kaff_str = str(kaff)
		wate_str = str(wate)
		cola_str = str(cola)
		#self.publish("/PIT_Hackathon/MateTracker/estimate", "Kaffee Reserven sind aufgebraucht in " + kaff_str + " Minuten; Wasser Reserven sind aufgebrauch in " + wate_str + " Minuten; Cola Reserven sind aufgebrauch in " + cola_str + " Minuten.")
		#self.publish("/PIT_Hackathon/MateTracker/estimate", kaff_str + ";" + wate_str + ";" + cola_str)
		#self.publish("/PIT_Hackathon/MateTracker/estimate", 1)
		self.publish("/PIT_Hackathon/MateTracker/estimate", wate_str)
		time.sleep(1)
		self.publish("/PIT_Hackathon/MateTracker/estimate", cola_str)
		time.sleep(1)
		self.publish("/PIT_Hackathon/MateTracker/estimate", kaff_str)
		#self.publish("/PIT_Hackathon/MateTracker/estimate", "Wackelkontakt")

#publisher = Publisher()
#publisher.push_estimate(80, 170, 4816)