from flask import Flask, render_template, request
from PIL import Image
from PIL import ImageCms
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

numImages = 0
@app.route('/', methods=['POST'])
def upload():
  global numImages
  try:
    # check if the post request has the file part
    file = request.files['photo']
    img = Image.open(file)
    # img = Image.open("./sample.jpg")
    # if img.mode == "CMYK":
    #   # color profiles can be found at C:\Program Files (x86)\Common Files\Adobe\Color\Profiles\Recommended
    #   img = ImageCms.profileToProfile(img, "USWebCoatedSWOP.icc", "sRGB_Color_Space_Profile.icm", outputMode="RGB")
    # # PIL image -> OpenCV image; see https://stackoverflow.com/q/14134892/2202732
    img = cv2.cvtColor(np.array(img), cv2.IMREAD_COLOR)

    # get the image dimensions (height, width and channels)
    h, w, c = img.shape
    # append Alpha channel -- required for BGRA (Blue, Green, Red, Alpha)
    img = np.concatenate([img, np.full((h, w, 1), 255, dtype=np.uint8)], axis=-1)

    # #read image file string data
    # filestr = request.files['photo'].read()
    # #convert string data to numpy array
    # npimg = np.frombuffer(filestr, np.uint8)
    # # convert numpy array to image
    # img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    ## (1) Convert to gray, and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 91, 2)

    ## (2) Morph-op to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11,11))
    morphed = cv2.morphologyEx(threshed, cv2.MORPH_OPEN, kernel)

    ## (3) Find the max-area contour
    cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnt = sorted(cnts, key=cv2.contourArea)[-1]

    ## (4) Create mask
    mask = np.zeros(img.shape[:2],np.uint8)
    cv2.drawContours(mask, [cnt],-1, 255, -1)
    masked = cv2.bitwise_and(img, img, mask=mask)

    ## (5) Crop
    x,y,w,h = cv2.boundingRect(cnt)
    print(x, y, w, h)
    dst = masked[y:y+h, x:x+w]
    
    processed_image = Image.fromarray(dst)
    # processed_image = Image.fromarray(morphed)
    width, height = processed_image.size
    newWidth, newHeight = int(width/5), int(height/5)
    processed_image = processed_image.resize((newWidth, newHeight))
    processed_image.save(f'../openFrameworks/apps/myApps/Tidepool/bin/data/images/test{numImages}.png');
    numImages += 1
    return('Image uploaded')
    print('Image uploaded')
  except Exception as err:
    print('Error occurred')
    print(err)
    return('Error, image not received.')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
  # upload()