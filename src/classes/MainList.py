from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea, QLabel
from PyQt6.QtCore import Qt

class MainList(QScrollArea):
  def __init__(self):
    super().__init__()
    self.setupUI()

  def setupUI(self):
    widget = QWidget()
    self.vbox = QVBoxLayout(widget)
    self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.vbox.setContentsMargins(0,0,0,0)

    self.setWidget(widget)
    self.setWidgetResizable(True)

    #self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    #self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    #self.scrollArea.setWidgetResizable(True)
    

  def addUnit(self, unit):
    self.vbox.addWidget(unit)