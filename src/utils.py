import os
import sys
import time

from blinker import signal

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
class auto_save():
  def __init__(self, DBM: DatabaseManager, List: MainList):
    self.List = List
    self.DBM = DBM
    self.timer: Timer = None
    signal("DB_Saved").connect(self.restart_timer)
    self.timer = Timer(60, self.save)
    self.timer.start()

  def save(self):
    if self.DBM.get_db_path != None:
      self.DBM.save_units(self.List.get_list(), withMessages=False, autosave=True)
    else:
      print("db_path was None while autosaving")

  def restart_timer(self, sender, **kwargs):
    if kwargs['data']:
      print("successfully autosaved!")
      self.timer = Timer(60, self.save)
      self.timer.start()
    else:
      print("error while autosaving!!!")
      time.sleep(180)
      self.timer = Timer(60, self.save)
      self.timer.start()

  def stop_thread(self):
    if self.timer != None and self.timer.is_alive():
      print("timer stopped")
      self.timer.cancel()

  def __del__(self):
    self.stop_thread()