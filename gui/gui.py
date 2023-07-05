import dearpygui.dearpygui as dpg
import serial
from time import sleep
from RTPWindows import TimeSeriesWindow

import status_color as col

SDAD_STATUS_BITS = 8
CMD_T0_SEND = 'A6'
ser = None
PLOT_DATA_BATCH_SIZE = 10
plot_data_buffer = []
dpg.create_context()
dpg.create_viewport(title='iC-MU Debug Tool')

with dpg.texture_registry(show=False):
	dpg.add_dynamic_texture(width=10, height=10, default_value=col.red(), 
			 tag="image_port_status_indicator")
	for i in range(8):
		dpg.add_dynamic_texture(width=10, height=10, default_value=col.red(), 
				tag=f"image_sdad_status_led_{i}")

def _update_sdad_status_textures(data):
	for i in range(SDAD_STATUS_BITS):
		if data[i] == '1':
			dpg.set_value(f"image_sdad_status_led_{i}", col.green())
		else:
			dpg.set_value(f"image_sdad_status_led_{i}", col.red())

def _update_dynamic_textures(status, **kwargs):
	if status == "success":
		dpg.set_value("image_port_status_indicator", col.green())
	
	elif status == "fail":
		dpg.set_value("image_port_status_indicator", col.red())
	
	elif status == "sdad_status_update":
		_update_sdad_status_textures(kwargs["data"])

def serial_write(data):
	global ser
	ser.write(data)

def serial_read():
	global ser
	return ser.read_until()

def plot_data_in_batch(data):
	global plot_data_buffer, PLOT_DATA_BATCH_SIZE
	if len(plot_data_buffer) > PLOT_DATA_BATCH_SIZE:
		plot.update_data([plot_data_buffer])
		plot_data_buffer = []
	else:
		plot_data_buffer.append(data)

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
	

def sdad_status_display_update(data):
	# Send binary representation of data after removing base representation
	_update_dynamic_textures("sdad_status_update", data=bin(data)[2:])

def activateCallback(sender, app_data):
	if sender == "button_sdad_status":
		CMD_T0_SEND = 'F5'
	serial_write(bytes.fromhex(CMD_T0_SEND))

with dpg.window(tag="window_interact", label="Interact", autosize=True):
	with dpg.group(tag="group_input_port_address", horizontal=True):
		dpg.add_input_text(tag="input_port_address", default_value="/dev/ttyACM0")
		dpg.add_image(texture_tag="image_port_status_indicator")
	dpg.add_button(tag="button_connect", label="Connect", callback=restart_serial)
	dpg.add_text(tag="text_counter", label="Start")
	dpg.add_button(tag="button_sdad_status", label="SDAD STATUS", callback=activateCallback)
	with dpg.group(tag="group_sdad_status_led", horizontal=True):
		for i in range(8):
			dpg.add_image(texture_tag=f"image_sdad_status_led_{i}")
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
			#plot_data_in_batch(float(data[1:]))
			plot.update_data([[float(data[1:])]])
		elif data[0] == 's':
			sdad_status_display_update(int(data[1:]))
	plot.update_plot()
	dpg.render_dearpygui_frame()
dpg.destroy_context()

ser.close()