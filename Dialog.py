from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from pic_thread import PicThread
import params
import resources


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle("Classement des images")
        self.setWindowFlags(self.windowFlags() & ~ QtCore.Qt.WindowContextHelpButtonHint);

        # stylesheet
        file = QtCore.QFile(":/resources/styles.css")
        file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        stream = file.readAll()
        self.setStyleSheet(str(stream.data(), encoding='utf-8'))

        # initialisation du thread
        self.thread = PicThread()

        # mise en place des widgets
        layout = QtWidgets.QGridLayout(self)

        hbl1 = QtWidgets.QHBoxLayout()
        browse_btn = QtWidgets.QPushButton(self)

        style = self.style()
        icon = style.standardIcon(QtWidgets.QStyle.SP_DialogOpenButton)
        browse_btn.setIcon(icon)
        browse_btn.setToolTip("Choisir le répertoire des photos ...")
        self.dir_le = QtWidgets.QLineEdit(self)
        self.dir_le.setReadOnly(True)

        hbl1.addWidget(browse_btn)
        hbl1.addWidget(self.dir_le)

        hbl2 = QtWidgets.QHBoxLayout()
        hbl2.addWidget(QtWidgets.QLabel("Décalage horaire", self))
        self.sb = QtWidgets.QSpinBox(self)
        self.sb.setMinimum(-12)
        self.sb.setMaximum(12)
        hbl2.addWidget(self.sb)

        space_item = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Fixed)
        hbl2.addSpacerItem(space_item)

        self.cbCopy = QtWidgets.QCheckBox("Copier", self)
        self.cbCopy.setCheckState(QtCore.Qt.Checked)
        hbl2.addWidget(self.cbCopy)

        self.cb = QtWidgets.QCheckBox("Modifier les données Exif", self)
        hbl2.addWidget(self.cb)

        hbl_buttons = QtWidgets.QHBoxLayout()
        hbl_buttons.setContentsMargins(5, 0, 5, 0)
        self.pb_start = QtWidgets.QPushButton(QtGui.QIcon(":/resources/start.png"),'', self)
        self.pb_stop = QtWidgets.QPushButton(QtGui.QIcon(":/resources/stop.png"),'', self)
        self.pb_stop.setEnabled(False)
        pb_quit = QtWidgets.QPushButton("Quitter", self)
        hbl_buttons.addWidget(self.pb_start)
        hbl_buttons.addWidget(self.pb_stop)
        hbl_buttons.addWidget(pb_quit)
        hbl2.addLayout(hbl_buttons)

        layout.addItem(hbl1, 0, 0, 1, 1)
        layout.addItem(hbl2, 1, 0, 1, 1)
        self.pbar = QtWidgets.QProgressBar(self)
        layout.addWidget(self.pbar, 2, 0, 1, 1)

        # signaux
        self.pb_start.clicked.connect(self.on_start)
        self.pb_stop.clicked.connect(self.thread.terminate)
        pb_quit.clicked.connect(self.reject)

        browse_btn.clicked.connect(self.on_browse_directory)
        self.sb.valueChanged.connect(lambda: self.thread.set_time_difference(self.sb.value()))
        self.cb.stateChanged.connect(lambda: self.thread.set_change_exif(self.cb.isChecked()))
        self.cbCopy.stateChanged.connect(lambda: self.thread.set_copy(self.cbCopy.isChecked()))
        self.thread.finished.connect(self.on_finished)
        self.thread.progress.connect(self.on_progress)

    def on_browse_directory(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Sélectionner le répertoire", params.DEFAULT_IMAGE_DIR,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        if dir is not None:
            self.dir_le.setText(dir)
            self.dir_le.setToolTip(dir)
            self.thread.set_directory(dir)

    def on_progress(self, value):
        self.pbar.setValue(value)

    def on_start(self):
        directory = self.dir_le.text()
        if not directory:
            return

        # comptage des fichiers
        dir = QtCore.QDir(directory)
        files = dir.entryList(["*.jpg", "*.jpeg"], QtCore.QDir.Files)
        if not len(files):
            return

        self.pbar.setMaximum(len(files))
        self.pb_start.setEnabled(False)
        self.pb_stop.setEnabled(True)

        self.thread.start()

    def on_finished(self):
        self.pbar.reset()
        self.pb_start.setEnabled(True)
        self.pb_stop.setEnabled(False)