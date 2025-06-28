from __future__ import annotations
import itertools
import argparse
import unittest
import typing
import heapq
import enum
import copy
import sys

class GameTurn(enum.Enum):
  PLAYER = enum.auto()
  BOSS = enum.auto()

class GameState:  
  def __init__(
    self,
    *,
    player: Player,
    boss: Boss,
  ) -> None:
    self.player = player
    self.boss = boss
    self.active_spells: list[Spell] = []
    self.active_spell_types: set[type[Spell]] = set()
    self.turn = GameTurn.PLAYER
    
  def current_actor(self) -> GameEntity:
    return typing.cast(GameEntity, self.player if self.turn == GameTurn.PLAYER else self.boss)
  
  def current_opponent(self) -> GameEntity:
    return typing.cast(GameEntity, self.boss if self.turn == GameTurn.PLAYER else self.player)

class Game:
  
  class SpellAlreadyActive(Exception): pass
  class InsufficientMana(Exception): pass
  
  def __init__(
    self,
    *,
    state: GameState
  ) -> None:
    self.state = state
    
  def cast_spell(self, spell_cls: type[Spell]) -> None:
    if spell_cls in self.state.active_spell_types:
      raise self.SpellAlreadyActive(f'{spell_cls.__name__} is already an active spell')
    
    if (actor := self.state.current_actor()) and isinstance(actor, Player):
      if actor.mana <= 0:
        raise self.InsufficientMana
      actor.mana -= spell_cls.cost()
    
    spell = spell_cls(self.state)
    spell.instant()
    if spell.has_effect:
      self.state.active_spell_types.add(spell_cls)
      self.state.active_spells.append(spell)
      
  def start_turn(self) -> None:
    if not self.state.active_spells:
      return
    
    new_active_spells: list[Spell] = []
    for spell in self.state.active_spells:
      spell_left = spell.effect()
      if spell_left:
        new_active_spells.append(spell)
    self.state.active_spells = new_active_spells
    self.state.active_spell_types = set(map(lambda s: type(s), self.state.active_spells))
  
  def end_turn(self) -> None:
    self.state.turn = GameTurn.BOSS if self.state.turn == GameTurn.PLAYER else GameTurn.PLAYER
    
  def is_over(self) -> bool:
    return self.state.boss.hp <= 0 or self.state.player.hp <= 0

@typing.runtime_checkable
class HasHp(typing.Protocol):
  hp: int
  
@typing.runtime_checkable
class HasArmor(typing.Protocol):
  armor: int

class GameEntity(HasHp, HasArmor):
  pass
      
class Player:
  def __init__(self, hp: int, mana: int) -> None:
    self.hp = hp
    self.armor = 0
    self.mana = mana
    
class Boss:
  def __init__(self, hp: int, damage: int) -> None:
    self.hp = hp
    self.armor = 0
    self.damage = damage

@typing.runtime_checkable
class Spell(typing.Protocol):  
  has_effect: bool
    
  @classmethod
  def cost(cls) -> int: return 0
  
  def __init__(self, game_state: GameState) -> None: pass
  def instant(self) -> None: pass
  def effect(self) -> bool: return False # if the effect still has remaining turns left
  
class MagicMissileSpell:
  def __init__(self, game_state: GameState) -> None:
    self.has_effect = False
    self._opponent = game_state.current_opponent()
    
  @classmethod
  def cost(cls) -> int:
    return 53
    
  def instant(self) -> None:
    self._opponent.hp -= 4
    
  def effect(self) -> bool:
    return False
  
class DrainSpell:
  def __init__(self, game_state: GameState) -> None:
    self.has_effect = False
    self._actor = game_state.current_actor()
    self._opponent = game_state.current_opponent()
    
  @classmethod
  def cost(cls) -> int:
    return 73  
    
  def instant(self) -> None:
    self._actor.hp += 2
    self._opponent.hp -= 2
    
  def effect(self) -> bool:
    return False
    
