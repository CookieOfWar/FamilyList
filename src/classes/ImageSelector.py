import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage

class ImageSelector(QWidget):
    # Исправлено: заменяем мутабельный [] на None
    def __init__(self, editmode=False, pixmaps=None):
        super().__init__()
        self.editmode = editmode
        # Если список не передан, создаем новый для каждого инстанса отдельно
        self.pixmaps = pixmaps if pixmaps is not None else []
        self.current_image_index: int = 0
        self.setupUI()

    def setupUI(self):
        self.vbox = QVBoxLayout()
        # Убираем лишние отступы по краям, чтобы виджет вставал вплотную
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

        self.setMaximumHeight(300)

        self.image_label = QLabel()
        # Центрируем картинку внутри QLabel, если пропорции не совпадают
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ГЛАВНОЕ РЕШЕНИЕ: Заставляем QLabel игнорировать размер самого Pixmap.
        # Теперь он будет гибко сжиматься и расширяться в зависимости от окна.
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        # Задаем минимальный размер, ниже которого картинка не схлопнется (вместо фиксированного)
        self.image_label.setMinimumSize(150, 150)
        
        self.vbox.addWidget(self.image_label, stretch=1)  # stretch=1 дает приоритет растяжения картинке

        self.hbox = QHBoxLayout()
        self.vbox.addLayout(self.hbox)

        self.back_button = QPushButton("<")
        self.back_button.setFixedWidth(40) # Делаем стрелочки аккуратными кнопками
        self.back_button.clicked.connect(self.previous_image)

        self.next_button = QPushButton(">")
        self.next_button.setFixedWidth(40)
        self.next_button.clicked.connect(self.next_image)
        
        self.current_image_text = QLabel()
        self.current_image_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hbox.addWidget(self.back_button)
        self.hbox.addWidget(self.current_image_text, stretch=1)
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

        self.update_current_image_index()

    # Автоматическое масштабирование при изменении размеров виджета пользователем
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_display()

    def previous_image(self):
        if not self.pixmaps:
            return
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.pixmaps) - 1
        self.update_current_image_index()

    def next_image(self):
        if not self.pixmaps:
            return
        self.current_image_index += 1
        if self.current_image_index >= len(self.pixmaps):
            self.current_image_index = 0
        self.update_current_image_index()

    def update_current_image_index(self):
        # Корректируем индекс, если он вышел за рамки (например, после удаления)
        if self.current_image_index >= len(self.pixmaps):
            self.current_image_index = max(0, len(self.pixmaps) - 1)
            
        if not self.pixmaps:
            self.current_image_text.setText("0/0")
        else:
            self.current_image_text.setText(f"{self.current_image_index + 1}/{len(self.pixmaps)}")
            
        self.update_image_display()

    # Выносим отрисовку в отдельный метод, который вызывается и при листании, и при ресайзе
    def update_image_display(self):
        if not self.pixmaps or self.image_label.width() <= 1 or self.image_label.height() <= 1:
            self.image_label.setPixmap(QPixmap())
            return

        # Берем текущий оригинальный pixmap
        current_pixmap = self.pixmaps[self.current_image_index]
        
        # Масштабируем с сохранением пропорций под текущий (!) размер QLabel
        scaled_pixmap = current_pixmap.scaled(
            self.image_label.width(), 
            self.image_label.height(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def delete_image(self):
        if not self.pixmaps:
            return
        self.pixmaps.pop(self.current_image_index)
        self.update_current_image_index()

    def upload_image(self):
        # Исправлено: корректная обработка отмены диалога (Cancel)
        image_url, _ = QFileDialog.getOpenFileName(self, "Выбрать картинку", "", "Картинка (*.jpg *.jpeg *.png)")
        if not image_url: 
            return # Если пользователь нажал отмену — ничего не делаем

        pixmap = QPixmap(image_url)
        if not pixmap.isNull():
            self.pixmaps.append(pixmap)
            # Переключаемся на только что добавленное фото
            self.current_image_index = len(self.pixmaps) - 1
            self.update_current_image_index()

    def get_pixmaps(self):
        return self.pixmaps
      
    def load_pixmaps(self, pixmaps):
        self.pixmaps = pixmaps if pixmaps is not None else []
        self.current_image_index = 0
        self.update_current_image_index()

    def add_pixmap(self, pixmap):
        if pixmap is None or pixmap.isNull():
            return False
        try:
            self.pixmaps.append(pixmap)
            # Исправлено: теперь принудительно обновляем UI и индекс, чтобы новое фото отобразилось
            self.current_image_index = len(self.pixmaps) - 1
            self.update_current_image_index()
            return True
        except Exception as e:
            print(f"Ошибка добавления изображения: {e}")
            return False