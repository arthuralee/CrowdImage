# Create your views here.
from django.http import HttpResponse
from core import models
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage, EmailMultiAlternatives
import json
import string, random, thread, math
import numpy as np
from matplotlib.path import Path
from PIL import Image
import os

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
    print os.path.dirname(os.path.realpath(__file__))
    email = request.POST.get('email')
    if email == None or email == "": # check that there is an email
        raise Exception("No email provided")
    
    imgData = request.FILES.get('photo')
    if imgData == None: # check that there is an image
        raise Exception("No image provided")

    polygon = request.POST.get('selectedPixels')
    if polygon == None: # check that there is an image
        raise Exception("No polygon provided")


    img = Image.open(imgData)
    # scaleImage(img)
    orig_width, orig_height = img.size
    img = padImage(img)
    p_width, p_height = img.size

    selectedPixels = poly2Pixels(json.loads(polygon), p_width, p_height)
    # print(selectedPixels)

    image = models.Image(
        height = orig_height, width=orig_width,
        padded_height = p_height,
        padded_width = p_width,
        email=email)
    image.save()
    
    # save image blocks in new thread
    thread.start_new_thread(saveBlocks, (img, image, selectedPixels))
    # saveBlocks(img, image)
    return HttpResponse()
    
    # try to reconstruct original image from blocks

    # reImg = constructImgFromBlocks(image, img)
    # re_width, re_height = reImg.size
    # reImg = finishImage(image)

    # send image
    # response = HttpResponse(mimetype="image/png")
    # reImg.save(response, "png")
    # return response
    # comparison = compareImgs(img, reImg)
    # return HttpResponse("ERRORS --> r: %d, g: %d, b: %d, a: %d" % comparison)
    # return HttpResponse("orig: (%d,%d), reconstruced: (%d,%d)" % (p_width,p_height, re_width,re_height))

@require_GET
@csrf_exempt
def getBlock(request):
    block = models.Block.pickBlock()

    if block == None:
        print("no block found")
        return JsonResponse({})
    else:
        print("block found")
        pixels = pixelsToFrontEnd(block.getPixels())
        data = {'id': block.key, 'height':100,
            'width':100, 'pixels':pixels}
        return JsonResponse(data)

@require_POST
@csrf_exempt
def returnBlock(request):
    key = request.POST.get('id')
    pixels = request.POST.get('pixels')

    if key == None:
        raise Exception("missing key in post data")
    if pixels == None:
        raise Exception("missing pixels in post data")

    block = get_object_or_404(models.Block, key=key)
    thread.start_new_thread(processReturnBlock, (pixels, block))

    return HttpResponse()

def processReturnBlock(pixels, block):
    # parse json
    pixels =json.loads(pixels)
    
    # in case someone else already submitted this block
    if block.done:
        return
    
    updateBlock(pixels, block)
    block.done = True
    
    image = block.image
    image.blocksLeft -= 1;
    image.save()
    block.save()
    
    print("blocksLeft: %d" % image.blocksLeft)
    if image.blocksLeft <= 0:
        finishImage(image)

###################
##### HELPERS #####
###################

def finishImage(image):
    img = constructImgFromBlocks(image)
    # todo: crop image here
    emailImg(img, image.email)
    blocks = models.Block.objects.filter(image=image)
    for block in blocks:
        block.delete()
    image.delete()
    return img

def emailImg(img, email):
    print ("saving image")
    img.save('tmp/img1.png', 'PNG')
    print ("emailing image")
    fromEmail = ' crowdimage@gmail.com'

    subject = 'Your image has been processed'
    toList = [email]

    text_content = ""
    html_content = '<h1>image:</h1><img src="img1.png">'

    email = EmailMultiAlternatives(subject, text_content, fromEmail, toList)
    email.attach_alternative(html_content, "text/html")
    # email.attach('your_image.png', img, 'image/png')
    email.attach_file('tmp/img1.png')
    print ("message sent")
    # email.attach_file(img)
    
    email.send()
    # return None

# updates the opacity in each block from the
# selections from the front end
def updateBlock(selectionArray, block):
    h = w = 100
    originalPixels = block.getPixels()

    newPixels = [[(0,0,0,0) for x in xrange(w)] for x in xrange(h)]
    
    for y in xrange(h):
        for x in xrange(w):
            (r,g,b,_) = originalPixels[y][x]
            a = (selectionArray[y][x]) * 255
            newPixels[y][x] = (r,g,b,a)

    block.setPixels(newPixels)

# takes 2D array of pixels as 4 channels and returns
# 2D array of pixels as (hex,alpha[0-1])
def pixelsToFrontEnd(pixelsArray):
    width = len(pixelsArray[0])
    height = len(pixelsArray)
    rows = []
    for y in xrange(height):
        row = []
        for x in xrange(width):
            p = pixelsArray[y][x]
            color = channelsToHex(p[0],p[1],p[2])
            a = round(p[3]/250.0)
            row.append([color,a])
        rows.append(row)
    return rows

def channelsToHex(r,g,b):
    h = hex((r<<16)+(g<<8)+(b<<0))[2:]
    while len(h)<6: h = '0'+h
    return h

def compareImgToArr(img1, imgArr):
    r=0
    g=0
    b=0
    a=0
    width, height = img1.size
    for y in xrange(height):
        for x in xrange(width):
            px1 = img1.getpixel((x,y))
            px2 = imgArr[y][x]
            if px1[0] != px2[0]: r += 1
            if px1[1] != px2[1]: g += 1
            if px1[2] != px2[2]: b += 1
            if px1[3] != px2[3]: a += 1
    return (r,g,b,a)

