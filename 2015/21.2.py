from __future__ import annotations
import argparse
import unittest
import textwrap
import typing
import copy
import sys
import io
import re

ATTACK_MIN_DAMAGE = 1
N_RINGS_ALLOWED = {0, 1, 2}

class Shop(typing.TypedDict):
  weapons: list[Item]
  armor: list[Item]
  rings: list[Item]

class Item(typing.TypedDict):
  name: str
  cost: int
  damage: int
  armor: int
  
class Boss:
  def __init__(self, hp: int, damage: int, armor: int):
    self.hp = hp
    self.damage = damage
    self.armor = armor

class Player:
  def __init__(self, hp: int, inventory: typing.Optional[Inventory] = None):
    self.hp = hp
    self.inventory = inventory if inventory else Inventory()
    
  def damage(self) -> int:
    return self.inventory.total_damage()
  
  def armor(self) -> int:
    return self.inventory.total_armor()
    
class Inventory():
  
  class InvalidInventory(Exception): pass
  
  def __init__(self):
    self.weapon: typing.Optional[Item] = None
    self.armor: typing.Optional[Item] = None
    self.rings: list[Item] = []
    
  def validate(self) -> None:
    if not self.weapon:
      raise self.InvalidInventory('Must have weapon in inventory!')
    if not 0 <= len(self.rings) <= 2:
      raise self.InvalidInventory('Must have between 0 and 2 rings!')
    
  def set_weapon(self, weapon: Item) -> None:
    self.weapon = weapon
  
  def set_armor(self, armor: typing.Optional[Item]) -> None:
    self.armor = armor
  
  def set_rings(self, rings: list[Item]) -> None:
    self.rings = rings
    
  def total_cost(self) -> int:
    cost = 0
    if self.weapon:
        cost += self.weapon['cost']
    if self.armor:
        cost += self.armor['cost']
    if self.rings:
        cost += sum(r['cost'] for r in self.rings)
    return cost
  
  def total_damage(self) -> int:
    damage = 0
    if self.weapon:
        damage += self.weapon['damage']
    if self.armor:
        damage += self.armor['damage']
    if self.rings:
        damage += sum(r['damage'] for r in self.rings)
    return damage
  
  def total_armor(self) -> int:
    armor = 0
    if self.weapon:
        armor += self.weapon['armor']
    if self.armor:
        armor += self.armor['armor']
    if self.rings:
        armor += sum(r['armor'] for r in self.rings)
    return armor

def find_worst_losing_gold_spend(*, player: Player, boss: Boss, shop: Shop) -> int:
  max_gold = -float('inf')
  
  # weapon combinations (1 required)
  weapon_c = shop['weapons']
  
  # armor combinations (between 0 and 1)
  armor_c = shop['armor'] + [None]
  
  # ring combinations (between 0 and 2)
  rings_c = ring_combinations(shop['rings'])
  
  for weapon in weapon_c:
    for armor in armor_c:
      for rings in rings_c:
        player_c = copy.deepcopy(player)
        player_c.inventory.set_weapon(weapon)
        player_c.inventory.set_armor(armor)
        player_c.inventory.set_rings(rings)
        player_c.inventory.validate()
        
        if not play(player=player_c, boss=copy.deepcopy(boss)):
          max_gold = max(max_gold, player_c.inventory.total_cost())
  
  return int(max_gold)

def ring_combinations(
  rings: list[Item],
  n_rings_allowed: set[int] = N_RINGS_ALLOWED
) -> list[list[Item]]:
  rings_c: list[list[Item]] = []
  
  max_n_rings_allowed = max(n_rings_allowed)
  curr_rings: list[Item] = []
  def rings_c_dfs(start: int) -> None:
    if len(curr_rings) in n_rings_allowed:
      rings_c.append(curr_rings.copy()) # shallow copy is okay here
    if len(curr_rings) == max_n_rings_allowed:
      return
    
    for i in range(start, len(rings)):
      curr_rings.append(rings[i])
      rings_c_dfs(i + 1)
      curr_rings.pop()
    
  rings_c_dfs(0)
  return rings_c

def play(*, player: Player, boss: Boss) -> bool:
  """Returns if the player wins or not."""
  while True:
    # player turn
    boss.hp -= max(player.damage() - boss.armor, ATTACK_MIN_DAMAGE)
    if boss.hp <= 0:
      return True
    
    # boss turn
    player.hp -= max(boss.damage - player.armor(), ATTACK_MIN_DAMAGE)
    if player.hp <= 0:
      return False

