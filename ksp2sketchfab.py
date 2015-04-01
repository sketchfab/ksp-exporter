import os
import sys

def main():

    # Params
    import ipdb

    gui_enabled = True

    from PyQt4 import QtGui
    import gui

    try:
        app = QtGui.QApplication(sys.argv)
        w = gui.Window()
        w.show()
        w.setFixedSize(400, 800)
    except:
        print("Failed to initialize QtGui interface")

        gui_enabled = False

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()