from django.db import models
from django import forms
import string, random, json

### HELPERS ###
def genKey(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


### MODELS ###
class Image(models.Model):
	width = models.IntegerField()
	height = models.IntegerField()
	email = models.CharField(max_length=75)
	blocksLeft = models.IntegerField(null=True)
	totalBlocks = models.IntegerField(null=True)

	# decrements block count and returns true if no more blocks
	def finishBlock(self):
		if self.blocksLeft == None:
			return False
		self.blocksLeft -= 1
		return not self.blocksLeft > 0

class Block(models.Model):
	image = models.ForeignKey(Image)
	dateTime = models.DateTimeField(auto_now_add=True)
	done = models.BooleanField(default=False)
	key = models.CharField(max_length=10, default=genKey, unique=True)
	pixels = models.TextField()
	
	# how many blocks come before this block in the image
	index = models.IntegerField()

	# return the pixels in this block as a 2D array of
	# tuples (color, selected[1/0])
	def getPixels(self):
		return json.loads(self.pixels)

	# takes a 2D array of pixel tuples and stores
	# them in the pixels TextField
	def setPixels(self, px):
		self.pixels = json.dumps(px)

	# gets the oldest block in the DB
	@classmethod
	def pickBlock(self):
		block
		try:
			return self.objects.filter(done=False).earliest('dateTime')
		except Exception, e: #DoesNotExist
			return None