class ShieldSpell:
  def __init__(self, game_state: GameState) -> None:
    self.has_effect = True
    self._turns_left = 6
    self._first_turn = True
    self._actor = game_state.current_actor()
    
  @classmethod
  def cost(cls) -> int:
    return 113
  
  def instant(self) -> None:
    pass
  
  def effect(self) -> bool:
    if self._first_turn:
      self._actor.armor += 7
      self._first_turn = False
    self._turns_left -= 1
    if self._turns_left:
      return True
    else:
      self._actor.armor -= 7
      return False
    
class PoisonSpell:
  def __init__(self, game_state: GameState) -> None:
    self.has_effect = True
    self._turns_left = 6
    self._opponent = game_state.current_opponent()
    
  @classmethod
  def cost(cls) -> int:
    return 173  
    
  def instant(self) -> None:
    pass
    
  def effect(self) -> bool:
    self._opponent.hp -= 3
    self._turns_left -= 1
    return bool(self._turns_left)
  
class RechargeSpell:
  
  @typing.runtime_checkable
  class HasMana(typing.Protocol):
    mana: int
  
  def __init__(self, game_state: GameState) -> None:
    self.has_effect = True
    self._turns_left = 5
    if (actor := game_state.current_actor()) and not hasattr(actor, 'mana'):
      raise RuntimeError(f'Actor must have mana attribute for recharge spell: {actor}')
    self._actor = typing.cast(RechargeSpell.HasMana, actor)
    
  @classmethod  
  def cost(cls) -> int:
    return 229
    
  def instant(self) -> None:
    pass
    
  def effect(self) -> bool:
    self._actor.mana += 101
    self._turns_left -= 1
    return bool(self._turns_left)
  
SPELLS_TYPES: list[type[Spell]] = [MagicMissileSpell, DrainSpell, ShieldSpell, PoisonSpell, RechargeSpell]

def play(initial_game: Game) -> int:
  min_mana = float('inf')
  
  counter = itertools.count()
  heap: list[tuple[int, int, Game, list[type[Spell]]]] = [(0, next(counter), initial_game, [])]
  while heap:
    curr_mana_spent, _, game, curr_spells = heapq.heappop(heap)
    if curr_mana_spent >= min_mana:
      continue
    
    for spell in SPELLS_TYPES:
      new_game = copy.deepcopy(game)
      
      # == player turn ==
      new_game.start_turn()
      new_game.state.player.hp -= 1
      if new_game.is_over():
        if new_game.state.player.hp > 0:
          min_mana = min(min_mana, curr_mana_spent)
        continue
      try:
        new_game.cast_spell(spell)
      except Game.InsufficientMana:
        continue # not a solution
      except Game.SpellAlreadyActive:
        continue # not a solution
      if new_game.is_over():
        if new_game.state.player.hp > 0:
          min_mana = min(min_mana, curr_mana_spent + spell.cost())
        continue
      new_game.end_turn()
      
      # == boss turn ==
      new_game.start_turn()
      if new_game.is_over():
        if new_game.state.player.hp > 0:
          min_mana = min(min_mana, curr_mana_spent + spell.cost())
        continue
      new_game.state.player.hp -= max(1, new_game.state.boss.damage - new_game.state.player.armor)
      if new_game.is_over():
        if new_game.state.player.hp > 0:
          min_mana = min(min_mana, curr_mana_spent + spell.cost())
        continue
      new_game.end_turn()
      
      heapq.heappush(heap, (curr_mana_spent + spell.cost(), next(counter), new_game, curr_spells + [spell]))
        
  return int(min_mana)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    unittest.main(argv=[sys.argv[0]], buffer=False)
  else:
    game = Game(
      state=GameState(
        player=Player(hp=50, mana=500),
        boss=Boss(hp=71, damage=10),
      )
    )
    
    print(play(game))