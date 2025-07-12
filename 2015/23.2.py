import argparse
import textwrap
import unittest
import typing
import sys
import io

def perform(instructions: list[str], register_start_map: dict[str, float]) -> dict[str, float]:
  registers: dict[str, float] = {}
  def reg_get(reg: str) -> float:
    return registers.get(reg, register_start_map[reg])
  
  i = 0
  while i >= 0 and i < len(instructions):
    instr = instructions[i]
    if instr.startswith('hlf'):
      reg = instr[4]
      registers[reg] = reg_get(reg) / 2
      i += 1
    elif instr.startswith('tpl'):
      reg = instr[4]
      registers[reg] = reg_get(reg) * 3
      i += 1
    elif instr.startswith('inc'):
      reg = instr[4]
      registers[reg] = reg_get(reg) + 1
      i += 1
    elif instr.startswith('jmp'):
      i += parse_str_signed_int(instr, start=4, stop=len(instr)-1)
    elif instr.startswith('jie'):
      reg = instr[4]
      if reg_get(reg) % 2 == 0:
        i += parse_str_signed_int(instr, start=7, stop=len(instr)-1)
      else:
        i += 1
    elif instr.startswith('jio'):
      reg = instr[4]
      if reg_get(reg) == 1:
        i += parse_str_signed_int(instr, start=7, stop=len(instr)-1)
      else:
        i += 1
    else:
      raise RuntimeError(f'Invalid instruction: {instr}')
  return registers

def parse_str_signed_int(str: str, start: int, stop: int) -> int:
  num = int(str[start+1:stop+1])
  match str[start]:
    case '-': return -num
    case '+': return num
    case _: raise RuntimeError(f'Invalid signed int operator: {str}')

def parse_instructions(stream: typing.TextIO) -> list[str]:
  instructions: list[str] = []
  line = stream.readline().strip()
  while line:
    instructions.append(line)
    line = stream.readline().strip()
  return instructions

class Tests(unittest.TestCase):
  def test_perform(self):
    self.assertEqual(
      perform([
        'inc a',
        'jio a, +2',
        'tpl a',
        'inc a',
      ], register_start_map={'a': 0}),
      {'a': 2}
    )
    
  def test_parse_instructions(self):
    self.assertEqual(
      parse_instructions(io.StringIO(textwrap.dedent("""\
        inc a
        jio a, +2
        tpl a
        inc a"""))),
      [
        'inc a',
        'jio a, +2',
        'tpl a',
        'inc a',
      ]
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      instructions = parse_instructions(f)
    print(perform(instructions, register_start_map={'a': 1, 'b': 0})['b'])