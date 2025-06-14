import hashlib

input = 'yzbqklnj'
guess = 1

def md5(s: str) -> str:
  return hashlib.md5(s.encode('utf-8')).hexdigest()

while not md5(input+str(guess)).startswith('00000'):
  guess += 1

print(guess)