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

class RaceState(typing.TypedDict):
  points: int
  distance: int
  staminaLeft: int
  restLeft: int

def race(reindeer: list[Reindeer], seconds: int) -> list[tuple[str, int]]:
  raceState: list[RaceState] = [
    RaceState(
      points=0,
      distance=0,
      staminaLeft=r['stamina_s'],
      restLeft=0
    ) for r in reindeer
  ]
  
  while seconds > 0:
    leaders: list[int] = []
    leader_distance = -1
    
    for i in range(len(reindeer)):
      r, state = reindeer[i], raceState[i]
      if state['staminaLeft']:
        state['distance'] += r['speed_km_s']
        state['staminaLeft'] -= 1
        if state['staminaLeft'] == 0:
          state['restLeft'] = r['rest_time_s']
      elif state['restLeft']:
        state['restLeft'] -= 1
        if state['restLeft'] == 0:
          state['staminaLeft'] = r['stamina_s']
      else:
        raise RuntimeError(f'Invalid state, expected to either have stamina or rest left: {r} - {state}')
  
      if state['distance'] > leader_distance:
        leaders.clear()
        leaders.append(i)
        leader_distance = state['distance']
      elif state['distance'] == leader_distance:
        leaders.append(i)
        
    # leaders get a point for each second in the lead
    for i in leaders:
      raceState[i]['points'] += 1
      
    seconds -= 1
  
  result: list[tuple[str, int]] = []
  for i in range(len(reindeer)):
    result.append((reindeer[i]['name'], raceState[i]['points']))
  return result

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
  def test_race(self):
    self.assertEqual(
      race([
        Reindeer(name='1', speed_km_s=2, stamina_s=2, rest_time_s=2), # 1, 1, 1, 1, 1
        Reindeer(name='2', speed_km_s=2, stamina_s=1, rest_time_s=2), # 1, 0, 0, 1, 0
      ], 5),
      [('1', 5), ('2', 2)]
    )
    self.assertEqual(
      race([
        Reindeer(name='1', speed_km_s=2, stamina_s=2, rest_time_s=3), # 0, 1, 1, 0, 0
        Reindeer(name='2', speed_km_s=3, stamina_s=1, rest_time_s=2), # 1, 0, 0, 1, 1
      ], 5),
      [('1', 2), ('2', 3)]
    )
    
  def test_race_real_world(self):
    self.assertEqual(
      race([
        Reindeer(name='Comet', speed_km_s=14, stamina_s=10, rest_time_s=127),
        Reindeer(name='Dancer', speed_km_s=16, stamina_s=11, rest_time_s=162),
      ], 1000),
      [('Comet', 312), ('Dancer', 689)]
    )

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
    print(max(map(lambda x: x[1], race(reindeer, 2503))))