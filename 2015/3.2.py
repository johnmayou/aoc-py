visited: set[tuple[int, int]] = set()
s_x = s_y = 0 # Santa
rb_x = rb_y = 0 # Robot Santa
rb_turn = False
with open('input.txt') as f:
  while (byte := f.read(1)):
    match byte:
      case '>':
        if rb_turn:
          rb_x += 1
        else:
          s_x += 1
      case '<':
        if rb_turn:
          rb_x -= 1
        else:
          s_x -= 1
      case '^':
        if rb_turn:
          rb_y += 1
        else:
          s_y += 1
      case 'v':
        if rb_turn:
          rb_y -= 1
        else:
          s_y -= 1
      case _: raise RuntimeError(f'Unexpected byte: {byte}')
    visited.add((rb_x, rb_y) if rb_turn else (s_x, s_y))
    rb_turn = not rb_turn
print(len(visited))