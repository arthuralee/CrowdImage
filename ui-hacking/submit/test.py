import numpy as np
from matplotlib.nxutils import points_inside_poly

nx, ny = 991, 678
poly_verts = [(708,88),(797,108),(808,192),(825,414),(807,468),(680,468),(542,457),(501,435),(505,383),(631,329),(660,254),(606,206),(629,142),(675,80)]

# Create vertex coordinates for each grid cell...
# (<0,0> is at the top left of the grid in this system)
x, y = np.meshgrid(np.arange(nx), np.arange(ny))
x, y = x.flatten(), y.flatten()

points = np.vstack((x,y)).T

grid = points_inside_poly(points, poly_verts)
grid = grid.reshape((ny,nx))

#assert(not grid[396][197])
#assert(grid[183][713])