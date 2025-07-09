from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QFileDialog
)
from PyQt6.QtCore import QPropertyAnimation, Qt
from PyQt6.QtGui import QIcon, QPixmap,  QImage

class ImageSelector(QWidget):
  def __init__(self, editmode=False, pixmaps = []):
    super().__init__()
    self.editmode = editmode
    self.pixmaps = pixmaps
    self.current_image_index: int = 0
    self.setupUI()

  def setupUI(self):
    self.vbox = QVBoxLayout()
    self.setLayout(self.vbox)

    self.image_label = QLabel()
    self.image_label.setMaximumSize(200, 250)
    self.image_label.setScaledContents(True)
    self.vbox.addWidget(self.image_label)

    self.hbox = QHBoxLayout()
    self.hbox.setAlignment(Qt.AlignmentFlag.AlignJustify)
    self.vbox.addLayout(self.hbox)

    self.back_button = QPushButton("<")
    self.back_button.clicked.connect(self.previous_image)

    self.next_button = QPushButton(">")
    self.next_button.clicked.connect(self.next_image)
    self.current_image_text = QLabel()

    self.hbox.addWidget(self.back_button)
    self.hbox.addWidget(self.current_image_text)
    self.hbox.addWidget(self.next_button)

    if self.editmode:
      self.delete_button = QPushButton("Удалить")
      self.delete_button.clicked.connect(self.delete_image)
      self.upload_button = QPushButton("Загрузить")
      self.upload_button.clicked.connect(self.upload_image)
      self.bottom_hbox = QHBoxLayout()

      self.bottom_hbox.addWidget(self.delete_button)
      self.bottom_hbox.addWidget(self.upload_button)
      self.vbox.addLayout(self.bottom_hbox)

  def previous_image(self):
    if self.pixmaps == None:
      return
    self.current_image_index -= 1
    if self.current_image_index < 0:
      self.current_image_index = len(self.pixmaps) - 1
    self.update_current_image_index()

  def next_image(self):
    if self.pixmaps == []:
      return
    self.current_image_index += 1
    if self.current_image_index >= len(self.pixmaps):
      self.current_image_index = 0
    self.update_current_image_index()

  def update_current_image_index(self):
    if self.current_image_index >= len(self.pixmaps):
      self.current_image_index = len(self.pixmaps) - 1
    self.current_image_text.setText(f"{self.current_image_index + 1}/{len(self.pixmaps)}")
    if len(self.pixmaps) == 0:
      self.image_label.setPixmap(QPixmap())
    else:
      self.image_label.setPixmap(self.pixmaps[self.current_image_index])

  def delete_image(self):
    if self.pixmaps == []:
      return
    self.pixmaps.pop(self.current_image_index)
    
    self.update_current_image_index()

  def upload_image(self):
    fd = QFileDialog(self, "Выбрать картинку", "", "Картинка (*.jpg *.png)")
    image_url = fd.getOpenFileName(self, 'Выбрать картинку', '')[0]
    print(image_url)
    pixmap = QPixmap(QImage(image_url))
    self.pixmaps.append(pixmap)
    self.update_current_image_index()

  def get_pixmaps(self):
    return self.pixmaps
  
  def load_pixmaps(self, pixmaps):
    self.pixmaps = pixmaps
    self.current_image_index = 0
    self.update_current_image_index()

  def add_pixmap(self, pixmap):
        """
        Добавляет изображение в коллекцию и создает его отображение
        :param pixmap: QPixmap - добавляемое изображение
        """
        if pixmap.isNull():
            return False

        try:
            # Сохраняем оригинал
            self.pixmaps.append(pixmap)
            
            # Создаем миниатюру для отображения
            #thumbnail = pixmap.scaled(
            #    100, 100,
            #    Qt.AspectRatioMode.KeepAspectRatio,
            #    Qt.TransformationMode.SmoothTransformation
            #)
            
            # Создаем QLabel для отображения
            self.image_label.setPixmap(pixmap)
            
            return True
        except Exception as e:
            print(f"Ошибка добавления изображения: {e}")
            return False

