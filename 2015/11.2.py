import argparse
import typing
import sys

ALPHABET_LOWER = [chr(unicode) for unicode in range(97, 123)]

def valid_password(password: str) -> bool:
  if len(password) != 8:
    return False
  
  increasing_straight = False
  pairs_seen: int = 0
  pair: typing.Optional[str] = None
  
  for i in range(len(password)):
    ch = password[i]
    
    if ch == 'i' or ch == 'o' or ch == 'l':
      return False
    
    if not increasing_straight and i + 2 < len(password) and (
      ord(ch) + 1 == ord(password[i + 1]) and
      ord(ch) + 2 == ord(password[i + 2])
    ):
      increasing_straight = True
      
    if pair and pair[0] == ch:
      pairs_seen += 1
      pair = None
    else:
      pair = ch
      
  if not increasing_straight:
    return False
  
  if pairs_seen < 2:
    return False
    
  return True

def next_password(password: str) -> str:
  pw = list(password)
  
  def rotate(i: int) -> None:
    if pw[i] == 'z':
      pw[i] = 'a'
      if i > 0:
        rotate(i - 1)
    else:
      pw[i] = chr(ord(pw[i]) + 1)
  
  while True:
    rotate(len(pw) - 1)
    
    password = ''.join(pw)
    if valid_password(password):
      return password

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', '--test', action='store_true')
args = arg_parser.parse_args()

if __name__ == '__main__':
  if args.test:
    def assert_equal(expected: typing.Any, actual: typing.Any) -> None:
      if actual != expected:
        raise RuntimeError(f'Expected {expected} but got {actual}')
   
    def test_valid_password() -> None:
      # unit cases
      assert_equal(False, valid_password('bcdffaa')) # too short
      assert_equal(False, valid_password('abcdffaaa')) # too long
      assert_equal(False, valid_password('accdffaa')) # missing increasing straight of 3 letters
      assert_equal(False, valid_password('abciffaa')) # contains i
      assert_equal(False, valid_password('abcoffaa')) # contains o
      assert_equal(False, valid_password('abclffaa')) # contains l
      assert_equal(False, valid_password('abcdffxz')) # missing non-overlapping pairs of letters
      assert_equal(False, valid_password('abcdehah')) # two of the same letters are not pairs if they are not touching
      
      # real world
      assert_equal(True, valid_password('abcdffaa'))
      assert_equal(True, valid_password('ghjaabcc'))
    
    def test_next_password() -> None:
      # real world
      assert_equal('abcdffaa', next_password('abcdefgh'))
      assert_equal('ghjaabcc', next_password('ghijklmn'))
      
    test_valid_password()
    test_next_password()
    
    print('All tests passed!')
    sys.exit()
    
  print(next_password(next_password('hxbxwxba')))