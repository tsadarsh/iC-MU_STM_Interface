import dearpygui.dearpygui as dpg
import serial
import re
from time import sleep

ser = serial.Serial(port="/dev/ttyACM0", baudrate=115200)
dpg.create_context()
dpg.create_viewport(title='iC-MU Debug Tool')

def activateCallback(sender, app_data):
	bytesSent = ser.write(b'0xF5')
	print(bytesSent)
	sleep(2)

with dpg.window(label="Interact"):
	dpg.add_text("Start", tag="tick")
	dpg.add_button(label="STATUS", tag="status", callback=activateCallback)

dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
	#ser.write(b'0xA6')
	data = ser.readline()
	print(data)
	data = str(data.decode('utf-8')[:-2])
	dpg.set_value("tick", data)
	dpg.render_dearpygui_frame()
dpg.destroy_context()

ser.close()