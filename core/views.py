# Create your views here.
from django.http import HttpResponse
from core import models
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
import json

#################
##### VIEWS #####
#################

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

@require_POST
@csrf_exempt
def submitPic(request):
  # should get from POST data instead
  poly = [(708,88),(797,108),(808,192),(825,414),(807,468),(680,468),(542,457),(501,435),(505,383),(631,329),(660,254),(606,206),(629,142),(675,80)]
  width = 950
  height = 700
  pixelarray = poly2pixels(poly, width, height) # result in pixelarray
	return HttpResponse()

@require_GET
@csrf_exempt
def getBlock(request):
	id = "abcd1234"
	height = 100
	width = 100
	pixels = generatePixels(100)
	data = {'id': id, 'height':height,
			'width':width, 'pixels':pixels}
	return JsonResponse(data)

@require_POST
@csrf_exempt
def returnBlock(request):
	return HttpResponse()

###################
##### HELPERS #####
###################

def JsonResponse(data):
	return HttpResponse(json.dumps(data), content_type="application/json")


def generatePixels(size):
	inPixelLabeled =  ['444444', 1]
	# outPixelLabeled = ['999999', 1]
	# inPixelUnLabeled =  ['444444', 0]
	outPixelUnLabeled = ['999999', 0]
	rows = []
	for r in xrange(size):
		row = []
		for p in xrange(size):
			if p <= int(r**1.03):
				row.append(outPixelUnLabeled)
			else:
				row.append(inPixelLabeled)
		rows.append(row)
	return rows

