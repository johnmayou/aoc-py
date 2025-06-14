# ribbon:
#   shortest distance around sides
#   or
#   smallest perimeter of any one face

# bow:
#   cubic feet of volume of the present

total_ft = 0

with open('input.txt') as f:
  line = f.readline()
  while line:
    l, w, h = map(lambda x: int(x), line.strip().split('x'))
    
    # ribbon
    sorted_sides = sorted([l, w, h])
    rbn_ft = (sorted_sides[0] + sorted_sides[1]) * 2
    total_ft += rbn_ft
    
    # bow
    bow_ft = l * w * h # volume of present
    total_ft += bow_ft
    
    line = f.readline()
    
print(total_ft)