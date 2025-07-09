from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea
)
from PyQt6.QtCore import QPropertyAnimation, Qt
from PyQt6.QtGui import QIcon

from classes.ImageSelector import ImageSelector
from classes.EditUnitDialog import EditUnitDialog


class ListUnit(QWidget):
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

        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(self.maxTopHeight)
        self.top_layout = QHBoxLayout(self.top_widget)
        
        self.last_name_text_edit = QLabel("Фамилия")
        #self.last_name_text_edit.setPlaceholderText("Фамилия")
        self.top_layout.addWidget(self.last_name_text_edit)

        self.first_name_text_edit = QLabel("Имя")
        #self.first_name_text_edit.setPlaceholderText("Имя")
        self.top_layout.addWidget(self.first_name_text_edit)

        self.middle_name_text_edit = QLabel("Отчество")
        #self.middle_name_text_edit.setPlaceholderText("Отчество")
        self.top_layout.addWidget(self.middle_name_text_edit)

        self.more_info_button = QPushButton("▼")
        self.more_info_button.clicked.connect(self.showHideInfo)
        self.more_info_button.setMaximumWidth(50)
        self.top_layout.addWidget(self.more_info_button)

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon("src/img/edit_icon.png"))
        self.edit_button.setFixedSize(20, 20)
        self.edit_button.setIconSize(self.edit_button.size())
        #self.edit_button.setStyleSheet("background-color: transparent;")
        self.edit_button.clicked.connect(self.edit_information)
        self.top_layout.addWidget(self.edit_button)

        self.bottom_widget = QWidget()
        self.bottom_widget.setFixedHeight(self.maxFullHeight - self.maxTopHeight)
        self.bottom_layout = QVBoxLayout(self.bottom_widget)

        self.description = QLabel()
        self.images = ImageSelector()

        self.additionalHbox = QHBoxLayout()
        self.additionalHbox.addWidget(self.description)
        self.additionalHbox.addWidget(self.images)
        self.bottom_layout.addLayout(self.additionalHbox)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.bottom_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setMaximumHeight(0)

        self.layout().addWidget(self.top_widget)
        self.layout().addWidget(self.scroll_area)

    def setupAnimation(self):
        self.animation = QPropertyAnimation(self.scroll_area, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.valueChanged.connect(self.update_parent_height)
        
    def showHideInfo(self):
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        if self.isOpen:
            self.animation.setStartValue(self.height())
            self.animation.setEndValue(0)
            self.more_info_button.setText("▼")
        else:
            self.animation.setStartValue(self.height())
            self.animation.setEndValue(self.maxFullHeight)
            self.more_info_button.setText("▲")

        self.isOpen = not self.isOpen
        self.animation.start()

    def update_parent_height(self, height):
        print("Max height: ", self.maximumHeight())
        # Обновляем высоту родительского виджета (если он в QScrollArea)
        parent = self.parent()
        if parent:
            parent.updateGeometry()

    def edit_information(self):
        self.edit_dialog = EditUnitDialog()
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