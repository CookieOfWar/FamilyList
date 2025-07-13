import sqlite3
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, pyqtSignal
from PyQt6.QtGui import QPixmap
from pprint import pprint

import shutil
import time
from blinker import signal

class DatabaseManager:
    def __init__(self):
        self.db_path = None

    def save_units(self, units, parent_widget=None, withMessages=True, autosave=False):
        if not autosave:
          """Сохраняет юниты в выбранный файл БД"""
          default_path = os.path.join(os.getcwd(), "family_list_backup.db")
          file_path, _ = QFileDialog.getSaveFileName(
              parent_widget,
              "Сохранить базу данных",
              default_path,
              "SQLite Database (*.db *.sqlite)"
          )
          
          if not file_path:
              return False

        else:
            file_path = self.db_path
        
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Создаем временную копию для безопасного сохранения
                temp_path = file_path + ".tmp"
                
                with sqlite3.connect(temp_path) as conn:
                    self._init_db(conn)
                    self._write_data(conn, units)

                conn.close()
                
                # Если сохранение успешно, заменяем старый файл
                #if os.path.exists(file_path):
                #    os.remove(file_path)
                #os.rename(temp_path, file_path)

                # Другой метод с shutil
                shutil.copy2(temp_path, file_path)
                os.unlink(temp_path)
                
                if withMessages:
                  QMessageBox.information(parent_widget, "Успех", "База данных успешно сохранена!")
                self.db_path = file_path
                signal("DB_Saved").send(self, data=True)
                return True
            
            except PermissionError as e:
                # Ошибка блокировки файла
                if attempt == max_retries - 1:  # Последняя попытка
                    QMessageBox.critical(
                        parent_widget,
                        "Ошибка",
                        f"Файл занят другим процессом. Закройте его и попробуйте снова.\n\nОшибка: {str(e)}"
                    )
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    signal("DB_Saved").send(self, data=False)
                    return False

                # Предлагаем повторить
                retry = QMessageBox.question(
                    parent_widget,
                    "Ошибка",
                    "Не удалось сохранить файл (возможно, он открыт в другой программе).\nПовторить попытку?",
                    QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Retry
                )

                if retry == QMessageBox.Cancel:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    signal("DB_Saved").send(self, data=False)
                    return False
                
                try:
                    conn.close()
                except:
                    pass
                time.sleep(1)  # Пауза перед повторной попыткой

            except Exception as e:
                # Другие ошибки
                QMessageBox.critical(
                    parent_widget,
                    "Ошибка",
                    f"Неизвестная ошибка при сохранении: {str(e)}"
                )
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    signal("DB_Saved").send(self, data=False)
                return False

        return False

    def load_units(self, parent_widget=None):
        """Загружает юниты из выбранного файла БД"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Загрузить базу данных",
            os.getcwd(),
            "SQLite Database (*.db *.sqlite)"
        )
        
        if not file_path:
            return None
        
        try:
            with sqlite3.connect(file_path) as conn:
                conn.row_factory = sqlite3.Row
                self.db_path = file_path
                return self._read_data(conn)
        except Exception as e:
            QMessageBox.critical(parent_widget, "Ошибка", f"Не удалось загрузить данные: {str(e)}")
            return None
        
    def get_db_path(self):
        return self.db_path

    def _init_db(self, connection):
        """Инициализирует структуру БД"""
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            description TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS unit_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER,
            image_data BLOB,
            FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
        )
        ''')
        connection.commit()

    def _write_data(self, connection, units):
        """Записывает данные в БД"""
        cursor = connection.cursor()
        
        #cursor.execute('DELETE FROM unit_images')
        #cursor.execute('DELETE FROM units')
        
        for unit in units:
            cursor.execute('''
            INSERT OR IGNORE INTO units (last_name, first_name, middle_name, description)
            VALUES (?, ?, ?, ?)
            ''', (
                unit.last_name_text_edit.text(),
                unit.first_name_text_edit.text(),
                unit.middle_name_text_edit.text(),
                unit.description.text()
            ))
            
            unit_id = cursor.lastrowid
            
            for pixmap in unit.images.get_pixmaps():
                image_bytes = self._pixmap_to_bytes(pixmap)
                cursor.execute('''
                INSERT OR IGNORE INTO unit_images (unit_id, image_data)
                VALUES (?, ?)
                ''', (unit_id, image_bytes))
        
        connection.commit()

    def _read_data(self, connection):
        """Читает данные из БД"""
        cursor = connection.cursor()
        units_data = []
        
        cursor.execute('SELECT * FROM units')
        units = cursor.fetchall()
        
        for unit_row in units:
            cursor.execute('SELECT image_data FROM unit_images WHERE unit_id = ?', (unit_row['id'],))
            images = [self._bytes_to_pixmap(row['image_data']) for row in cursor.fetchall()]
            
            units_data.append({
                'last_name': unit_row['last_name'],
                'first_name': unit_row['first_name'],
                'middle_name': unit_row['middle_name'],
                'description': unit_row['description'],
                'images': images
            })

        return units_data

    def _pixmap_to_bytes(self, pixmap):
        """Конвертирует QPixmap в байты"""
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        return bytes(byte_array)

    def _bytes_to_pixmap(self, data):
        """Конвертирует байты в QPixmap"""
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        return pixmap