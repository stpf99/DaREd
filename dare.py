import random
import math

def generate_grid(density=0.3):
    """Generuje siatkę 64x64 z losowymi aktywnymi polami."""
    return [[1 if random.random() < density else 0 for _ in range(64)] for _ in range(64)]

def rotate_90(grid):
    """Obrót siatki o 90 stopni w prawo."""
    return [list(row) for row in zip(*grid[::-1])]

def find_patterns(grid, min_size=2):
    """Wyszukuje kwadratowe wzorce aktywnych pól."""
    patterns = []
    for i in range(64):
        for j in range(64):
            if grid[i][j] == 1:
                for size in range(min_size, 5):
                    if i + size <= 64 and j + size <= 64:
                        subgrid = [row[j:j+size] for row in grid[i:i+size]]
                        if all(cell == 1 for row in subgrid for cell in row):
                            patterns.append((i, j, size, subgrid))
    return patterns

def encode_B(pattern, angle=0, mirror=False, log_step=1):
    """Koduje wzorzec jako komendę 'B' z parametrami."""
    i, j, size, _ = pattern
    angle_code = int(angle / 90) % 4  # 0-3 (0°, 90°, 180°, 270°)
    mirror_code = 1 if mirror else 0
    log_code = int(math.log2(log_step)) if log_step >= 1 else 0
    return f"B{i}{j}{size}{angle_code}{mirror_code}{log_code}"

def encode_grid(grid):
    """Koduje całą siatkę, optymalizując za pomocą funkcji 'A' i 'B'."""
    encoded = []
    
    # Sprawdź optymalny obrót
    original_count = sum(sum(row) for row in grid)
    rotated = rotate_90(grid)
    rotated_count = sum(sum(row) for row in rotated)
    
    if rotated_count < original_count:
        encoded.append('x')
        use_grid = rotated
    else:
        use_grid = grid
    
    # Koduj pojedyncze komórki (A)
    for i in range(64):
        for j in range(64):
            if use_grid[i][j] == 1:
                encoded.append(f"A{chr(48+i)}{chr(48+j)}")
    
    # Koduj wzorce (B) z transformacjami
    patterns = find_patterns(use_grid)
    for pattern in patterns[:2]:  # Ogranicz do 2 wzorców
        encoded.append(encode_B(pattern, angle=90, log_step=2))
    
    return ''.join(encoded)

def save_to_file(encoded_str, filename="encoded_grid.txt"):
    """Zapisuje zakodowany układ do pliku."""
    with open(filename, 'w') as f:
        f.write(encoded_str)

# Przykład użycia
if __name__ == "__main__":
    grid = generate_grid(density=0.4)
    encoded = encode_grid(grid)
    save_to_file(encoded)
    print("Zakodowany układ:", encoded)
