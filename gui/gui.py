import dearpygui.dearpygui as dpg
from time import sleep
from RTPWindows import TimeSeriesWindow
from functools import partial

import status_color as col
from gui_serial import Communication as Com

class Debugger:
	def __init__(self) -> None:
		self.SDAD_STATUS_BITS = 8
		self.CMD_TO_SEND = ['\x97', '\x10', '\x00'] # at startup: _REGISTER_READ_CMD
		self.com = None
		self.baudrate = 115200
		self._REGISTER_READ_CMD = ['\x97', '\x10', '\x00']
		self._SDAD_STATUS_CMD = ['\xF5', '\x00', '\x00']
		self.DEVICE_CONNECTED = False
	
	def init_gui(self) -> None:
		dpg.create_context()
		dpg.create_viewport(title='iC-MU Debug Tool')
	
		with dpg.texture_registry(show=False):
			dpg.add_dynamic_texture(width=10, height=10, default_value=col.red(), 
					tag="image_port_status_indicator")
			for i in range(8):
				dpg.add_dynamic_texture(width=10, height=10, default_value=col.red(), 
						tag=f"image_sdad_status_led_{i}")
		
		with dpg.window(tag="window_interact", label="Interact", autosize=True):
			with dpg.group(tag="group_input_port_address", horizontal=True):
				dpg.add_input_text(tag="input_port_address", default_value="/dev/ttyACM0")
				dpg.add_image(texture_tag="image_port_status_indicator")
			dpg.add_button(tag="button_connect", label="Connect", callback=self._button_connect_callback)
			dpg.add_text(tag="text_counter", label="Start")
			dpg.add_button(tag="button_sdad_status", label="SDAD STATUS", callback=self._button_sdad_status_callback)
			with dpg.group(tag="group_sdad_status_led", horizontal=True):
				for i in range(8):
					dpg.add_image(texture_tag=f"image_sdad_status_led_{i}")
			dpg.add_button(tag="button_register_read", label="RR", callback=self._button_register_read_callback)
			dpg.add_text(tag="text_reg_read", label="Nonee")
					
		self.plot = TimeSeriesWindow("plot", ["pos"])
		dpg.configure_item("plot"+"_win", pos=[250, 0])
		dpg.set_global_font_scale(1.3)

		dpg.setup_dearpygui()
		dpg.show_viewport()

	def establish_serial_com(self):
		self.port = dpg.get_value("input_port_address")
		self.com = Com()
		if(self.com.connect(port=self.port, baudrate=self.baudrate)):
			self.DEVICE_CONNECTED = True
		else:
			self.DEVICE_CONNECTED = False

	def _update_sdad_status_textures(self, data) -> None:
		for i in range(self.SDAD_STATUS_BITS):
			if data[i] == '1':
				dpg.set_value(f"image_sdad_status_led_{i}", col.green())
			else:
				dpg.set_value(f"image_sdad_status_led_{i}", col.red())

	def _update_dynamic_textures(self, status, **kwargs):
		if status == "success":
			dpg.set_value("image_port_status_indicator", col.green())
		
		elif status == "fail":
			dpg.set_value("image_port_status_indicator", col.red())
		
		elif status == "sdad_status_update":
			self._update_sdad_status_textures(kwargs["data"])

	def _sdad_status_display_update(self, data):
		# Send binary representation of data after removing base representation
		self._update_dynamic_textures("sdad_status_update", data=bin(data)[2:])

	def _button_sdad_status_callback(self, **kwargs):
		self.CMD_TO_SEND = self._SDAD_STATUS_CMD
		self.com.write(bytearray([ord(i) for i in self.CMD_TO_SEND]))
	
	def _button_register_read_callback(self, **kwargs):
		self.CMD_TO_SEND = self._REGISTER_READ_CMD
		self.com.write(bytearray([ord(i) for i in self.CMD_TO_SEND]))

	def _button_connect_callback(self, **kwargs):
		if(self.com.connect(port=dpg.get_value("input_port_address"), baudrate=self.baudrate)):
			self._update_dynamic_textures("success")
		else:
			self._update_dynamic_textures("fail")

	def _process_data_and_update_gui(self, data):
		dpg.set_value("text_counter", data)
		if data[0] == 'd':
			#plot_data_in_batch(float(data[1:]))
			self.plot.update_data([[float(data[1:])]])
		elif data[0] == 's':
			self._sdad_status_display_update(int(data[1:]))
		elif data[0] == 'p':
			dpg.set_value("text_reg_read", data[1:])
		self.plot.update_plot()

	def mainloop(self):
		while dpg.is_dearpygui_running():
			if self.DEVICE_CONNECTED is False:
				return 0 # No serial device found! Did you establish serial communication?
			
			self.com.write(bytearray([ord(i) for i in self.CMD_TO_SEND]))
			data = self.com.read_until().decode()
			print(data[:])
			self._process_data_and_update_gui(data=data)
			dpg.render_dearpygui_frame()
		
	def kill(self):
		dpg.destroy_context()
		if(self.com.close()):
			return 1 # Port closed successfully!
		else:
			return 0 # Port did not close properly!