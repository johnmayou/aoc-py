visited: set[tuple[int, int]] = set()
x = y = 0
with open('input.txt') as f:
  while (byte := f.read(1)):
    match byte:
      case '>': x += 1
      case '<': x -= 1
      case '^': y += 1
      case 'v': y -= 1
      case _: raise RuntimeError(f'Unexpected byte: {byte}')
    visited.add((x, y))
print(len(visited))