# takes an image object and looks in the db for all
# of its blocks and then reconstructs the original
# image from them
def constructImgFromBlocks(image, paddedImg=None):
    blocks = models.Block.objects.filter(image=image).order_by('index')
    
    # construct image array
    width = image.padded_width
    height = image.padded_height
    newImgArr = [[(0,0,0,0) for x in xrange(width)] for x in xrange(height)] 

    blocksPerRow = width/50 - 1
    
    for i in xrange(len(blocks)):
        block = blocks[i]
        blockPixels = block.getPixels()
        xOffset = (i % blocksPerRow) * 50
        yOffset = (i / blocksPerRow) * 50
        for y in xrange(100):
            for x in xrange(100):
                absx = x+xOffset
                absy = y+yOffset

                (r,g,b, newA) = tuple(blockPixels[y][x])
                (_,_,_,oldA) = newImgArr[y+yOffset][x+xOffset]
                
                if absx<50 and absy<50:
                    d=1
                elif absx<50:
                    d=2
                elif absy<50:
                    d=2
                else:
                    d=4

                if absx>=width-50 and absy<50:
                    d=1
                elif absx>=width-50:
                    d=2

                a = oldA + (newA/d)
                if(a>255):
                    print("(%d,%d)" % (absx,absy))
                    print(a)
                newImgArr[absy][absx] = (r,g,b,a)


    print("done constructing image array")
    # newImgNumpyArr = numpy.array(newImgArr)
    if paddedImg != None:
        comparison = compareImgToArr(paddedImg, newImgNumpyArr)
        print("ERRORS --> r: %d, g: %d, b: %d, a: %d" % comparison)
    newImg = createImageFromArray(newImgArr)
    # newImg = Image.fromarray(newImgNumpyArr, mode="RGBA")
    return newImg

def createImageFromArray(arr):
    w = len(arr[0])
    h = len(arr)
    img = Image.new(mode='RGBA', size=(w,h), color=(0,0,0,0))
    for y in xrange(h):
        for x in xrange(w):
            pixel = arr[y][x]
            img.putpixel((x,y),pixel)
    return img


# takes in the padded image data and the model that stores
# the original image sizes, email, etc
def saveBlocks(imgData, image, selectedPixels):
    width, height = imgData.size
    print("width: %d, height: %d" % (width,height))
    rows = []
    for y in xrange(height):
        row = []
        for x in xrange(width):
            (r,g,b,_) = imgData.getpixel((x,y))
            a = (selectedPixels[y][x]) * 255
            row.append((r,g,b,a))
        rows.append(row)
    
    numBlocks = getNumBlocks(width,height)
    image.blocksLeft = numBlocks
    image.totalBlocks = numBlocks
    

    for i in xrange(numBlocks):
        (blockPixels, done) = getBlockFromArray(rows, i)
        block = models.Block(image=image, index=i)
        block.setPixels(blockPixels)
        block.done = done
        if(done):
            image.blocksLeft -=1
        block.save()
    image.save()
    print("all blocks saved")

def getNumBlocks(width, height):
    # -1 because blocks are actuall 100x100
    return ((width/50)-1) * ((height/50)-1)

def getBlockFromArray(pixelArray, i):
    width = len(pixelArray[0])
    height = len(pixelArray)

    blocksPerRow = (width/50) - 1
    
    xOffset = (i % blocksPerRow) * 50
    yOffset = (i / blocksPerRow) * 50

    var = 0
    rows = []
    for y in xrange(100):
        y = y + yOffset
        row = []
        for x in xrange(100):
            x = x+xOffset
            (r,g,b,a) = pixelArray[y][x]
            var += a/255
            row.append((r,g,b,a))
        rows.append(row)

    done = var == 0 or var == 100*100
    return (rows,done)

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
# def handleBlockCreation(image,poly):
#     imageLoc = image.img
#     blocks = image_utils.makeBlocks(img,poly)
#     i = 0
#     for b in blocks:
#         block = models.Block(
#             image = image,
#             pixels = b,
#             index = i
#         )
#         i += 1
#     return None

def JsonResponse(data):
    return HttpResponse(json.dumps(data), content_type="application/json")


# def generatePixels(size):
#     inPixelLabeled =  ['444444', 1]
#     # outPixelLabeled = ['999999', 1]
#     # inPixelUnLabeled =  ['444444', 0]
#     outPixelUnLabeled = ['999999', 0]
#     rows = []
#     for r in xrange(size):
#         row = []
#         for p in xrange(size):
#             if p <= int(r**1.03):
#                 row.append(outPixelUnLabeled)
#             else:
#                 row.append(inPixelLabeled)
#         rows.append(row)
#     return rows

def poly2Pixels(points, w, h):
    rows = []
    path = Path(points)

    for y in xrange(h):
        row = []
        for x in xrange(w):
            row.append(path.contains_point((x,y)))
        rows.append(row)
    return rows
# pixelarray = poly2pixels(poly, width, height) # result in pixelarray
# helper function to convert polygon into a 2d array of selected pixels
# def poly2Pixels(poly_verts, nx, ny):
#   # Create vertex coordinates for each grid cell...
#   # (<0,0> is at the top left of the grid in this system)
#   x, y = np.meshgrid(np.arange(nx), np.arange(ny))
#   x, y = x.flatten(), y.flatten()

#   points = np.vstack((x,y)).T

#   grid = points_inside_poly(points, poly_verts)
#   grid = grid.reshape((ny,nx))

#   return grid