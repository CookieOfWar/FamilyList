from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QMessageBox
)
from PyQt6.QtCore import QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from classes.ImageSelector import ImageSelector
from classes.EditUnitDialog import EditUnitDialog

from utils import resource_path


class ListUnit(QWidget):
    move_self_signal = pyqtSignal(object, int)
    kys_signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.maxTopHeight = 50
        self.maxFullHeight = 300
        self.isOpen = False
        
        self.setupUI()
        self.setupAnimation()

    def setupUI(self):
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Верхняя часть
        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(self.maxTopHeight)
        self.top_layout = QHBoxLayout(self.top_widget)
        
        self.last_name_text_edit = QLabel("Фамилия")
        self.top_layout.addWidget(self.last_name_text_edit)

        self.first_name_text_edit = QLabel("Имя")
        self.top_layout.addWidget(self.first_name_text_edit)

        self.middle_name_text_edit = QLabel("Отчество")
        self.top_layout.addWidget(self.middle_name_text_edit)

        self.more_info_button = QPushButton("▼")
        self.more_info_button.clicked.connect(self.showHideInfo)
        self.more_info_button.setMaximumWidth(50)
        self.top_layout.addWidget(self.more_info_button)

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon(resource_path("img/edit_icon.png")))
        self.edit_button.setFixedSize(20, 20)
        self.edit_button.setIconSize(self.edit_button.size())
        self.edit_button.clicked.connect(self.edit_information)
        self.top_layout.addWidget(self.edit_button)

        self.index_change_text = QTextEdit()
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(resource_path("img/delete_icon.png")))
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.clicked.connect(self.delete_unit)
        self.delete_button.setIconSize(self.delete_button.size())

         # Нижняя часть (контент)
        self.bottom_widget = QWidget()
        self.bottom_layout = QHBoxLayout(self.bottom_widget)
        
        self.description = QLabel("Описание будет здесь")
        self.images = ImageSelector()
        
        self.bottom_layout.addWidget(self.description)
        self.bottom_layout.addWidget(self.images)

        # Добавляем обе части в основной layout
        self.layout().addWidget(self.top_widget)
        self.layout().addWidget(self.bottom_widget)
        
        # Изначально скрываем нижнюю часть
        self.bottom_widget.setMaximumHeight(0)

    def get_last_name(self):
        return self.last_name_text_edit.text()
    def get_first_name(self):
        return self.first_name_text_edit.text()
    def get_middle_name(self):
        return self.middle_name_text_edit.text()
    def get_description(self):
        return self.description.text()
    def get_pixmaps(self):
        return self.images.get_pixmaps()

    def setupAnimation(self):
        self.animation = QPropertyAnimation(self.bottom_widget, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.valueChanged.connect(self.updateParentLayout)

    def showHideInfo(self):
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        if self.isOpen:
            self.animation.setStartValue(self.maxFullHeight - self.maxTopHeight)
            self.animation.setEndValue(0)
            self.more_info_button.setText("▼")
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.maxFullHeight - self.maxTopHeight)
            self.more_info_button.setText("▲")

        self.isOpen = not self.isOpen
        self.animation.start()

    def updateParentLayout(self, height):
        # Обновляем геометрию родителя
        if self.parent():
            self.parent().updateGeometry()

    def edit_information(self):
        self.edit_dialog = EditUnitDialog("" if self.last_name_text_edit.text() == "Фамилия" else self.last_name_text_edit.text(), 
            "" if self.first_name_text_edit.text() == "Имя" else self.first_name_text_edit.text(), 
            "" if self.middle_name_text_edit.text() == "Отчество" else self.middle_name_text_edit.text(), 
            "" if self.description.text() == "Описание будет здесь" else self.description.text(), self.images.get_pixmaps())
        self.edit_dialog.end_of_operation.connect(self.update_information)
        self.edit_dialog.show()
    
    def update_information(self, last_name, first_name, middle_name, description, pixmaps):
        if [last_name, first_name, middle_name, description, pixmaps] == ["", "", "", "", []]:
            return
        self.last_name_text_edit.setText(last_name)
        self.first_name_text_edit.setText(first_name)
        self.middle_name_text_edit.setText(middle_name)
        self.description.setText(description)
        self.images.load_pixmaps(pixmaps)

    
    def turn_to_manage_mode(self, index):
        self.top_layout.removeWidget(self.more_info_button)
        self.more_info_button.hide()
        self.top_layout.removeWidget(self.edit_button)
        self.edit_button.hide()

        self.top_layout.addWidget(self.index_change_text)
        self.top_layout.addWidget(self.delete_button)
        self.index_change_text.show()
        self.delete_button.show()

        self.index_change_text.setText(str(index + 1))

        self.index_change_text.keyPressEvent = self.index_edit_press_event

    
    def turn_to_normal_mode(self):
        self.top_layout.removeWidget(self.index_change_text)
        self.index_change_text.hide()
        self.top_layout.removeWidget(self.delete_button)
        self.delete_button.hide()

        self.top_layout.addWidget(self.more_info_button)
        self.more_info_button.show()
        self.top_layout.addWidget(self.edit_button)
        self.edit_button.show()
    
    def index_edit_press_event(self,  event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            text = self.index_change_text.toPlainText()
            try:
                num = int(text)
            except:
                return
            self.move_self_signal.emit(self, num)
        else:
            QTextEdit.keyPressEvent(self.index_change_text, event)
            
    
    def delete_unit(self):
        mb = QMessageBox(self)
        mb.setWindowTitle("Подтверждение")
        mb.setText("Вы действительно хотите удалить этот элемент?")
        mb.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        button = mb.exec()
        if button == QMessageBox.StandardButton.Yes:
            self.kys_signal.emit(self)

    