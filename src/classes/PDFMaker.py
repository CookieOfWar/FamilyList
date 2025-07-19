import sys
import os
import math

from fpdf import FPDF
import tempfile

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QBuffer, QIODevice, QByteArray, Qt

from classes.ListUnit import ListUnit


def convert_qpixmap_to_file(qpixmap: QPixmap, temp_dir: str, filename_prefix: str, index: int) -> str:
  if qpixmap is None or qpixmap.isNull():
    return None

  try:
    full_filename = os.path.join(temp_dir, f"{filename_prefix}_{index}.png")
    success = qpixmap.save(full_filename, "PNG")
    if success:
      return full_filename
    else:
      print(f"Ошибка при сохранении изображения: {full_filename}")
      return None
  except Exception as e:
    print(f"Исключение при сохранении QPixmap: {e}")
    return None


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

    # Параметры страницы
    self.page_width = 210  # ширина страницы A4 в мм
    self.page_height = 297  # высота страницы A4 в мм
    self.margin = 15       # отступ от краев
    self.spacing = 5       # промежуток между фото
    self.max_images_per_row = 3

  def add_person(self, person: ListUnit):
    page_num = self.pdf.page_no() + 1

    # Добавляем новую страницу для человека
    self.pdf.add_page()
    
    # Заголовок страницы
    self.pdf.set_font("Roboto", 'B', 16)
    full_name = person.get_full_name()
    self.pdf.cell(0, 10, full_name, ln=1, align='C')
    self.pdf.ln(10)

    self.toc_entries.append((full_name, page_num))
    
    # Описание
    self.pdf.set_font("Roboto", size=12)
    self.pdf.multi_cell(0, 7, person.get_description())
    self.pdf.ln(10)
    
    # Добавляем изображения
    self._add_images(person.get_pixmaps())

  def _add_images(self, images):
    if not images:
      return
        
    num_images = len(images)
    usable_width = self.page_width - 2 * self.margin
    current_y = self.pdf.get_y()
    usable_height = self.page_height - current_y - self.margin
    
    # Определяем сетку для изображений
    if num_images == 1:
      cols = 1
    elif num_images == 2:
      cols = 2
    else:
      cols = min(num_images, self.max_images_per_row)
    
    rows = math.ceil(num_images / cols)
    
    # Максимальная ширина и высота для одного изображения
    max_img_width = (usable_width - (cols - 1) * self.spacing) / cols
    max_img_height = (usable_height - (rows - 1) * self.spacing) / rows
    
    # Временные файлы для изображений
    temp_paths = []
    try:
      # Сначала сохраняем все изображения во временные файлы и получаем их размеры
      img_info = []
      for i, pixmap in enumerate(images):
        temp_path = os.path.join(self.temp_dir, f"temp_img_{i}.png")
        pixmap.save(temp_path)
        temp_paths.append(temp_path)
        
        # Получаем размеры изображения (в пикселях)
        width_px = pixmap.width()
        height_px = pixmap.height()
        aspect_ratio = width_px / height_px
        img_info.append((temp_path, aspect_ratio))
      
      # Добавляем изображения в сетку с сохранением пропорций
      for i, (img_path, aspect_ratio) in enumerate(img_info):
        row = i // cols
        col = i % cols
        
        # Рассчитываем размеры с сохранением пропорций
        # Сначала пробуем по ширине
        img_width = max_img_width
        img_height = img_width / aspect_ratio
        
        # Если не помещается по высоте, то подгоняем по высоте
        if img_height > max_img_height:
          img_height = max_img_height
          img_width = img_height * aspect_ratio
        
        # Позиция на странице
        x = self.margin + col * (max_img_width + self.spacing)
        y = current_y + row * (max_img_height + self.spacing)
        
        # Центрируем изображение в ячейке
        x_offset = (max_img_width - img_width) / 2
        y_offset = (max_img_height - img_height) / 2
        
        # Если выходим за пределы страницы, добавляем новую
        if y + max_img_height > self.page_height - self.margin:
          self.pdf.add_page()
          current_y = self.margin
          y = current_y + (i // cols) * (max_img_height + self.spacing)
        
        # Вставляем изображение
        self.pdf.image(img_path, x=x + x_offset, y=y + y_offset, w=img_width, h=img_height)
      
      # Обновляем текущую позицию Y
      last_row = (num_images - 1) // cols
      self.pdf.set_y(current_y + (last_row + 1) * (max_img_height + self.spacing))
    
    finally:
      # Удаляем временные файлы
      for temp_path in temp_paths:
        if os.path.exists(temp_path):
          os.remove(temp_path)

  def _add_toc_page(self):
    # Сохраняем текущую позицию
    current_page = self.pdf.page_no()
    
    # Вставляем страницу оглавления в начало
    self.pdf.insert_page(0)
  
    self.pdf.set_font("Roboto", 'B', 16)
    self.pdf.cell(0, 10, "Оглавление", ln=1, align='C')
    self.pdf.ln(10)
    
    self.pdf.set_font("Roboto", size=12)
    
    # Добавляем пункты оглавления
    for name, page in self.toc_entries:
      # Название персоны
      self.pdf.cell(0, 10, name, ln=0)
      
      # Точки до номера страницы
      self.pdf.cell(0, 10, "." * (70 - len(name)), ln=0)
      
      # Номер страницы
      self.pdf.cell(0, 10, str(page), ln=1, align='R')
    
    # Возвращаемся на последнюю страницу
    self.pdf.set_page(current_page + 1)

  def create_pdf(self, units, filename):
    for i, unit in enumerate(units):
      self.add_person(unit)

    #self._add_toc_page()
    
    self.pdf.output(filename)

    os.rmdir(self.temp_dir)

    print("PDF успешно создан:", filename)