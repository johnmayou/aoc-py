import argparse
import unittest
import typing
import sys
import io
import re

class Reindeer(typing.TypedDict):
  name: str
  speed_km_s: int
  stamina_s: int
  rest_time_s: int

def calc_distance(reindeer: Reindeer, seconds: int) -> int:
  distance = 0
  staminaLeft = reindeer['stamina_s']
  while seconds > 0:
    if staminaLeft:
      distance += reindeer['speed_km_s']
      seconds -= 1
      staminaLeft -= 1
    else:
      seconds -= reindeer['rest_time_s']
      staminaLeft = reindeer['stamina_s']
  return distance

def parse_reindeer(stream: typing.TextIO) -> list[Reindeer]:
  reindeer: list[Reindeer] = []
  
  line = stream.readline()
  while line:
    capture = re.match(r'(\w+) can fly (\d+) km/s for (\d+) seconds, but then must rest for (\d+) seconds.', line)
    if not capture: raise RuntimeError(f'Invalid line, did not match expected format: "{line}"')
    
    name, speed_km_s, stamina_s, rest_time_s = capture.groups()
    reindeer.append(Reindeer(
      name=name,
      speed_km_s=int(speed_km_s),
      stamina_s=int(stamina_s),
      rest_time_s=int(rest_time_s),
    ))
    
    line = stream.readline()
    
  return reindeer

class Tests(unittest.TestCase):
  def test_calc_distance(self):
    self.assertEqual(2, calc_distance(Reindeer(name='', speed_km_s=2, stamina_s=1, rest_time_s=2), 1))
    self.assertEqual(2, calc_distance(Reindeer(name='', speed_km_s=2, stamina_s=1, rest_time_s=2), 2))
    self.assertEqual(2, calc_distance(Reindeer(name='', speed_km_s=2, stamina_s=1, rest_time_s=2), 3))
    self.assertEqual(4, calc_distance(Reindeer(name='', speed_km_s=2, stamina_s=1, rest_time_s=2), 4))
    self.assertEqual(4, calc_distance(Reindeer(name='', speed_km_s=2, stamina_s=1, rest_time_s=2), 5))

  def test_parse_reindeer(self):
    self.assertEqual(
      parse_reindeer(io.StringIO('Dancer can fly 27 km/s for 5 seconds, but then must rest for 132 seconds.')),
      [Reindeer(
        name='Dancer',
        speed_km_s=27,
        stamina_s=5,
        rest_time_s=132,
      )]
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('input.txt') as f:
      reindeer = parse_reindeer(f)
    print(max(calc_distance(r, 2503) for r in reindeer))