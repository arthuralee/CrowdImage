# Create your views here.
from django.http import HttpResponse
from core import models
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
import json
import string, random, thread, math
from PIL import Image

#################
##### VIEWS #####
#################

@require_GET
def submitView(request):
    data = {}
    return render_to_response("submit.html", data, context_instance=RequestContext(request))

@require_POST
@csrf_exempt
def submitPic(request):
    email = request.POST.get('email')
    if email == None or email == "": # check that there is an email
        raise Exception("No email provided")
    
    imgData = request.FILES.get('image')
    if imgData == None: # check that there is an image
        raise Exception("No image provided")
    img = Image.open(imgData)
    scaleImage(img)
    orig_width, orig_height = img.size
    img = padImage(img)

    image = models.Image(height = orig_height, width=orig_width, email=email)
    image.save()
    
    # save image blocks in new thread
    thread.start_new_thread(saveBlocks, (img, image))
    
    return HttpResponse("height: %d, width: %d" %(orig_height, orig_width))

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

# takes in the padded image data and the model that stores
# the original image sizes, email, etc
def saveBlocks(imgData, image):
    width, height = imgData.size
    print("width: %d, height: %d" % (width,height))
    rows = []
    for y in xrange(height):
        row = []
        for x in xrange(width):
            pixel = imgData.getpixel((x,y))
            row.append(pixel)
        rows.append(row)
    
    numBlocks = getNumBlocks(width,height)
    image.blocksLeft = numBlocks
    image.totalBlocks = numBlocks
    image.save()

    for i in xrange(numBlocks):
        blockPixels = getBlockFromArray(rows, i)
        block = models.Block(image=image, index=i)
        block.setPixels(blockPixels)
        block.save()
    print("all blocks saved")

def getNumBlocks(width, height):
    return ((width/50)) * ((height/50))

def getBlockFromArray(pixelArray, i):
    width = len(pixelArray[0])
    height = len(pixelArray)

    blocksPerRow = width/50
    
    xOffset = i % blocksPerRow
    yOffset = i / blocksPerRow

    rows = []
    for y in xrange(100):
        y = y + yOffset
        row = []
        for x in xrange(100):
            x = x+xOffset
            row.append(pixelArray[y][x])
        rows.append(row)

    return rows

# scales image to about 0.5 megapixels
# because thats still a crap ton of workers
def scaleImage(img):
    w, h = img.size
    f = 750.0 # (750*750) / (50*50) = 225 blocks
    factor = math.sqrt((f*f)/(w*h)) # calculate scale factor
    if(factor>1):
        return
    print("original w: "+str(w))
    print("original h: "+str(h))
    w = int(w * factor)
    h = int(h * factor)
    print("new w: "+str(w))
    print("new h: "+str(h))
    print("factor: "+str(factor))
    img.thumbnail((w,h), Image.ANTIALIAS)

    
# pads image with alpha=0 pixels so that 100x100 blocks fit nicely
def padImage(img):
    def rnd(x, base=100):
        return base * ((x+(base-1))/base)
    
    w, h = img.size
    w = rnd(w)
    h = rnd(h)
    newImg = Image.new(mode='RGBA', size=(w,h), color=(0,0,0,0))
    newImg.paste(img, (0,0))
    return newImg

# given the location of an image, this
# creates blocks out of the image and
# saves them into the db
# meant to be called in a new thread
def handleBlockCreation(image,poly):
    imageLoc = image.img
    blocks = image_utils.makeBlocks(img,poly)
    i = 0
    for b in blocks:
        block = models.Block(
            image = image,
            pixels = b,
            index = i
        )
        i += 1
    return None

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

