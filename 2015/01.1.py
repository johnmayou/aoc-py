floor = 0
with open('1.1-input.txt') as f:
  while (byte := f.read(1)):
    match byte:
      case '(': floor += 1
      case ')': floor -= 1
      case _: raise RuntimeError(f'Unexpected byte: {byte}')
print(floor)