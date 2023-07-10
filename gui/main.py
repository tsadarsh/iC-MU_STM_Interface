from gui import Debugger as dbg

if __name__ == '__main__':
    ui = dbg()
    ui.init_gui()
    ui.establish_serial_com()
    if ui.DEVICE_CONNECTED:
        ui.mainloop()
    else:
        print("No device")
    ui.kill()