import sqlite3
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap

class DatabaseManager:
    def __init__(self):
        self.db_path = None

    def save_units(self, units, parent_widget=None):
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
        
        try:
            # Создаем временную копию для безопасного сохранения
            temp_path = file_path + ".tmp"
            
            with sqlite3.connect(temp_path) as conn:
                self._init_db(conn)
                self._write_data(conn, units)
            
            # Если сохранение успешно, заменяем старый файл
            if os.path.exists(file_path):
                os.remove(file_path)
            os.rename(temp_path, file_path)
            
            QMessageBox.information(parent_widget, "Успех", "База данных успешно сохранена!")
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Ошибка", f"Не удалось сохранить данные: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
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
                return self._read_data(conn)
        except Exception as e:
            QMessageBox.critical(parent_widget, "Ошибка", f"Не удалось загрузить данные: {str(e)}")
            return None

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
        
        cursor.execute('DELETE FROM unit_images')
        cursor.execute('DELETE FROM units')
        
        for unit in units:
            cursor.execute('''
            INSERT INTO units (last_name, first_name, middle_name, description)
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
                INSERT INTO unit_images (unit_id, image_data)
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