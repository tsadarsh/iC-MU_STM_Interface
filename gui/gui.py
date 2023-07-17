import dearpygui.dearpygui as dpg
from threading import Lock
from time import sleep
from RTPWindows import TimeSeriesWindow
from functools import partial
import pickle
from typing import List

import status_color as col
from gui_serial import Communication as Com

REGISTER_DETAILS_FILE = "./mu_1sf_driver_registers_data.pkl"

class Debugger:
	def __init__(self) -> None:
		self.SDAD_STATUS_BITS = 8
		self.CMD_TO_SEND = ['A6', '00', '00'] # at startup: _SDAD_TRANSMISSION
		self.com = None
		self.baudrate = 115200
		# TODO: Make tags into a dict, say self._spi_cmd_tags = {}
		self._tag_SDAD_TRANSMISSION = 'SDAD_TRANSMISSION'
		self._tag_SDAD_STATUS = 'SDAD_STATUS'
		self._tag_ACTIVATE = 'ACTIVATE'
		self._tag_READ_REGISTER = 'READ_REGISTER'
		self._tag_WRITE_REGISTER = 'WRITE_REGISTER'
		self._tag_REGISTER_STATUS_DATA = 'REGISTER_STATUS_DATA'
		self._SDAD_TRANSMISSION = ['A6', '00', '00'] 
		self._REGISTER_READ_CMD = ['97', '00', '00']
		self._SDAD_STATUS_CMD = ['F5', '00', '00']
		self._REGISTER_WRITE_CMD = ['D2', '00', '00']
		self._DEFAULT_CMD = self._SDAD_TRANSMISSION
		self.DEVICE_CONNECTED = False
		self.com = Com()
		self._write_lock = Lock()
		self._read_lock = Lock()
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
			dpg.add_text(tag="text_read_register", label="Nonee")
			dpg.add_input_text(tag="input_write_register")
			dpg.add_button(tag="button_write_register", label="Write", callback=self._button_write_register_callback)
			dpg.add_text(tag="text_write_register")
					
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
		with self._read_lock:
			data = self.com.read_until()
			self._process_data_and_update_gui(tag=self._tag_SDAD_STATUS, data=data)
	
	def _button_read_register_callback(self, **kwargs):
		register_name =  dpg.get_value("combo_register_select")
		self.CMD_TO_SEND = self._REGISTER_READ_CMD
		data = [] # list elements are of bytes type
		for i in range(len(self._register_details[register_name]['addr'])):
			self.CMD_TO_SEND[1] = self._register_details[register_name]['addr'][i][2:]
			print("CMD_TO_SEND (to read):", self.CMD_TO_SEND)
			with self._write_lock:
				self.com.write(bytearray(b"".join(bytes.fromhex(i) for i in self.CMD_TO_SEND)))
			with self._read_lock:
				recv = self.com.read_until()
				data.append(recv)
			print("Received:", recv)
		self._process_data_and_update_gui(tag=self._tag_READ_REGISTER,
					data=data,
					len=self._register_details[register_name]['len'],
					pos=self._register_details[register_name]['pos'])

	def _button_write_register_callback(self, **kwargs):
		register_name =  dpg.get_value("combo_register_select")
		data_tx = dpg.get_value("input_write_register").split(',')
		
		# Handle if no register is selected from combo box
		if len(register_name) == 0:
			data = f"Select register from the drop down list"
			self._process_data_and_update_gui(tag=self._tag_WRITE_REGISTER, data=data.encode())
			return
		
		if data_tx[0] == '':
			data = f"Enter data to be written"
			self._process_data_and_update_gui(tag=self._tag_WRITE_REGISTER, data=data.encode())
			return

		# Check if there is enough data provided to write
		if len(data_tx) != len(self._register_details[register_name]['addr']):
			data = f"Provide {len(self._register_details[register_name]['addr'])} comma seperated HEX values"
			self._process_data_and_update_gui(tag=self._tag_WRITE_REGISTER, data=data.encode())
			return
		
		data_rx = b''
		self.CMD_TO_SEND = self._REGISTER_WRITE_CMD
		for i in range(len(self._register_details[register_name]['addr'])):
			self.CMD_TO_SEND[1] = self._register_details[register_name]['addr'][i][2:]
			self.CMD_TO_SEND[2] = data_tx[i]
			print("CMD_TO_SEND (to write):", self.CMD_TO_SEND)
			with self._write_lock:
				self.com.write(bytearray(b"".join(bytes.fromhex(i) for i in self.CMD_TO_SEND)))
			with self._read_lock:
				data_rx += self.com.read_until()
		self._process_data_and_update_gui(
			tag=self._tag_WRITE_REGISTER,
			data=data_rx,
			kwargs={
				'len':self._register_details[register_name]['len'],
				'pos':self._register_details[register_name]['pos']
			}
		)

	def _button_connect_callback(self, **kwargs):
		if(self.com.connect(port=dpg.get_value("input_port_address"), baudrate=self.baudrate)):
			self.DEVICE_CONNECTED = True
			self._update_dynamic_textures("success")
		else:
			self.DEVICE_CONNECTED = False
			self._update_dynamic_textures("fail")

	def __process_data_for_read_register(self, data: List[bytes], pos: int, len_: int):
		# TODO: Check if STATUS byte for all is VALID
		# TODO: Test if the following logic is correct
		if len_ % 8 == 0:
			data_bin = ''
			for i in data:
				data_bin += bin(int(i.decode().rstrip().split(',')[1]))[2:]
		else:
			byte_to_modify = int(data[-1].decode().rstrip().split(',')[1])
			byte_to_modify_cleaned = ((byte_to_modify << (8 - (pos + 1))) >> (8 - (len_ % 8)))
			len_of_byte_modified = len(list(bin(byte_to_modify_cleaned)[2:]))
			modified_last_byte = '0'*((len_ % 8) - len_of_byte_modified) + bin(byte_to_modify_cleaned)[2:]
			data_bin = ''
			for i in data[:-1]:
				data_bin += bin(int(i.decode().rstrip().split(',')[1]))[2:]
			data_bin += modified_last_byte
		data_hex = hex(int(data_bin, 2))
		return data_hex

	def _process_data_and_update_gui(self, tag, data, **kwargs):
		if len(data) == 0:	
			dpg.set_value("text_counter", "No data received in the last second!")
			return
		
		# FIXME: data has inconsistent type: _tag_READ_REGISTER sends data as List[bytes] 
		# while other _tags send it as a byte-string.
		# Process data only if received
		if tag == self._tag_SDAD_TRANSMISSION:
			data = data.decode()
			self.plot.update_data([[float(data)]])
		elif tag == self._tag_SDAD_STATUS:
			data = data.decode()
			self._sdad_status_display_update(int(data))
		elif tag == self._tag_READ_REGISTER:
			data = self.__process_data_for_read_register(data, pos=int(kwargs['pos']), len_=int(kwargs['len']))
			dpg.set_value("text_read_register", data)
		elif tag == self._tag_WRITE_REGISTER:
			data = data.decode()
			#data = bin(int(data))
			dpg.set_value("text_write_register", data)

		self.plot.update_plot()
	
	def mainloop(self):
		while dpg.is_dearpygui_running():
			if self.DEVICE_CONNECTED:
				with self._write_lock:
					self.com.write(bytearray(b"".join(bytes.fromhex(i) for i in self._DEFAULT_CMD))) # TODO: Handle when connection breaks
				with self._read_lock:	
					data = self.com.read_until()
					print("mainloop recv:", data[:])
					self._process_data_and_update_gui(tag=self._tag_SDAD_TRANSMISSION, data=data)
			else:
				print("No device!")
			
			dpg.render_dearpygui_frame()
		
	def kill(self):
		dpg.destroy_context()
		if(self.com.close()):
			return 1 # Port closed successfully!
		else:
			return 0 # Port did not close properly!