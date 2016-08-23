import sys
import gui
from PyQt5.QtWidgets import *

def main():
    try:
        app = QApplication(sys.argv)
        w = gui.Window()
        w.show()
    except Exception as e:
        print(e)
        print("Failed to initialize QtGui interface")
        return

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
