from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QMenuBar, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from classes.MainList import MainList
from classes.ListUnit import ListUnit

class MainWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.resize(600, 800)
    self.List: MainList = None
    self.setupUI()
    for i in range(10):
      self.List.addUnit(ListUnit())
    unit = ListUnit()
    self.List.addUnit(unit)

  def setupUI(self):
    self.central_layout = QVBoxLayout()
    self.setLayout(self.central_layout)

    self.setupTools()
    
    self.List = MainList()
    self.central_layout.addWidget(self.List)


  def setupTools(self):
    tool_widget = QWidget()
    tool_layout = QHBoxLayout()
    tool_widget.setLayout(tool_layout)
    self.central_layout.addWidget(tool_widget)
    tool_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
    tool_layout.addWidget(QLabel("Настройки"))

    settings_button = QPushButton()
    settings_button.setIcon(QIcon("src/img/settings_icon.png"))
    settings_button.setFixedSize(40, 40)
    settings_button.setIconSize(settings_button.size())

    tool_layout.addWidget(settings_button)
