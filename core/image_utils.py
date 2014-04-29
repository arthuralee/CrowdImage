# given the relative location of an image
# this opens the image and creates an array
# of 2D arrays of 100x100 pixel tuples, each overlapping
# by 50px with the previous block
# every pixel in the image is guaranteed to be in exactly 2 blocks
def makeBlocks(img, polygon):
	selectedPixels = poly2pixels(polygon)
	return None
  
# pixelarray = poly2pixels(poly, width, height) # result in pixelarray
# helper function to convert polygon into a 2d array of selected pixels
def poly2pixels(poly_verts, nx, ny):
  # Create vertex coordinates for each grid cell...
  # (<0,0> is at the top left of the grid in this system)
  x, y = np.meshgrid(np.arange(nx), np.arange(ny))
  x, y = x.flatten(), y.flatten()

  points = np.vstack((x,y)).T

  grid = points_inside_poly(points, poly_verts)
  grid = grid.reshape((ny,nx))

  return grid

# takes an array of blocks
# and returns 2D array of floats where each float
# indicates the opacity 
# requires that blocks are in sorted order and that each pixel
# is in exactly 2 blocks
def combineBlocks(blocks):
	return None

# takes an image path and a 2D array of
# pixel opacities as floats (0-1) and
# sets each pixel to that opacity
# and then saves the image
def setOpacity(img, opacArray):
	# http://pillow.readthedocs.org/en/latest/reference/Image.html#PIL.Image.Image.paste
	return None

# creates width * height image with 0 oppacity
def _createInvisibleImage(width, height):
	return None

## procedures ##

### uploading an image ###
#### get the file object that was uploaded
#### turn the file into blocks with colors and opacities
#### save the blocks to the database

### having workers fill out blocks ###
#### get an unfinish block from the db and send it to a worker
#### get back the array of 1s and 0s and only update the alpha values in the block and save it

### combining blocks
#### create an empty array the size of all the blocks (gotta calculate this from # of blocks and width)
#### walk through each block setting each pixel to the RGB color for that pixel in the block and 1/2 the alpha value in that block
#### make in image from the array (convert to numpy array first)
#### crop the image to the size of the original image
#### email the images, delete the image and all of its blocks