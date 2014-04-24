CrowdImage
==========
[crowdimage.herokuapp.com](crowdimage.herokuapp.com)

Crowd-sourced image manipulation. CMU 05-499C Crowd Programming final project
  

##API

####post: `/api/submitpic`
#####request:
	
	{
		"photo": "...",
		"selectedPixels": [[1,1,0,1,0,...],[...],...],
		"email": "hello@example.com"
	}
`selectedPixels` is an 2D array of 1s and 0s where 1 means that pixel was selected by the uploader as being part of the image to be cropped

#####response:
http response 200 or 500

####get: `/api/getblock`
#####request:
http get request (no parameters)

#####response:
	
	{
		"id": "abcd1234",
		"height": 100,
		"width": 100,
		"pixels": [[["2B303B",0],["C6C6C6",1],...],[...],...]
	}
`pixels` is a 2 dimentional array of pixels by rows and columns. Each pixel however is represented as an array (so actually it's a 3D array) of [colorHexValue,initSelectVal] where colorHexValue is the hexidemial color of that pixel and the initSelectVal is a 1 or a 0 indicating whether or not the given pixel should start out as being selected or not.

####post: `/api/returnblock`
request:
	
	{
		"id": "abcd1234",
		"pixels": [[1,1,0,1,0,...],[...],...]
	}
`pixels` is a 2 dimentional array of 1s and 0s indicating whether or not each pixel was selected by the worker.

#####response:
http response 200 or 500