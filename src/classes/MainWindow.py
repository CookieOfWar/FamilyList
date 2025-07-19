from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QMenuBar, QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QIcon, QPixmap, QImage
from classes.MainList import MainList
from classes.ListUnit import ListUnit
from classes.DatabaseManager import DatabaseManager
from classes.PDFMaker import PDFMaker
from pprint import pprint

from utils import resource_path, auto_save

class MainWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.resize(600, 800)
    self.List: MainList = MainList()
    self.setupUI()
    self.DBM = DatabaseManager()

    self.autosave = auto_save(self.DBM, self.List)

    #for i in range(400):
    #  unit = ListUnit()
    #  unit.update_information("test", "test", "test",
    #                          "a big description",
    #                          [QPixmap(QImage("/home/astr/Programming/Python/FamilyList/img/arrow_down.png")),
    #                           QPixmap(QImage("/home/astr/Programming/Python/FamilyList/img/arrow_up.png")),
    #                           QPixmap(QImage("/home/astr/Programming/Python/FamilyList/img/delete_icon.png")),
    #                           QPixmap(QImage("/home/astr/Programming/Python/FamilyList/img/edit_icon.png"))])
    #  self.List.addUnit(unit)

  def setupUI(self):
    self.central_layout = QVBoxLayout()
    self.setLayout(self.central_layout)

    self.setupTools()
    
    self.central_layout.addWidget(self.List)


  def setupTools(self):
    tool_widget = QWidget()
    tool_layout = QHBoxLayout()
    tool_widget.setLayout(tool_layout)
    self.central_layout.addWidget(tool_widget)
    tool_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
    tool_layout.addWidget(QLabel("Настройки"))

    filter_hbox = QHBoxLayout()
    self.central_layout.addLayout(filter_hbox)
    self.filter_last_button = QPushButton("Фамилия")
    self.filter_first_button = QPushButton("Имя")
    self.filter_middle_button = QPushButton("Отчество")
    for i in [self.filter_last_button, self.filter_first_button, self.filter_middle_button]:
      i.setStyleSheet("border: none;")
      i.clicked.connect(self.filterList)
    filter_hbox.addWidget(self.filter_last_button)
    filter_hbox.addWidget(self.filter_first_button)
    filter_hbox.addWidget(self.filter_middle_button)

    download_button = QPushButton()
    download_button.clicked.connect(self.downloadDB)
    print("resourse path: " + resource_path("img/download_icon.png"))
    download_button.setIcon(QIcon(resource_path("img/download_icon.png")))
    download_button.setFixedSize(40, 40)
    download_button.setIconSize(download_button.size())

    upload_button = QPushButton()
    upload_button.clicked.connect(self.uploadDB)
    upload_button.setIcon(QIcon(resource_path("img/upload_icon.png")))
    upload_button.setFixedSize(40, 40)
    upload_button.setIconSize(upload_button.size())

    tool_layout.addWidget(download_button)
    tool_layout.addWidget(upload_button)

    add_button = QPushButton("+")
    add_button.clicked.connect(lambda: (self.List.addUnit(ListUnit()), self.reset_filters()))
    add_button.setFixedSize(40, 40)

    manage_button = QPushButton()
    manage_button.clicked.connect(self.manage_list)
    manage_button.setIcon(QIcon(resource_path("img/settings_icon.png")))
    manage_button.setFixedSize(40, 40)
    manage_button.setIconSize(manage_button.size())

    tool_layout.addWidget(add_button)
    tool_layout.addWidget(manage_button)

    pdf_button = QPushButton()
    pdf_button.clicked.connect(self.generatePDF)
    pdf_button.setIcon(QIcon(resource_path("img/pdf_icon.png")))
    pdf_button.setFixedSize(40, 40)
    pdf_button.setIconSize(pdf_button.size())
    tool_layout.addWidget(pdf_button)

  def reset_filters(self):
    for i in [self.filter_last_button, self.filter_first_button, self.filter_middle_button]:
      i.setText(i.text().replace(" ▲", "").replace(" ▼", ""))

  def filterList(self):
    l = [self.filter_last_button, self.filter_first_button, self.filter_middle_button]
    sender = self.sender()
    l.remove(sender)
    for i in l:
      i.setText(i.text().replace("▼", "").replace("▲", ""))
    if isinstance(sender, QPushButton):
      if sender.text().find(" ▼") == -1:
        sender.setText(sender.text().replace(" ▲", "") + " ▼")
      else:
        sender.setText(sender.text().replace(" ▼", "") + " ▲")
    
    self.List.filterList(sender.text())
  

  def downloadDB(self):
    """Обработчик загрузки БД"""
    units_data = self.DBM.load_units(self)
    if units_data is not None:
        # Очищаем текущие данные
        self.List.clear_units()
        
        # Загружаем новые данные
        for unit_data in units_data:
            pprint(unit_data)
            unit = ListUnit()
            unit.update_information(unit_data['last_name'],
                                    unit_data['first_name'],
                                    unit_data['middle_name'],
                                    unit_data['description'],
                                    unit_data['images'])
            #unit.last_name_text_edit.setText(unit_data['last_name'])
            #unit.first_name_text_edit.setText(unit_data['first_name'])
            #unit.middle_name_text_edit.setText(unit_data['middle_name'])
            #unit.description.setText(unit_data['description'])
            
            #for pixmap in unit_data['images']:
            #    unit.images.add_pixmap(pixmap)
            
            self.List.addUnit(unit)

  def uploadDB(self):
    self.DBM.save_units(self.List.get_list())

  def manage_list(self):
    self.List.turn_to_manage_mode()

  def generatePDF(self):
    out = QFileDialog.getSaveFileName(self, "Сохранить как", "", "PDF (*.pdf)")
    if out[0] == "":
      return
    PDFMaker().create_pdf(self.List.get_list(), out[0])


  def closeEvent(self, event: QCloseEvent | None) -> None:
    reply = QMessageBox.question(
            self, 
            'Подтверждение',
            'Вы уверены, что хотите закрыть окно? Не забудьте сохраниться.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
    if reply == QMessageBox.StandardButton.Yes:
        # Выполняем действия перед закрытием
        self.autosave.stop_thread()
        event.accept()  # Принимаем закрытие
    else:
        event.ignore() 