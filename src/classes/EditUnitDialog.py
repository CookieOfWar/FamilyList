from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea
)
from PyQt6.QtCore import QPropertyAnimation, Qt, pyqtSignal, pyqtSlot
from classes.ImageSelector import ImageSelector

class EditUnitDialog(QWidget):
  end_of_operation = pyqtSignal(str, str, str, str, list)
  def __init__(self, ln, fn, mn, desc, pix):
    super().__init__()
    self.setupUI(ln, fn, mn, desc, pix)

  def setupUI(self, ln, fn, mn, desc, pix):
    self.hbox = QHBoxLayout()
    self.vbox = QVBoxLayout()

    self.setLayout(self.vbox)
    self.last_name_edit = QTextEdit(ln)
    self.last_name_edit.setPlaceholderText("Фамилия")
    self.last_name_edit.setMaximumHeight(50)
    self.vbox.addWidget(self.last_name_edit)

    self.first_name_edit = QTextEdit(fn)
    self.first_name_edit.setPlaceholderText("Имя")
    self.first_name_edit.setMaximumHeight(50)
    self.vbox.addWidget(self.first_name_edit)

    self.middle_name_edit = QTextEdit(mn)
    self.middle_name_edit.setPlaceholderText("Отчество")
    self.middle_name_edit.setMaximumHeight(50)
    self.vbox.addWidget(self.middle_name_edit)

    self.vbox.addLayout(self.hbox)

    self.description = QTextEdit(desc)
    self.description.setPlaceholderText("Описание")
    self.hbox.addWidget(self.description)

    self.image_edit = ImageSelector(True, pix)
    self.hbox.addWidget(self.image_edit)

    self.bottom_hbox = QHBoxLayout()
    self.cancel_button = QPushButton("Отменить")
    self.cancel_button.clicked.connect(self.cancel_operation)
    self.save_button = QPushButton("Сохранить")
    self.save_button.clicked.connect(self.save_operation)

    self.bottom_hbox.addWidget(self.cancel_button)
    self.bottom_hbox.addWidget(self.save_button)

    self.vbox.addLayout(self.bottom_hbox)

  def cancel_operation(self):
    self.end_of_operation.emit("", "", "", "", [])
    self.close()

  def save_operation(self):
    self.end_of_operation.emit(self.last_name_edit.toPlainText(), self.first_name_edit.toPlainText(), self.middle_name_edit.toPlainText(), self.description.toPlainText(), self.image_edit.get_pixmaps())
    self.close()
