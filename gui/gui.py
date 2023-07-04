import dearpygui.dearpygui as dpg
import serial
import re

ser = serial.Serial(port="/dev/ttyACM0", baudrate=115200)
dpg.create_context()
dpg.create_viewport(title='iC-MU Debug Tool')

with dpg.window(label="Interact"):
	dpg.add_text("Start", tag="tick")

dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
	data = ser.readline()
	data = int(re.search("\d+", str(data)).group())
	dpg.set_value("tick", data)
	dpg.render_dearpygui_frame()
dpg.destroy_context()

ser.close()