import sys


def main():

    from PyQt4 import QtGui
    import gui

    try:
        app = QtGui.QApplication(sys.argv)
        w = gui.Window()
        w.show()
        w.setFixedSize(400, 800)
    except:
        print("Failed to initialize QtGui interface")

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
