import dearpygui.dearpygui as dpg
from threading import Lock
from time import sleep
from RTPWindows import TimeSeriesWindow
from functools import partial
import pickle

import status_color as col
from gui_serial import Communication as Com

REGISTER_DETAILS_FILE = "./mu_1sf_driver_registers_data.pkl"

class Debugger:
	def __init__(self) -> None:
		self.SDAD_STATUS_BITS = 8
		self.CMD_TO_SEND = ['A6', '00', '00'] # at startup: _SDAD_TRANSMISSION
		self.com = None
		self.baudrate = 115200
		self._SDAD_TRANSMISSION = ['A6', '00', '00'] 
		self._REGISTER_READ_CMD = ['97', '00', '00']
		self._SDAD_STATUS_CMD = ['F5', '00', '00']
		self._DEFAULT_CMD = self._SDAD_TRANSMISSION
		self.DEVICE_CONNECTED = False
		self.com = Com()
		self._write_lock = Lock()
		self._register_details = ["File not found!"]
	
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
			self.__load_register_details()
			dpg.add_combo(
				tag="combo_register_select",
				items=list(self._register_details.keys())
			)
			dpg.add_button(tag="button_read_register", label="Read Register", callback=self._button_read_register_callback)
			dpg.add_text(tag="text_reg_read", label="Nonee")
					
		self.plot = TimeSeriesWindow("plot", ["pos"])
		self.port = dpg.get_value("input_port_address")
		dpg.configure_item("plot"+"_win", pos=[250, 0])
		dpg.set_global_font_scale(1.3)

		dpg.setup_dearpygui()
		dpg.show_viewport()

	def __load_register_details(self) -> None:
		# TODO: Handle if file not exits
		with open(REGISTER_DETAILS_FILE, 'rb') as f:
			self._register_details = pickle.load(f)

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
		with self._write_lock:
			self.com.write(bytearray(b"".join(bytes.fromhex(i) for i in self.CMD_TO_SEND)))
	
	def _button_read_register_callback(self, **kwargs):
		register_name =  dpg.get_value("combo_register_select")
		self.CMD_TO_SEND = self._REGISTER_READ_CMD
		for idx, addr in enumerate(self._register_details[register_name]['addr']):
			# First byte is register read command. Register addr (1 or 2 bytes) follows next.
			self.CMD_TO_SEND[idx+1] = addr[2:]
		print(self.CMD_TO_SEND)
		self.com.write(bytearray(b"".join(bytes.fromhex(i) for i in self.CMD_TO_SEND)))

	def _button_connect_callback(self, **kwargs):
		if(self.com.connect(port=dpg.get_value("input_port_address"), baudrate=self.baudrate)):
			self.DEVICE_CONNECTED = True
			self._update_dynamic_textures("success")
		else:
			self.DEVICE_CONNECTED = False
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
			if self.DEVICE_CONNECTED:
				with self._write_lock:
					self.com.write(bytearray(b"".join(bytes.fromhex(i) for i in self._DEFAULT_CMD))) # TODO: Handle when connection breaks
					data = self.com.read_until().decode()
					print(data[:])
					self._process_data_and_update_gui(data=data)
			
			else:
				print("No device!")
			
			dpg.render_dearpygui_frame()
		
	def kill(self):
		dpg.destroy_context()
		if(self.com.close()):
			return 1 # Port closed successfully!
		else:
			return 0 # Port did not close properly!