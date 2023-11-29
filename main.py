from flask import Flask, render_template, request, redirect, flash
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans


UPLOAD_PATH = 'C:/Users/jayes/PycharmProjects/Day_92_Color extracting site/static/upload'
app = Flask(__name__)
app.config['UPLOAD_PATH'] = UPLOAD_PATH
app.secret_key = "secretkey"
Bootstrap(app)


def convert_to_hex(colors):
    # THE BELOW SOLUTION GIVES COLORS WHICH ARE SIMILAR TO ONE ANOTHER AND HENCE MAKES THE PICTURE MORE COMPLEX
    # array_2d = colors.reshape(-1, 3)   # this converts the 3d array to 2d array, -1 to determine the rows and 3 to specify number of elements in each row
    # hex_array = ["#{:02x}{:02x}{:02x}".format(element[0], element[1], element[2]) for element in array_2d]
    # count_pixels = Counter(hex_array)  # counts the occurrence of each color , returns a dictionary of count
    # sort_pixels = sorted(hex_array, key=lambda x: (-count_pixels[x], x))  # Sorting the list based on the counts, -ve given as the conversion by default is ascending order eg: 40,50 --> -50,-40
    # color_list = list(dict.fromkeys(sort_pixels))  # removes duplicate from the list using fromkeys as dictionary has unique key (i.e only one key) with value none
    # return color_list

    reshaped_image = colors.reshape(-1, 3)
    kmeans = KMeans(n_clusters=15, random_state=0).fit(reshaped_image)  # algorithm applied
    clustered_colors = kmeans.cluster_centers_.astype(int)   # clusters average rgb color of the image according to n_clusters valure
    # Count the number of pixels in each cluster
    labels = kmeans.labels_    # this assigns each pixel to one of the 15 clusters created by K-Means based on their similarity to the cluster centers (average colors).Each label in the labels array indicates which cluster a pixel belongs to.
    cluster_counts = np.bincount(labels)    # counts how many pixels are assigned to each cluster.

    # Create a list of (color, count) pairs
    color_counts = [(clustered_colors[i], count) for i, count in enumerate(cluster_counts)]

    # Sort the colors based on their count in descending order
    color_counts.sort(key=lambda x: x[1], reverse=True)

    # Extract the sorted colors
    sorted_colors = [color for color, _ in color_counts]

    # Convert to hex code
    hex_array = ["#{:02x}{:02x}{:02x}".format(element[0], element[1], element[2]) for element in sorted_colors]
    return hex_array


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        image = request.files['readme_img']
        if image.filename == '':
            flash('Image not uploaded please try again.')
            return redirect('/')
        elif image.filename.split('.')[-1] == 'png' or image.filename.split('.')[-1] == 'jpg' or image.filename.split('.')[-1] == 'jpeg':
            # Saving image file on server and using it later to display on webpage
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            number = int(request.form['color'])
            if number > 15:
                number = 15

            # detecting pixel and converting it into rgb and then into hex code
            img = cv2.imread(f'static/upload/{filename}')
            np_array = np.array(img)
            rgb_array = cv2.cvtColor(np_array, cv2.COLOR_BGR2RGB)
            colors_hex_code = convert_to_hex(rgb_array)
            return render_template('colorextractor.html', image=f'/upload/{filename}', number_of_images=number,
                                   colors=colors_hex_code)
        else:
            flash('File not supported please try again')
            return redirect('/')
    else:
        return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
