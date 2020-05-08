from datetime import datetime, timedelta
import os
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
import piexif
import shutil
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

        spaceItem = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Fixed)
        hbl2.addSpacerItem(spaceItem)

        self.cbCopy = QtWidgets.QCheckBox("Copier", self)
        self.cbCopy.setCheckState(QtCore.Qt.Checked)
        hbl2.addWidget(self.cbCopy)

        self.cb = QtWidgets.QCheckBox("Modifier les données Exif", self)
        hbl2.addWidget(self.cb)

        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close | QtWidgets.QDialogButtonBox.Ok, self)
        bb.button(QtWidgets.QDialogButtonBox.Ok).setIcon(QtGui.QIcon(":/resources/start.png"))
        bb.button(QtWidgets.QDialogButtonBox.Close).setText("Quitter")
        hbl2.addWidget(bb)

        layout.addItem(hbl1, 0, 0, 1, 1)
        layout.addItem(hbl2, 1, 0, 1, 1)
        self.pbar = QtWidgets.QProgressBar(self)
        layout.addWidget(self.pbar, 2, 0, 1, 1)

        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.dispatch)
        browse_btn.clicked.connect(self.on_browse_directory)

    def on_browse_directory(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Sélectionner le répertoire", params.DEFAULT_IMAGE_DIR,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        if dir is not None:
            self.dir_le.setText(dir)
            self.dir_le.setToolTip(dir)

    def dispatch(self):
        self.pbar.reset()
        count = 0

        directory = self.dir_le.text()
        if not directory:
            return

        dec = self.sb.value()

        # comptage des fichiers
        qdir = QtCore.QDir(directory)
        list = qdir.entryList(["*.jpg", "*.jpeg"], QtCore.QDir.Files)
        self.pbar.reset()
        self.pbar.setMaximum(len(list))

        it = QtCore.QDirIterator(directory, ["*.jpg", "*.jpeg"], QtCore.QDir.Files)
        while it.hasNext():
            path = it.next()

            # Mise a jour de la progress bar
            count += 1
            self.pbar.setValue(count)

            metadatas = piexif.load(path)
            if piexif.ExifIFD.DateTimeOriginal not in metadatas['Exif']:
                continue

            str_date = str(metadatas['Exif'][piexif.ExifIFD.DateTimeOriginal], 'UTF-8')
            date = datetime.strptime(str_date, '%Y:%m:%d %H:%M:%S')
            if dec != 0:
                date += timedelta(hours=dec)

            folder = '{}/{}'.format(directory, date.strftime('%Y-%m-%d'))
            if not os.path.exists(folder):
                try:
                    os.mkdir(folder)
                except OSError:
                    print("Echec de la création du répertoire %s" % folder)
                    continue

            # copie du fichier
            shutil.copy2(path, folder)

            # change metadatas
            if dec != 0 and self.cb.isChecked():
                filepath = '{}/{}'.format(folder, os.path.basename(path))

                metadatas['Exif'][piexif.ExifIFD.DateTimeOriginal] = date.strftime('%Y:%m:%d %H:%M:%S')
                metadatas['Exif'][piexif.ExifIFD.DateTimeDigitized] = date.strftime('%Y:%m:%d %H:%M:%S')
                exif_bytes = piexif.dump(metadatas)
                piexif.insert(exif_bytes, filepath)