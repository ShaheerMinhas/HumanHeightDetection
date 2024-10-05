from flask import Flask, render_template, request
import cv2
import numpy as np
from rembg import remove
import base64
import io

app = Flask(__name__)

def remove_background(image_file):
    input_data = image_file.read()
    result = remove(input_data)
    nparr = np.frombuffer(result, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return image

def detect_grid(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    grid_contour = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4 and cv2.contourArea(approx) > 500:
            grid_contour = approx
            break
            
    if grid_contour is not None:
        cv2.drawContours(image, [grid_contour], -1, (0, 255, 0), 3)
        x, y, w, h = cv2.boundingRect(grid_contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
        return (x, y, w, h)
    else:
        print("Grid not found.")
        return None

def detect_height(image, grid_info):
    if grid_info is None:
        print("Grid not detected, unable to calculate height.")
        return None
    grid_pixel_height = grid_info[3]  # Height from boundingRect
    grid_in_inches = 2  # Known grid height in inches
    pixel_to_inch_ratio = grid_in_inches / grid_pixel_height
    human_pixel_height = image.shape[0]  # Total image height in pixels
    human_height_inches = human_pixel_height * pixel_to_inch_ratio
    human_height_cm = human_height_inches * 2.54
    return human_height_inches, human_height_cm

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['image']
        image_no_bg = remove_background(file)
        grid_info = detect_grid(image_no_bg)
        heights = detect_height(image_no_bg, grid_info)
        
        _, buffer = cv2.imencode('.png', image_no_bg)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        if heights:
            human_height_inches, human_height_cm = heights
            height_text = f"Human Height: {human_height_inches:.2f} inches / {human_height_cm:.2f} cm"
        else:
            height_text = "Grid not detected, unable to calculate height."
        
        return render_template("index.html", img_data=img_str, height_text=height_text)

    return render_template("index.html", img_data=None, height_text=None)

if __name__ == "__main__":
    app.run(debug=True)
