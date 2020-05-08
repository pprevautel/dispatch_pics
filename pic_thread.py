import os
from datetime import datetime, timedelta
from PyQt5 import QtCore
import piexif


class PicThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

        self._dir = None
        self._dec = 0
        self._copy = True
        self._changeExif = False

    # signal envoye a chaque copie de fichier
    progress = QtCore.pyqtSignal(int)

    def __del__(self):
        self.wait()

    def set_directory(self, name):
        self._dir = name

    def set_time_difference(self, dec):
        self._dec = dec

    def set_copy(self, copy):
        self._copy = copy

    def set_change_exif(self, change):
        self._changeExif = change

    def run(self):
        count = 0

        it = QtCore.QDirIterator(self._dir, ["*.jpg", "*.jpeg"], QtCore.QDir.Files)
        while it.hasNext():
            path = it.next()

            # Mise a jour de la progress bar
            count += 1
            self.progress.emit(count)

            metadatas = piexif.load(path)
            if piexif.ExifIFD.DateTimeOriginal not in metadatas['Exif']:
                continue

            str_date = str(metadatas['Exif'][piexif.ExifIFD.DateTimeOriginal], 'UTF-8')
            date = datetime.strptime(str_date, '%Y:%m:%d %H:%M:%S')
            if self._dec != 0:
                date += timedelta(hours=self._dec)

            folder = os.path.join(self._dir, date.strftime('%Y-%m-%d'))
            if not os.path.exists(folder):
                try:
                    os.mkdir(folder)
                except OSError:
                    print("Echec de la création du répertoire %s" % folder)
                    continue

            # copie ou deplaement du fichier
            new_file_path = os.path.join(folder, os.path.basename(path))
            if self._copy:
                QtCore.QFile.copy(path, new_file_path)
            else:
                QtCore.QFile.rename(path, new_file_path)

            # change metadatas
            if self._dec != 0 and self._changeExif is True:
                metadatas['Exif'][piexif.ExifIFD.DateTimeOriginal] = date.strftime('%Y:%m:%d %H:%M:%S')
                metadatas['Exif'][piexif.ExifIFD.DateTimeDigitized] = date.strftime('%Y:%m:%d %H:%M:%S')
                exif_bytes = piexif.dump(metadatas)
                piexif.insert(exif_bytes, new_file_path)
