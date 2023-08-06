import sys
import os.path
from PyQt6 import QtWidgets, QtGui, QtCore, Qsci

from pyaudicle import Ui_MainWindow
import pychuck
from pychuck.core import _Chuck

'''================================================================================'''
'''|                                  EDITOR                                      |'''
'''================================================================================'''


class ScintillaEditor(Qsci.QsciScintilla):

    def __init__(self):
        super(ScintillaEditor, self).__init__()
        self.path = None

        # -------------------------------- #
        #     QScintilla editor setup      #
        # -------------------------------- #

        self.setText("")
        self.setLexer(None)  # We install lexer later
        self.setUtf8(True)  # Set encoding to UTF-8

        # 1. Text wrapping
        # -----------------
        self.setWrapMode(Qsci.QsciScintilla.WrapMode.WrapWord)
        self.setWrapVisualFlags(Qsci.QsciScintilla.WrapVisualFlag.WrapFlagByText)
        self.setWrapIndentMode(Qsci.QsciScintilla.WrapIndentMode.WrapIndentIndented)

        # 2. End-of-line mode
        # --------------------
        self.setEolMode(Qsci.QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)

        # 3. Indentation
        # ---------------
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)

        # 4. Caret
        # ---------
        self.setCaretForegroundColor(QtGui.QColor("#ff0000ff"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#1f0000ff"))
        self.setCaretWidth(2)

        # 5. Margins
        # -----------
        self.setMarginType(0, Qsci.QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsForegroundColor(QtGui.QColor("#ff888888"))

        # -------------------------------- #
        #          Install lexer           #
        # -------------------------------- #
        self.__lexer = Qsci.QsciLexerPython(self)
        self.setLexer(self.__lexer)

    def read(self, path):
        self.path = path
        self.setText(open(path).read())

    def clear(self):
        self.path = None
        self.setText("")

    def save(self):
        with open(self.path, "w") as f:
            f.write(self.text())


'''=== end class ==='''


class TabMaster:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget
        self.tab_widget.addTab(ScintillaEditor(), "Untitled")

    def add_tab(self, file_path):
        file_name = os.path.basename(file_path)
        n_tab = self.tab_widget.count()
        if self.tab_widget.tabText(0) == "Untitled" and len(self.tab_widget.widget(0).text()) == 0:
            self.tab_widget.setTabText(0, file_name)
            self.tab_widget.widget(0).read(file_path)
            return
        for i in range(n_tab):
            if self.tab_widget.widget(i).path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return
        self.tab_widget.addTab(ScintillaEditor(), file_name)
        self.tab_widget.widget(n_tab).read(file_path)
        self.tab_widget.setCurrentIndex(n_tab)

    def remove_tab(self, index):
        if self.tab_widget.count() == 1:
            self.tab_widget.setTabText(0, "Untitled")
            self.tab_widget.widget(0).clear()
        else:
            tab = self.tab_widget.widget(index)
            tab.deleteLater()
            self.tab_widget.removeTab(index)

    def add_new_tab(self):
        count = 1
        n_tab = self.tab_widget.count()
        for i in range(n_tab):
            if self.tab_widget.tabText(i).startswith("Untitled"):
                count += 1
        tab_name = "Untitled" if count == 1 else f"Untitled {count}"
        self.tab_widget.addTab(ScintillaEditor(), tab_name)
        self.tab_widget.setCurrentIndex(n_tab)

    def save_file(self):
        if self.tab_widget.currentWidget().path is None:
            return self.save_file_as()
        self.tab_widget.currentWidget().save()

    def save_file_as(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self.tab_widget, "Save File", "", "Python Files (*.py)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_name)
            self.tab_widget.currentWidget().path = file_path
            self.tab_widget.currentWidget().save()

    def close_editor(self):
        self.remove_tab(self.tab_widget.currentIndex())

    def curr_tab_name(self):
        return self.tab_widget.tabText(self.tab_widget.currentIndex())

    def curr_tab_code(self):
        return self.tab_widget.currentWidget().text()


class StreamToTextBrowser:
    def __init__(self, text_browser):
        self.text_browser = text_browser

    def write(self, message):
        self.text_browser.append(message)

    def flush(self):
        pass


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("PyAudicle")

        # console
        sys.stdout = sys.stderr = StreamToTextBrowser(self.textBrowser)

        # button
        self.pushButton.clicked.connect(self.change_vm_state)
        self.pushButton_2.clicked.connect(self.add_shred)
        self.pushButton_3.clicked.connect(self.replace_shred)
        self.pushButton_4.clicked.connect(self.remove_shred)
        self.pushButton_5.clicked.connect(self.remove_last_shred)
        self.pushButton_6.clicked.connect(self.clear_vm)

        # explorer
        self.file_system_model = QtGui.QFileSystemModel(self)
        self.file_system_model.setRootPath(QtCore.QDir.rootPath())
        self.treeView.setModel(self.file_system_model)
        self.treeView.setRootIndex(self.file_system_model.index(QtCore.QDir.currentPath()))
        self.treeView.header().hide()
        for i in range(1, self.treeView.header().count()):
            self.treeView.hideColumn(i)
        self.treeView.doubleClicked.connect(self.treeView_doubleClicked)

        # virtual machine
        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 65)
        self.tableWidget.setColumnWidth(3, 20)
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setRowHeight(i, 20)
            for j in range(3):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem())
            button = QtWidgets.QPushButton("-")
            button.clicked.connect(lambda _, row=i: self.remove_row(row))
            self.tableWidget.setCellWidget(i, 3, button)
        self.refresh_table_timer = QtCore.QTimer()
        self.refresh_table_timer.timeout.connect(self.refresh_table)
        self.refresh_table_timer.start(500)

        # editor
        self.tab_master = TabMaster(self.tabWidget_3)
        self.tabWidget_3.tabCloseRequested.connect(self.tab_master.remove_tab)

        # action
        self.actionNew_File.triggered.connect(self.tab_master.add_new_tab)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionOpen_Folder.triggered.connect(self.open_folder)
        self.actionSave.triggered.connect(self.tab_master.save_file)
        self.actionSave_As.triggered.connect(self.tab_master.save_file_as)
        self.actionClose_Editor.triggered.connect(self.tab_master.close_editor)

    def change_vm_state(self):
        if self.pushButton.text() == "Start Virtual Machine":
            self.pushButton.setText("Stop Virtual Machine")
            print("Starting Virtual Machine...")
            pychuck.VM.start()
        else:
            self.pushButton.setText("Start Virtual Machine")
            print("Stopping Virtual Machine...")
            pychuck.VM.stop()

    def add_shred(self):
        pychuck.VM.add_shred(self.tab_master.curr_tab_code(), self.tab_master.curr_tab_name())

    def replace_shred(self):
        name = self.tab_master.curr_tab_name()
        pychuck.VM.remove_shred(name)
        pychuck.VM.add_shred(self.tab_master.curr_tab_code(), name)

    def remove_shred(self):
        pychuck.VM.remove_shred(self.tab_master.curr_tab_name())

    def remove_last_shred(self):
        pychuck.VM.remove_last_shred()

    def clear_vm(self):
        pychuck.VM.clear_vm()

    def treeView_doubleClicked(self, index):
        file_path = self.file_system_model.filePath(index)
        if QtCore.QFileInfo(file_path).isFile():
            self.tab_master.add_tab(file_path)

    def open_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",
                                                             "All Files (*);;Python Files (*.py)")
        if file_path:
            self.tab_master.add_tab(file_path)

    def open_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            self.treeView.setRootIndex(self.file_system_model.index(folder_path))

    def refresh_table(self):
        for i in range(self.tableWidget.rowCount()):
            for j in range(3):
                self.tableWidget.item(i, j).setText("")
        for i, shred in enumerate(pychuck.VM._shreds):
            self.tableWidget.item(i, 0).setText(str(shred._id))
            self.tableWidget.item(i, 1).setText(shred._name)
            seconds = shred._samples_computed // pychuck.VM._sample_rate
            min, sec = divmod(seconds, 60)
            self.tableWidget.item(i, 2).setText(f'{min:02}:{sec:02}')

    def change_shred_state(self, row):
        self.tableWidget.cellWidget(row, 3).setCheckState(QtCore.Qt.CheckState.Unchecked)

    def remove_row(self, row):
        id_str = self.tableWidget.item(row, 0).text()
        if len(id_str) > 0:
            pychuck.VM.remove_shred(id=int(id_str))


def main():
    _Chuck()
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
