w_sqft = 0
with open('input.txt') as f:
  line = f.readline()
  while line:
    l, w, h = map(lambda x: int(x), line.strip().split('x'))
    s_areas = (2*l*w, 2*l*h, 2*w*h)
    w_total = sum(s_areas) + (min(s_areas) / 2)
    w_sqft += w_total
    line = f.readline()
print(w_sqft)