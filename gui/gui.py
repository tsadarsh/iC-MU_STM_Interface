import dearpygui.dearpygui as dpg
import serial
import re
from time import sleep

CMD_T0_SEND = 'A6'
ser = None
dpg.create_context()
dpg.create_viewport(title='iC-MU Debug Tool')

texture_data = []
for i in range(0, 10 * 10):
    texture_data.append(255)
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(255)
with dpg.texture_registry(show=False):
	dpg.add_dynamic_texture(width=10, height=10, default_value=texture_data, 
			 tag="UART_PORT_STATUS")

def _update_dynamic_textures(status):
	if status == "success":
		new_texture_data = []
		for i in range(0, 10 * 10):
			new_texture_data.append(0)
			new_texture_data.append(255)
			new_texture_data.append(0)
			new_texture_data.append(255)

		dpg.set_value("UART_PORT_STATUS", new_texture_data)
	
	if status == "fail":
		new_texture_data = []
		for i in range(0, 10 * 10):
			new_texture_data.append(255)
			new_texture_data.append(0)
			new_texture_data.append(0)
			new_texture_data.append(255)

		dpg.set_value("UART_PORT_STATUS", new_texture_data)

def restart_serial(sender, app_data):
	print("restarting...")
	print(app_data)
	global ser
	try:
		ser = serial.Serial(port=dpg.get_value("port_address"), baudrate=115200)
		_update_dynamic_textures("success")
	except serial.serialutil.SerialException:
		_update_dynamic_textures("fail")
	

def activateCallback(sender, app_data):
	CMD_T0_SEND = 'F5'
	ser.write(bytes.fromhex(CMD_T0_SEND))

	# Read until an expected sequence is found (‘\n’ by default)
	#data = ser.read_until()
	
	#print(data)
	#dpg.set_value("tick", data.decode())

with dpg.window(label="Interact"):
	dpg.add_input_text(tag="port_address", default_value="/dev/ttyACM0", callback=restart_serial)
	dpg.add_image("UART_PORT_STATUS")
	dpg.add_button(label="Connect", tag="connect", callback=restart_serial)
	dpg.add_text("Start", tag="tick")
	dpg.add_button(label="UPDATE", tag="update", callback=activateCallback)

dpg.setup_dearpygui()
dpg.show_viewport()
#dpg.start_dearpygui()
restart_serial(None, None)
while dpg.is_dearpygui_running():
	CMD_T0_SEND = 'A6'
	ser.write(bytes.fromhex(CMD_T0_SEND))
	data = ser.read_until()
	print(data)
	dpg.set_value("tick", data.decode())
	dpg.render_dearpygui_frame()
dpg.destroy_context()

ser.close()