def parse_boss(stream: typing.TextIO) -> Boss:
  text = stream.read()
  
  hp_match = re.search(r'Hit Points: (\d+)', text)
  damage_match = re.search(r'Damage: (\d+)', text)
  armor_match = re.search(r'Armor: (\d+)', text)
  
  if not (hp_match and damage_match and armor_match):
    raise RuntimeError(f'Unable to parse boss: {text}')
  
  return Boss(
    hp=int(hp_match.group(1)),
    damage=int(damage_match.group(1)),
    armor=int(armor_match.group(1)),
  )

def parse_shop(stream: typing.TextIO) -> Shop:
  weapons = parse_shop_table(stream)
  armor = parse_shop_table(stream)
  rings = parse_shop_table(stream)
  return Shop(weapons=weapons, armor=armor, rings=rings)
  
def parse_shop_table(stream: typing.TextIO) -> list[Item]:
  items: list[Item] = []
  
  stream.readline() # skip header
  
  line = stream.readline().strip()
  while line:
    capture = re.match(r'(.+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
    if not capture: raise RuntimeError(f'Unable to find item data from line item: "{line}"')
    
    name, cost, damage, armor = capture.groups()
    items.append(Item(
      name=name.strip(),
      cost=int(cost),
      damage=int(damage),
      armor=int(armor),
    ))
    
    line = stream.readline().strip()
    
  return items

class Tests(unittest.TestCase):
  def test_ring_combinations(self):
    r1 = Item(name='1', cost=1, damage=1, armor=1)
    r2 = Item(name='2', cost=2, damage=2, armor=2)
    r3 = Item(name='3', cost=3, damage=3, armor=3)

    # allow 1
    self.assertEqual(
      {frozenset(item['name'] for item in subset) for subset in ring_combinations([r1, r2, r3], n_rings_allowed={1})},
      {frozenset(item['name'] for item in subset) for subset in [[r1], [r2], [r3]]},
    )
    
    # allow 0, 1, or 2
    self.assertEqual(
      {frozenset(item['name'] for item in subset) for subset in ring_combinations([r1, r2, r3], n_rings_allowed={0, 1, 2})},
      {frozenset(item['name'] for item in subset) for subset in typing.cast(list[list[Item]], [[], [r1], [r2], [r3], [r1, r2], [r1, r3], [r2, r3]])},
    )
  
  def test_play(self):
    player = Player(hp=0)
    player.inventory.set_weapon(Item(name='', cost=0, damage=5, armor=0))
    player.inventory.set_armor(Item(name='', cost=0, damage=0, armor=5))
    
    # win
    player.hp = 8
    self.assertTrue(play(player=player, boss=Boss(hp=12, damage=7, armor=2)))
    
    # lose
    player.hp = 6
    self.assertFalse(play(player=player, boss=Boss(hp=12, damage=7, armor=2)))
  
  def test_parse_boss(self):
    boss = parse_boss(io.StringIO('Hit Points: 10\nDamage: 11\nArmor: 12'))
    self.assertEqual(boss.hp, 10)
    self.assertEqual(boss.damage, 11)
    self.assertEqual(boss.armor, 12)
  
  def test_parse_shop_table(self):
    # single digits
    self.assertEqual(
      parse_shop_table(io.StringIO(textwrap.dedent("""\
        Weapons:    Cost  Damage  Armor
        Weapon        1     2       3
      """))),
      [Item(name='Weapon', cost=1, damage=2, armor=3)]
    )
    
    # multiple digits
    self.assertEqual(
      parse_shop_table(io.StringIO(textwrap.dedent("""\
        Weapons:    Cost  Damage  Armor
        Weapon       10     20     30
      """))),
      [Item(name='Weapon', cost=10, damage=20, armor=30)]
    )
    
    # +1 in name
    self.assertEqual(
      parse_shop_table(io.StringIO(textwrap.dedent("""\
        Weapons:    Cost  Damage  Armor
        Weapon +1     1     2       3
      """))),
      [Item(name='Weapon +1', cost=1, damage=2, armor=3)]
    )

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]])
  else:
    with open('boss.txt') as f:
      boss = parse_boss(f)
      
    with open('shop.txt') as f:
      shop = parse_shop(f)
      
    gold = find_worst_losing_gold_spend(
      player=Player(hp=100),
      boss=boss,
      shop=shop
    )
    
    print(gold)