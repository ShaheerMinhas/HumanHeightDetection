import cv2
from rembg import remove 
from flask import Flask, render_template, request, send_file
from PIL import Image
import numpy as np
import io

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def enlarge_image():
    if 'image' not in request.files:
        return "No image uploaded", 400

    image_file = request.files['image']
    scale = float(request.form['scale'])
    method = request.form['method']

 


    img_io = io.BytesIO()
    enlarged_img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
