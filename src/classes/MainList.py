from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea, QLabel
from PyQt6.QtCore import Qt

class MainList(QScrollArea):
  def __init__(self):
    super().__init__()
    self.units: list = []

    self.manageMode = False

    self.setupUI()

  def setupUI(self):
    widget = QWidget()
    self.vbox = QVBoxLayout(widget)
    self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.vbox.setContentsMargins(0,0,0,0)
    self.vbox.addStretch(1)

    self.setWidget(widget)
    self.setWidgetResizable(True)

    #self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    #self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    #self.scrollArea.setWidgetResizable(True)
    

  def addUnit(self, unit):
    count = self.vbox.count()
    if count > 0:
      self.vbox.insertWidget(count - 1, unit)
      self.units.append(unit)
    else:
      self.vbox.addWidget(unit)
      self.vbox.addStretch(1)
      self.units.append(unit)

    unit.move_self_signal.connect(self.move_unit)
    unit.kys_signal.connect(self.kill_unit)

  def filterList(self, button_text):
    if button_text.find("Фамилия") != -1:
      self.units.sort(key=lambda u:(
        u.get_last_name().lower(),
        u.get_first_name().lower(),
        u.get_middle_name().lower()
      ), reverse=True if button_text.find("▲") != -1 else False)
    elif button_text.find("Имя") != -1:
      self.units.sort(key=lambda u:(
        u.get_first_name().lower(),
        u.get_last_name().lower(),
        u.get_middle_name().lower()
      ), reverse=True if button_text.find("▲") != -1 else False)
    elif button_text.find("Отчество") != -1:
      self.units.sort(key=lambda u:(
        u.get_middle_name().lower(),
        u.get_last_name().lower(),
        u.get_first_name().lower()
      ), reverse=True if button_text.find("▲") != -1 else False)

    for child in self.vbox.children():
      self.vbox.removeWidget(child)
    for unit in self.units:
      self.vbox.addWidget(unit)

  def turn_to_manage_mode(self, forceTurn=False):
    if forceTurn:
      for unit_index in range(len(self.units)):
        self.units[unit_index].forceHideInfo()
        self.units[unit_index].turn_to_normal_mode()
        self.units[unit_index].turn_to_manage_mode()  
        self.manageMode = True
      return
    for unit_index in range(len(self.units)):
      self.units[unit_index].forceHideInfo()
      if self.manageMode:
        self.units[unit_index].turn_to_normal_mode()
      else:
        self.units[unit_index].turn_to_manage_mode()
    
    self.manageMode = not self.manageMode

  
  def move_unit(self, unit, offset):
    try:
        current_index = self.units.index(unit)
    except ValueError:
        return
    target_index = current_index + offset
    if target_index < 0 or target_index >= len(self.units):
        return
    self.units.pop(current_index)
    self.units.insert(target_index, unit)
    self.vbox.insertWidget(target_index, unit)
    unit.turn_to_manage_mode()

  def kill_unit(self, unit):
    self.vbox.removeWidget(unit)
    unit.deleteLater()
    self.units.remove(unit)

    if len(self.units) == 0:
      self.manageMode = False

  def get_list(self):
    return self.units
  
  def clear_units(self):
        #"""Полностью очищает все юниты из списка и layout"""
        # 1. Удаляем все виджеты из layout
        #while self.vbox.count():
        #    item = self.vbox.takeAt(0)  # Берем первый элемент
        #    widget = item.widget()
        #    if widget:
        #        widget.setParent(None)  # Удаляем родителя
        #        widget.deleteLater()   # Планируем удаление виджета

        print(self.units)
        for unit in self.units:
          #print("killed unit ", unit)
          #self.kill_unit(unit)
          self.vbox.removeWidget(unit)
          unit.deleteLater()
        self.units.clear()
        
        # 2. Очищаем внутренний список
        #self.units.clear()
        self.manageMode = False
        
        # 3. (Опционально) Обновляем интерфейс
        self.updateGeometry()