from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QMenuBar, QPushButton, QMessageBox, QFileDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QCoreApplication
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

    self.autosave = auto_save(self.DBM, self.List, self)

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
    self.central_layout.setSpacing(2)
    margins = self.central_layout.contentsMargins()
    self.central_layout.setContentsMargins(margins.left(), 0, margins.right(), margins.bottom())

    # Меню
    menubar = QMenuBar()
    menubar.setContentsMargins(0, 0, 0, 0)
    self.central_layout.insertWidget(0, menubar)
    file_menu = menubar.addMenu("Файл")
    upload_action = file_menu.addAction(
        QIcon(resource_path("img/download_icon.png")), 
        "Открыть базу данных..."
    )
    upload_action.triggered.connect(self.downloadDB)
    download_action = file_menu.addAction(
        QIcon(resource_path("img/upload_icon.png")), 
        "Сохранить базу данных..."
    )
    download_action.triggered.connect(self.uploadDB)


    tool_widget = QWidget()
    tool_layout = QHBoxLayout()
    tool_layout.setContentsMargins(0, 0, 0, 0)
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

    # Старые кнопки сохранения/загрузки
    #download_button = QPushButton()
    #download_button.clicked.connect(self.downloadDB)
    #print("resourse path: " + resource_path("img/download_icon.png"))
    #download_button.setIcon(QIcon(resource_path("img/download_icon.png")))
    #download_button.setFixedSize(40, 40)
    #download_button.setIconSize(download_button.size())

    #upload_button = QPushButton()
    #upload_button.clicked.connect(self.uploadDB)
    #upload_button.setIcon(QIcon(resource_path("img/upload_icon.png")))
    #upload_button.setFixedSize(40, 40)
    #upload_button.setIconSize(upload_button.size())

    #tool_layout.addWidget(download_button)
    #tool_layout.addWidget(upload_button)

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
    """Обработчик загрузки БД с индикатором выполнения"""
    units_data = self.DBM.load_units(self)
    if units_data is not None:
        self.List.clear_units()
        
        # Создаем модальный прогресс-бар для загрузки карточек
        progress = QProgressDialog("Подготовка к загрузке данных...", None, 0, len(units_data), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.show()
        QCoreApplication.processEvents()
        
        # Загружаем новые данные
        for i, unit_data in enumerate(units_data):
            # Обновляем текст и ползунок
            progress.setLabelText(f"Загрузка карточки: {unit_data['last_name']} {unit_data['first_name']}")
            progress.setValue(i)
            QCoreApplication.processEvents()

            unit = ListUnit()
            unit.update_information(unit_data['last_name'],
                                    unit_data['first_name'],
                                    unit_data['middle_name'],
                                    unit_data['description'],
                                    unit_data['images'])

            self.List.addUnit(unit)

        # Успешно завершаем прогресс
        progress.setValue(len(units_data))
        progress.close()

  def uploadDB(self):
    self.DBM.save_units(self.List.get_list())

  def manage_list(self):
    self.List.turn_to_manage_mode()

  def generatePDF(self):
    units = self.List.units
    if not units:
        return

    filename, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "", "PDF файлы (*.pdf)")
    if not filename:
        return

    # ВАЖНО: Максимум ставим на 1 больше, чем количество элементов (запас для записи файла)
    total_steps = len(units) + 1
    
    progress = QProgressDialog("Инициализация генерации PDF...", None, 0, total_steps, self)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)
    
    # ВАЖНО: Запрещаем окну закрываться самостоятельно при достижении максимума
    progress.setAutoClose(False) 
    
    # Явно показываем окно и заставляем Qt отрисовать его структуру на экране ДО цикла
    progress.show()
    QCoreApplication.processEvents()
    
    def on_pdf_progress(value, text):
        progress.setLabelText(text)
        progress.setValue(value)
        # Прокачиваем очередь событий, чтобы окно обновлялось и не зависало
        QCoreApplication.processEvents()

    # Запуск генерации
    maker = PDFMaker()
    maker.create_pdf(units, filename, progress_callback=on_pdf_progress)

    # Закрываем окно вручную, так как автозакрытие отключено
    progress.close()


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