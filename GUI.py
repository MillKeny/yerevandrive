import sys
import ast

from extractContent import *
from replaceContent import *
from convertText import *
from manipulateCars import *

from PyQt6 import QtWidgets, QtGui, QtCore, QtMultimedia
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTreeWidgetItem, QApplication
import ydt_ui
    
class Program(QtWidgets.QMainWindow, ydt_ui.Ui_MainWindow):
    previews = {}
    currentZoom = 0
    currentOpened = ''
    currentIni = None
    convertSwap = True
    
    recentOpened = []
    gamePath = ''
    
    def resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)
    
    def save_config(self):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'recents': self.recentOpened,
            'gamepath': self.gamePath
        }

        config_path = self.resource_path('data/ydt.ini')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
    def load_config(self):
        if os.path.exists('data/ydt.ini'):
            config = configparser.ConfigParser()
            config.read('data/ydt.ini')
            self.recentOpened = ast.literal_eval(config['SETTINGS']['recents'])
            self.gamePath = config['SETTINGS']['gamepath']
        else:
            self.save_config()
    
    def locate_game(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Locate Game')
        if path == '':
            return
        if not os.path.isdir(path + '/Cars'):
            QMessageBox.warning(self, 'Invalid Yerevan Drive folder', 'Not valid Yerevan Drive root folder')
            return
        self.gamePath = path
        self.locateLabel.setText(path)
        self.open_cars()
        
    def open_cars(self):
        cars = get_params(self.gamePath + '/Cars')
        
        for k, v in cars.items():
            QTreeWidgetItem(self.carTree, [k])
            
    def car_select_changed(self):
        if self.carTree.selectedItems():
            cars = get_params(self.gamePath + '/Cars')
            lastn = 0
            for n, i in enumerate(cars[self.carTree.selectedItems()[0].text(0)]):
                self.paramsTable.setItem(n, 0, QtWidgets.QTableWidgetItem(str(round(struct.unpack('f', i)[0], 2))))
                lastn = n
            self.paramsTable.setItem(lastn+1, 0, QtWidgets.QTableWidgetItem(str(getCarsNPC(self.gamePath + '/Cars')[self.carTree.selectedItems()[0].text(0)])))
            self.paramsTable.setColumnWidth(0, self.groupBox_3.width()//2)
    
    def save_params(self):
        if self.carTree.selectedItems():
            reply = QMessageBox.question(self, 'Replacing', 'Do you really want to replace original strings?')
            if reply != 16384:
                return

            params = []
            for i in range(self.paramsTable.rowCount()-1):
                params.append(float(self.paramsTable.item(i, 0).text()))
            replace_params(self.gamePath + '/Cars/' + self.carTree.selectedItems()[0].text(0), params)
            setCarsNPC(self.gamePath + '/Cars/' + self.carTree.selectedItems()[0].text(0), int(self.paramsTable.item(self.paramsTable.rowCount()-1, 0).text()))
            QMessageBox.information(self, 'Saving', 'New car parameters saved successfully')
    
    def open_file(self, filepath=''):
        self.close_file()
        
        # filepath = "work\\tex\\mobjects.tex"
        if not filepath:
            filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Yerevan Drive Files (*.tex *.snd *.atx *.ini);;Image Archive (*.tex *.atx);;Audio Archive (*.snd);;Config File (*.ini);;All Files (*.*)")[0]
            if not filepath:
                return
        self.currentOpened = filepath
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        if filepath in self.recentOpened: self.recentOpened.remove(filepath)
        self.recentOpened.insert(0, filepath)
        if len(self.recentOpened) > 10:
            self.recentOpened.pop()
        
        if not check_suffix(filepath, '.ini'):
            filelist = extract_yd(filepath=filepath, just_read=False, preview=True)
            for i in filelist:
                    QTreeWidgetItem(self.fileTree, [i[0], str(i[2]) + ' bytes'])
                
        if check_suffix(filepath, '.snd'):
            self.radioConv.setText('')
            self.stackedWidget.setCurrentWidget(self.page_2)
        elif check_suffix(filepath, '.ini'):
            self.currentIni = openText(filepath)
            for k, v in self.currentIni.items():
                    QTreeWidgetItem(self.fileTree, [k, str(len(v)) + ' strings'])
            self.stackedWidget.setCurrentWidget(self.page_3)
        else:
            self.radioConv.setText('PNG')
            self.radioConv.setEnabled(True)
            self.stackedWidget.setCurrentWidget(self.page)
            for i in filelist:
                self.previews[i[0]] = QtGui.QPixmap('.temp/previews/' + i[0] + '.png')
        
        if not check_suffix(filepath, '.ini'):
            self.actionClose_2.setEnabled(True)
            self.extractButton.setEnabled(True)
            self.extractAllButton.setEnabled(True)
            self.radioOrig.setEnabled(True)
            self.radioOrig.setChecked(True)
        self.replaceButton.setEnabled(True)
        self.setWindowTitle("Yerevan Drive Tools | " + filepath)
        self.textTable.setRowCount(0)
        self.imageprev.setText('')
        
        for i in self.menuOpen_Recent.actions():
            self.menuOpen_Recent.removeAction(i)
        for i in self.recentOpened:
            if os.path.exists(i): self.menuOpen_Recent.addAction(i)
            else: self.recentOpened.remove(i)
        
        QApplication.restoreOverrideCursor()
            
    def extract_file(self):
        if self.fileTree.selectedItems():
            selected = self.fileTree.selectedItems()[0].text(0)
            if check_suffix(self.currentOpened, '.snd'):
                filters = 'WAVE (*.wav)'
            else:
                if check_suffix(selected, '.dds'):
                    filters = "DirectDraw Surface (*.dds)"
                elif check_suffix(selected, '.bmp'):
                    filters = "Bitmap Picture (*.bmp)"
                elif check_suffix(selected, '.tga'):
                    filters = "Truevision TGA (*.tga)"
                elif check_suffix(selected, '.jpg'):
                    filters = "JPEG (*.jpg)"
                filters += ";;PNG Image (*.png)"
            filepath = QtWidgets.QFileDialog.getSaveFileName(self, "Extract File", self.fileTree.selectedItems()[0].text(0), filters)
            if filepath[0]:
                if check_suffix_list(filepath[0], ['.dds', '.bmp', '.tga', '.jpg', '.wav']):
                    shutil.copy('.temp/original/' + selected, filepath[0])
                elif filepath[0].endswith('.png'):
                    shutil.copy('.temp/previews/' + selected + '.png', filepath[0])
                else:
                    QMessageBox.information(self, "Extracting Failed", "Not supported file format")
                    
    def extract_all(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Extract All")
        if directory:
            for file in os.listdir('.temp/original/'):
                filename = os.fsdecode(file)
                if self.radioConv.isChecked():
                    src = '.temp/previews/' + file + '.png'
                    dest = directory + '/' + filename + '.png'
                else:
                    src = '.temp/original/' + file
                    dest = directory + '/' + filename
                shutil.copy(src, dest)
            
            QMessageBox.information(self, 'Extracted All', 'Extracted all successfully to ' + directory)
    
    def replace_file(self):
        if not self.fileTree.selectedItems():
            return
        
        if check_suffix_list(self.currentOpened, ['.tex', '.atx']):
            filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Image (*.tga *.bmp *.gif *.ppm *.jpg *.tif *.cel *.dds *.png *.psd *.rgb *.bw *.rgba)")[0]
            if not filepath:
                return
            
            message = replace_yd(self.currentOpened, self.fileTree.selectedItems()[0].text(0), filepath, '.temp/converted')
            if message[0] == 0:
                QMessageBox.warning(self, 'Replacing Error', message[1])
            else:
                QMessageBox.information(self, 'Replacing', message[1])
        elif check_suffix(self.currentOpened, '.snd'):
            filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "WAVE (*.wav)")[0]
            if not filepath:
                return
            
            message = replace_yd(self.currentOpened, self.fileTree.selectedItems()[0].text(0), filepath, '.temp/converted')
            if message[0] == 0:
                QMessageBox.warning(self, 'Replacing Error', message[1])
            else:
                QMessageBox.information(self, 'Replacing', message[1])
        elif check_suffix(self.currentOpened, '.ini'):
            reply = QMessageBox.question(self, 'Replacing', 'Do you really want to replace original strings?')
            if reply != 16384:
                return
            
            config = configparser.ConfigParser()
            config.read(self.currentOpened)

            for i in range(self.textTable.rowCount()):
                config[self.fileTree.selectedItems()[0].text(0)][self.textTable.item(i, 0).text()] = convertText(self.textTable.item(i, 1).text())
            
            with open(self.currentOpened, 'w', encoding='ansi') as configfile:
                config.write(configfile)
                QMessageBox.information(self, 'Replacing', "Ini file saved successfully!")
        self.open_file(self.currentOpened)
        
    def select_changed(self):
        if check_suffix_list(self.currentOpened, ['.tex', '.atx']):
            self.currentZoom = 0
            
            if self.fileTree.selectedItems():
                pixmap = self.previews[self.fileTree.selectedItems()[0].text(0)]
            else:
                return
            
            if pixmap.width() > 500:
                pixmap = pixmap.scaled(500, pixmap.height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            elif pixmap.height() > 500:
                pixmap = pixmap.scaled(pixmap.width(), 500, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            
            self.imageprev.setPixmap(pixmap)
            self.imageprev.resize(pixmap.width(), pixmap.height())
        elif check_suffix(self.currentOpened, '.ini'):
            if self.fileTree.selectedItems():
                self.textTable.setRowCount(len(self.currentIni[self.fileTree.selectedItems()[0].text(0)]))

                n = 0
                for k, v in self.currentIni[self.fileTree.selectedItems()[0].text(0)].items():
                    self.textTable.setItem(n, 0, QtWidgets.QTableWidgetItem(k))
                    self.textTable.setItem(n, 1, QtWidgets.QTableWidgetItem(convertText(v, True)))
                    n+=1
            
                for i in range(self.textTable.rowCount()):
                    self.textTable.setRowHeight(i, 40)
                    
                self.textTable.setColumnWidth(1, self.stackedWidget.width()-200)
                
    def text_convert_changed(self):
        left = self.plainTextEdit_L.toPlainText()
        self.plainTextEdit_R.setPlainText(convertText(left, self.convertSwap))
    
    def swap_convert(self):
        temp = self.label_L.text()
        self.label_L.setText(self.label_R.text())
        self.label_R.setText(temp)
        temp2 = self.plainTextEdit_L.toPlainText()
        self.plainTextEdit_L.setPlainText(self.plainTextEdit_R.toPlainText())
        self.plainTextEdit_R.setPlainText(temp2)
        
        self.convertSwap = not self.convertSwap
    
    def play_sound(self):
        if self.fileTree.selectedItems():
            self.player.setSource(QtCore.QUrl.fromLocalFile(".temp/original/" + self.fileTree.selectedItems()[0].text(0)))
            self.player.play()
    
    def search_changed(self):
        text = self.searchBar.text()

        if not text:
            for i in range(self.fileTree.topLevelItemCount()):
                self.fileTree.setRowHidden(i, QtCore.QModelIndex(), False)
            return
        
        for i in range(self.fileTree.topLevelItemCount()):
            item = self.fileTree.topLevelItem(i)
            match = text.lower() in item.text(0).lower()
            self.fileTree.setRowHidden(i, QtCore.QModelIndex(), not match)
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Yerevan Drive Tools")
        self.setWindowIcon(QtGui.QIcon('data/icon.ico'))
        self.load_config()

        self.imageprev.setText('')
        self.locateLabel.setText(self.gamePath)
        self.stackedWidget.setCurrentWidget(self.page)
        self.tabWidget.setCurrentWidget(self.mainTab)
        if self.gamePath != '':
            self.open_cars()
        
        self.actionOpen.triggered.connect(self.open_file)
        self.actionClose_2.triggered.connect(self.close_file)
        self.actionQuit.triggered.connect(self.close)
        for i in self.recentOpened:
            if os.path.exists(i): self.menuOpen_Recent.addAction(i)
            else: self.recentOpened.remove(i)
        self.menuOpen_Recent.triggered.connect(lambda action: self.open_file(action.text()))
        self.actionAbout.triggered.connect(lambda: QMessageBox.about(self, 'About', """
Yerevan Drive Tools for modding and exploring game's contents
by Artyom "MillKeny" Arzumanyan

«Երևան Դրայվ»-ի գործիքներ՝ խաղի պարունակությունը փոխելու ու ուսումնասիրելու համար
Հեղինակ՝ Արտյոմ "MillKeny" Արզումանյան

v1.1
"""))
        
        self.fileTree.itemSelectionChanged.connect(self.select_changed)
        self.carTree.itemSelectionChanged.connect(self.car_select_changed)
        self.extractButton.pressed.connect(self.extract_file)
        self.extractAllButton.pressed.connect(self.extract_all)
        self.replaceButton.pressed.connect(self.replace_file)
        self.playButton.pressed.connect(self.play_sound)
        self.convertTextButton.pressed.connect(self.text_convert_changed)
        self.swapButton.pressed.connect(self.swap_convert)
        self.searchBar.textChanged.connect(self.search_changed)
        self.locateButton.pressed.connect(self.locate_game)
        self.saveParamsButton.pressed.connect(self.save_params)
        
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.copyL.pressed.connect(lambda: self.clipboard.setText(self.plainTextEdit_L.toPlainText().strip()))
        self.copyR.pressed.connect(lambda: self.clipboard.setText(self.plainTextEdit_R.toPlainText().strip()))

        self.player = QtMultimedia.QMediaPlayer()
        self.audio = QtMultimedia.QAudioOutput()
        self.player.setAudioOutput(self.audio)
        
        # lay = QtWidgets.QFormLayout()
        # self.page_2.setLayout(lay)
        # lay.addWidget(QtWidgets.QLabel("QAQ"))
        # self.stackedWidget.setCurrentWidget(self.page_2)

    def wheelEvent(self, e):
        if self.previews:
            pos = self.groupBox.mapFromGlobal(e.globalPosition().toPoint())
            if self.groupBox.rect().contains(pos):
                if self.fileTree.selectedItems():
                    pixmap = self.previews[self.fileTree.selectedItems()[0].text(0)]
                else:
                    return
                
                if e.angleDelta().y() > 0: scalefactor = 40
                else: scalefactor = -40
                
                if self.currentZoom == 0:
                    if pixmap.width() > pixmap.height(): neww = pixmap.width() + scalefactor
                    else: neww = pixmap.height() + scalefactor
                else: neww = self.currentZoom + scalefactor
                if neww > self.stackedWidget.width()-40:
                    neww = self.stackedWidget.width()-40
                elif neww < 32:
                    neww = 32
                    
                pixmap = pixmap.scaled(neww, neww, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                self.imageprev.setPixmap(pixmap)
                
                self.currentZoom = neww
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if check_suffix_list(str(url.toLocalFile()), ['.tex', '.snd', '.atx', '.ini']):
                        self.open_file(str(url.toLocalFile()))
                        return
        else:
            event.ignore()
            
    def close_file(self):
        self.fileTree.clear()
        self.imageprev.clear()
        self.fileTree.clearSelection()
        self.previews = {}
        self.currentZoom = 0
        self.actionClose_2.setEnabled(False)
        self.extractButton.setEnabled(False)
        self.replaceButton.setEnabled(False)
        self.extractAllButton.setEnabled(False)
        self.radioConv.setEnabled(False)
        self.radioOrig.setEnabled(False)
        self.radioConv.setText('')
        self.stackedWidget.setCurrentWidget(self.page)
        
        self.setWindowTitle("Yerevan Drive Tools")
        self.player.stop()
        self.quit_gui()
    
    def quit_gui(self):
        self.player.setSource(QtCore.QUrl.fromLocalFile(''))
        if os.path.exists('.temp'): shutil.rmtree('.temp')
        self.save_config()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Program()
    window.show()
    try: window.open_file(sys.argv[1])
    except: pass
    app.exec()
    window.quit_gui()

if __name__ == '__main__':
    main()