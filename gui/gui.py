import dearpygui.dearpygui as dpg
import serial
import re
from time import sleep
CMD_T0_SEND = 'A6'
ser = serial.Serial(port="/dev/ttyACM0", baudrate=115200)
dpg.create_context()
dpg.create_viewport(title='iC-MU Debug Tool')

def activateCallback(sender, app_data):
	CMD_T0_SEND = 'A6'
	ser.write(bytes.fromhex(CMD_T0_SEND))

	# Read until an expected sequence is found (‘\n’ by default)
	data = ser.read_until()
	
	print(data)
	dpg.set_value("tick", data.decode())

with dpg.window(label="Interact"):
	dpg.add_text("Start", tag="tick")
	dpg.add_button(label="UPDATE", tag="update", callback=activateCallback)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
# while dpg.is_dearpygui_running():
# 	#ser.write(bytes.fromhex(CMD_T0_SEND))
# 	#CMD_T0_SEND = 'A6'
# 	data = ser.readline()
# 	print(data)
# 	#data = str(data.decode('utf-8')[:-2])
# 	#dpg.set_value("tick", data)
# 	dpg.render_dearpygui_frame()
dpg.destroy_context()

ser.close()