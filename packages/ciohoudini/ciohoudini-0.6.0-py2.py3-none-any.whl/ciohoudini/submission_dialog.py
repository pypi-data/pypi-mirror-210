import hou
from PySide2 import QtWidgets
from PySide2 import QtWidgets, QtCore, QtGui

from ciohoudini.validation_tab import ValidationTab
# PROGRESS TAB NOT YET IMPLEMENTED
# from ciohoudini.progress_tab import ProgressTab
from ciohoudini.response_tab import ResponseTab
from ciohoudini import validation

class SubmissionDialog(QtWidgets.QDialog):

    def __init__(self, nodes, parent=None):
        super(SubmissionDialog, self).__init__(parent)
        self.setWindowTitle("Conductor Submission")
        self.setStyleSheet(hou.qt.styleSheet())
        self.layout = QtWidgets.QVBoxLayout()
        self.tab_widget = QtWidgets.QTabWidget()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

        self.validation_tab = ValidationTab(self)
        self.tab_widget.addTab(self.validation_tab, "Validation")

        # PROGRESS TAB NOT YET IMPLEMENTED
        # self.progress_tab = ProgressTab(self)
        # self.tab_widget.addTab(self.progress_tab, "Progress")
 
        self.response_tab = ResponseTab(self)
        self.tab_widget.addTab(self.response_tab, "Response")
        self.setGeometry(300, 200, 1000, 600)
        self.tab_widget.setTabEnabled(1, False)

        self.nodes = nodes
 
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.run()
    
    def run(self):
        errors, warnings, notices =  validation.run(*(self.nodes))
        self.validation_tab.populate(errors, warnings, notices)

    def on_close(self):
        self.accept()
