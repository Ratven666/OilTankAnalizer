import math

import numpy as np

z_min = -2.455

l_s = 0.01

print(math.fmod(z_min,l_s))
print(z_min // l_s)
print(z_min % l_s)

print(z_min - math.fmod(z_min,l_s))

z0 = 1
z_max = 10

levels_step = 0.5

print(np.arange(z0, z_max + 1e-9, levels_step))

print(np.linspace(0, 360, 9)[:-1])