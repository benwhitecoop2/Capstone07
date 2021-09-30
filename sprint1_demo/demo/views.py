from django.shortcuts import render
from django.http import HttpResponse as res
from .FacialDetection.facial_detection import facial_detection
# Create your views here.

def getFaces(url):
   faceDetect = facial_detection(url)
   faceDetect.start()
   return faceDetect.join()

def home(req):
    return render(req, 'demo/home.html')

def img1(req):
    
    request = int(req.path.replace('/', ''))

    image_path = 'demo/static/demo/images/'
    images_list = [ 
        [1, 'face1.jpg'], 
        [2, 'group1.jpg'], 
        [3, 'group2.jpg'],
        [4, 'face2.jpg'] 
    ]

    for img in images_list:
        if (img[0] == request):
            image_path = image_path + img[1]

    result = getFaces(image_path)

    url_alt = result[0][11:]
    image_path = image_path[11:]

    
    if (request < 4):
        request = request + 1
    else:
        request = ''

    print(request)

    content = {
        'img_alt_url': url_alt,
        'faces_num': result[1],
        'img_raw_url': image_path,
        'next_page': request
    }

    return render(req, 'demo/img1.html', content)
