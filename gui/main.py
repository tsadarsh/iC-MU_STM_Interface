from gui import Debugger as dbg

if __name__ == '__main__':
    ui = dbg()
    ui.init_gui()

    ui.mainloop()

    if ui.kill():
        print("Port closed")
    else:
        print("Exitied but unable to close port")