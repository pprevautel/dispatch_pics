import sys
from PyQt5.QtWidgets import QApplication
from Dialog import Dialog


if __name__ == "__main__":
    app = app = QApplication(sys.argv)

    dlg = Dialog()
    dlg.show()

    sys.exit(app.exec_())