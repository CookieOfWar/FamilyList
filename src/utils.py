import os
import sys
import time

from blinker import signal
from PyQt6.QtCore import QTimer, QObject
from classes.DatabaseManager import DatabaseManager
from classes.MainList import MainList

def resource_path(relative_path):
  """Получает абсолютный путь к ресурсу для работы и для сборки."""
  if getattr(sys, 'frozen', False):  # Если программа собрана в EXE
      base_path = os.path.join(sys._MEIPASS)  # Для PyInstaller в режиме onedir
  else:
      base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src"  # Путь к папке src/
  
  return os.path.join(base_path, relative_path)

def start_auto_saving(DBM: DatabaseManager):
  pass

from threading import Timer
class auto_save(QObject): # Наследуем от QObject для корректной работы таймеров Qt
    def __init__(self, DBM: DatabaseManager, List: MainList, main_window):
        super().__init__()
        self.List = List
        self.DBM = DBM
        self.main_window = main_window # Сохраняем ссылку на главное окно для статус-бара
        
        signal("DB_Saved").connect(self.restart_timer)
        
        # Используем безопасный QTimer вместо threading.Timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.save)
        self.timer.start(60000) # 60 секунд

    def save(self):
        if self.DBM.get_db_path() is not None:
            # Выводим неблокирующее сообщение в левый нижний угол окна
            if hasattr(self.main_window, 'statusBar') and self.main_window.menuBar():
                self.main_window.statusBar().showMessage("Автосохранение базы данных...")
            
            # Спокойно сохраняем. Так как мы в главном потоке, крашей не будет.
            self.DBM.save_units(self.List.get_list(), parent_widget=self.main_window, withMessages=False, autosave=True)
        else:
            print("db_path was None while autosaving")
            # Если база еще ни разу не сохранялась ручками, перезапускаем таймер проверки через минуту
            self.timer.start(60000)

    def restart_timer(self, sender, **kwargs):
        if kwargs.get('data'):
            print("successfully autosaved!")
            # Показываем статус "Успешно" в течение 3 секунд
            if hasattr(self.main_window, 'statusBar') and self.main_window.menuBar():
                self.main_window.statusBar().showMessage("База данных автоматически сохранена", 3000)
            
            self.timer.start(60000) # Взводим на следующие 60 секунд
        else:
            print("error while autosaving!!!")
            if hasattr(self.main_window, 'statusBar') and self.main_window.menuBar():
                self.main_window.statusBar().showMessage("Ошибка автосохранения! Повтор через 3 минуты...", 5000)
            
            # Вместо time.sleep(), который намертво вешал бы программу, 
            # мы просто просим таймер сработать не через 60 секунд, а через 180 (3 минуты)
            self.timer.start(180000)

    def stop_thread(self):
        # Метод переименовывать не стал, чтобы не ломать твою логику вызова при закрытии
        if self.timer and self.timer.isActive():
            print("timer stopped")
            self.timer.stop()

    def __del__(self):
        self.stop_thread()