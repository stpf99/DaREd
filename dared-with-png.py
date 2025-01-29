import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QSize
from PIL import Image
import numpy as np

def rotate_270(grid):
    """Obrót siatki o 270 stopni (odwrotność 90)."""
    return [list(row) for row in zip(*grid)][::-1]

def apply_transform(subgrid, angle, mirror):
    """Stosuje transformacje do wzorca."""
    # Obrót
    for _ in range(angle // 90):
        subgrid = [list(row) for row in zip(*subgrid[::-1])]
    # Odbicie
    if mirror:
        subgrid = [row[::-1] for row in subgrid]
    return subgrid

def decode_grid(encoded_str):
    """Dekoduje string z zakodowanym układem."""
    grid = [[0 for _ in range(64)] for _ in range(64)]
    if not encoded_str:
        return grid
    
    rotate_flag = False
    if encoded_str[0] == 'x':
        rotate_flag = True
        encoded_str = encoded_str[1:]
    
    i = 0
    while i < len(encoded_str):
        cmd = encoded_str[i]
        if cmd == "A":
            # Format: A<row><col>
            row = ord(encoded_str[i+1]) - 48
            col = ord(encoded_str[i+2]) - 48
            if 0 <= row < 64 and 0 <= col < 64:
                grid[row][col] = 1
            i += 3
        elif cmd == "B":
            # Format: B<row><col><size><angle><mirror><log_step>
            row = ord(encoded_str[i+1]) - 48
            col = ord(encoded_str[i+2]) - 48
            size = ord(encoded_str[i+3]) - 48
            angle = (ord(encoded_str[i+4]) - 48) * 90
            mirror = bool(ord(encoded_str[i+5]) - 48)
            log_step = 2 ** (ord(encoded_str[i+6]) - 48)
            
            # Generuj wzorzec i transformuj
            subgrid = [[1 for _ in range(size)] for _ in range(size)]
            subgrid = apply_transform(subgrid, angle, mirror)
            
            # Aplikuj do siatki z uwzględnieniem log_step
            for di in range(size):
                for dj in range(size):
                    ni = row + di * log_step
                    nj = col + dj * log_step
                    if 0 <= ni < 64 and 0 <= nj < 64:
                        grid[ni][nj] = subgrid[di][dj]
            i += 7
        else:
            i += 1
    
    return rotate_270(grid) if rotate_flag else grid

def save_grid_as_png(grid, filename="decoded_grid.png", scale=1):
    """Zapisuje siatkę jako obraz PNG.
    
    Args:
        grid (list[list[int]]): Siatka 64x64 z wartościami 0 i 1
        filename (str): Nazwa pliku wyjściowego
        scale (int): Współczynnik skalowania (1 piksel siatki = scale x scale pikseli w obrazie)
    """
    # Konwertuj siatkę na tablicę numpy
    array = np.array(grid, dtype=np.uint8) * 255
    
    # Stwórz obraz
    img = Image.fromarray(array)
    
    # Jeśli potrzebne skalowanie
    if scale > 1:
        new_size = (64 * scale, 64 * scale)
        img = img.resize(new_size, Image.NEAREST)
    
    # Odwróć kolory (0 -> czarny, 1 -> biały)
    img = Image.fromarray(255 - np.array(img))
    
    # Zapisz
    img.save(filename)

class GridDisplay(QWidget):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Układ 64x64')
        layout = QGridLayout()
        layout.setSpacing(0)
        
        for i in range(64):
            for j in range(64):
                cell = QLabel()
                cell.setFixedSize(QSize(30, 30))
                color = QColor(0, 0, 0) if self.grid[i][j] else QColor(255, 255, 255)
                cell.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
                layout.addWidget(cell, i, j)
        
        self.setLayout(layout)
        self.setFixedSize(30*64 + 16, 30*64 + 16)

def read_encoded_file(filename="encoded_grid.txt"):
    """Odczytuje zakodowany układ z pliku."""
    with open(filename, 'r') as f:
        return f.read().strip()

if __name__ == '__main__':
    encoded = read_encoded_file()
    grid = decode_grid(encoded)
    
    # Zapisz jako PNG
    save_grid_as_png(grid, "decoded_grid.png", scale=1)  # Skalowanie x4 dla lepszej widoczności
    
    app = QApplication(sys.argv)
    window = GridDisplay(grid)
    window.show()
    sys.exit(app.exec_())
