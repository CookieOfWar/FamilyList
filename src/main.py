from classes.MainWindow import MainWindow
from classes.MainList import MainList
from classes.ListUnit import ListUnit
from classes.ImageSelector import ImageSelector
import os

from PyQt6.QtWidgets import QApplication

import sys

if __name__ == '__main__':
  #sys.argv += ['-platform', 'minimal:darkmode=2']
  app = QApplication(sys.argv)
  mainWindow = MainWindow()
  mainWindow.show()
  #imageSelector = ImageSelector()
  #imageSelector.show()
  
  sys.exit(app.exec())

