import sys
import os
import math
import tempfile
from fpdf import FPDF
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Убран неиспользуемый метод convert_qpixmap_to_file

class PDFMaker:
    def __init__(self):
        self.pdf = FPDF()

        path_to_fonts = os.getcwd() + "/src/"
        self.pdf.add_font('Roboto', '', path_to_fonts + 'Roboto-Regular.ttf', uni=True)
        self.pdf.add_font('Roboto', 'B', path_to_fonts + 'Roboto-Bold.ttf', uni=True)
        self.pdf.add_font('Roboto', 'I', path_to_fonts + 'Roboto-Italic.ttf', uni=True)

        self.pdf.set_auto_page_break(True)
        self.pdf.set_font('Roboto', size=12)

        self.temp_dir = tempfile.mkdtemp()
        self.toc_entries = []

        # ГЛАВНОЕ ИСПРАВЛЕНИЕ: сквозной счетчик для уникальности имен файлов картинок
        self.img_counter = 0 

        # Параметры страницы
        self.page_width = 210  
        self.page_height = 297  
        self.margin = 15       
        self.spacing = 5       
        self.max_images_per_row = 3

    def add_person(self, person):
        page_num = self.pdf.page_no() + 1

        self.pdf.add_page()
        
        self.pdf.set_font("Roboto", 'B', 16)
        full_name = person.get_full_name()
        self.pdf.cell(0, 10, full_name, ln=1, align='C')
        self.pdf.ln(10)

        self.toc_entries.append((full_name, page_num))
        
        self.pdf.set_font("Roboto", size=12)
        self.pdf.multi_cell(0, 7, person.get_description())
        self.pdf.ln(10)
        
        self._add_images(person.get_pixmaps())

    def _add_images(self, images):
        if not images:
            return
            
        num_images = len(images)
        usable_width = self.page_width - 2 * self.margin
        current_y = self.pdf.get_y()
        usable_height = self.page_height - current_y - self.margin
        
        if num_images == 1:
            cols = 1
        elif 2 <= num_images <= 4:
            cols = 2
        else:
            cols = min(num_images, self.max_images_per_row)
        
        rows = math.ceil(num_images / cols)
        
        max_img_width = (usable_width - (cols - 1) * self.spacing) / cols
        max_img_height = (usable_height - (rows - 1) * self.spacing) / rows
        
        temp_paths = []
        try:
            img_info = []
            for pixmap in images:
                # Используем сквозной self.img_counter вместо i локального цикла
                temp_path = os.path.join(self.temp_dir, f"temp_img_{self.img_counter}.png")
                self.img_counter += 1
                
                pixmap.save(temp_path)
                temp_paths.append(temp_path)
                
                width_px = pixmap.width()
                height_px = pixmap.height()
                aspect_ratio = width_px / height_px if height_px > 0 else 1
                img_info.append((temp_path, aspect_ratio))
          
            for i, (img_path, aspect_ratio) in enumerate(img_info):
                row = i // cols
                col = i % cols
                
                img_width = max_img_width
                img_height = img_width / aspect_ratio
                
                if img_height > max_img_height:
                    img_height = max_img_height
                    img_width = img_height * aspect_ratio
                
                x = self.margin + col * (max_img_width + self.spacing)
                y = current_y + row * (max_img_height + self.spacing)
                
                x_offset = (max_img_width - img_width) / 2
                y_offset = (max_img_height - img_height) / 2
                
                if y + max_img_height > self.page_height - self.margin:
                    self.pdf.add_page()
                    current_y = self.margin
                    y = current_y + (i // cols) * (max_img_height + self.spacing)
                
                self.pdf.image(img_path, x=x + x_offset, y=y + y_offset, w=img_width, h=img_height)
          
            last_row = (num_images - 1) // cols
            self.pdf.set_y(current_y + (last_row + 1) * (max_img_height + self.spacing))
        
        finally:
            for temp_path in temp_paths:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    # Добавляем аргумент progress_callback
    def create_pdf(self, units, filename, progress_callback=None):
        for i, unit in enumerate(units):
            self.add_person(unit)
            if progress_callback:
                # Передаем шаг от 1 до N
                progress_callback(i + 1, f"Обработка: {unit.get_full_name()}")

        # Перед тяжелой записью на диск меняем текст, но НЕ ставим максимальное значение
        if progress_callback:
            progress_callback(len(units), "Запись PDF-файла на диск (это может занять время)...")
            
        # Самая долгая операция
        self.pdf.output(filename)

        # Только теперь, когда файл записан, процесс завершен на 100%
        if progress_callback:
            progress_callback(len(units) + 1, "Готово!")

        try:
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Не удалось удалить временную директорию: {e}")