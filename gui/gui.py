import dearpygui.dearpygui as dpg
import serial
from time import sleep
from RTPWindows import TimeSeriesWindow

import status_color as col

CMD_T0_SEND = 'A6'
ser = None
dpg.create_context()
dpg.create_viewport(title='iC-MU Debug Tool')

with dpg.texture_registry(show=False):
	dpg.add_dynamic_texture(width=10, height=10, default_value=col.red(), 
			 tag="image_port_status_indicator")

def _update_dynamic_textures(status):
	if status == "success":
		dpg.set_value("image_port_status_indicator", col.green())
	
	if status == "fail":
		dpg.set_value("image_port_status_indicator", col.red())

def serial_write(data):
	global ser
	ser.write(data)

def serial_read():
	global ser
	return ser.read_until()

def restart_serial(sender, app_data):
	print("restarting...")
	print(dpg.get_value("input_port_address"))
	global ser
	try:
		ser = serial.Serial(port=dpg.get_value("input_port_address"), baudrate=115200)
		_update_dynamic_textures("success")
	except serial.serialutil.SerialException:
		ser = None
		_update_dynamic_textures("fail")
	

def activateCallback(sender, app_data):
	CMD_T0_SEND = '32'
	ser.write(bytes.fromhex(CMD_T0_SEND))

with dpg.window(tag="window_interact", label="Interact", autosize=True):
	with dpg.group(tag="group_input_port_address", horizontal=True):
		dpg.add_input_text(tag="input_port_address", default_value="/dev/ttyACM0")
		dpg.add_image(texture_tag="image_port_status_indicator")
	dpg.add_button(tag="button_connect", label="Connect", callback=restart_serial)
	dpg.add_text(tag="text_counter", label="Start")
	dpg.add_button(tag="button_update", label="UPDATE", callback=activateCallback)

plot = TimeSeriesWindow("plot", ["pos"])
dpg.configure_item("plot"+"_win", pos=[250, 0])

dpg.setup_dearpygui()
dpg.show_viewport()
#dpg.start_dearpygui()
#restart_serial(None, None)
while dpg.is_dearpygui_running():
	CMD_T0_SEND = 'A6'
	if ser is not None:
		serial_write(bytes.fromhex(CMD_T0_SEND))
		data = serial_read().decode()
		print(data[1:])
		dpg.set_value("text_counter", data)
		if data[0] == 'd':
			plot.update_data([[float(data[1:])]])
	plot.update_plot()
	dpg.render_dearpygui_frame()
dpg.destroy_context()

ser.close()