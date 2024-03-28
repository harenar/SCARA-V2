# -*- coding: utf-8 -*-
"""SCARA v2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1L9VxtWAKdn_35sPAMfzokFGIsyFoIamo
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import imageio
import math
import os

L1, L2, L3 = 12.0, 13.1, 12.3

def compute_angles(a, b, c, d):
    print(f"Sides: a={a}, b={b}, c={c}, d={d}")

    # Start with assumed angle between b and c as 30 degrees
    angle_bc = 45

    while angle_bc<180:
        # print(f"Assumed angle between sides b and c: {angle_bc} degrees")

        # Compute the length of the diagonal e
        e = math.sqrt(b**2 + c**2 - 2 * b * c * math.cos(math.radians(angle_bc)))
        # print(f"Calculated length of diagonal e: {e}")

        # Check for validity of the diagonal
        if e > a + d or e > b + c:
            print("Invalid diagonal length. Quadrilateral cannot be formed.")
            return "Invalid diagonal length. Quadrilateral cannot be formed."

        # Using the law of cosines in the two triangles to find all angles
        # Triangle 1: Sides a, d, e
        try:
            angle_ad = math.degrees(math.acos((a**2 + d**2 - e**2) / (2 * a * d)))
            angle_de = math.degrees(math.acos((d**2 + e**2 - a**2) / (2 * d * e)))
            angle_ae = 180 - angle_ad - angle_de
        except ValueError:
            angle_bc += 2
            continue

        # Triangle 2: Sides b, c, e
        try:
            angle_bc = math.degrees(math.acos((b**2 + c**2 - e**2) / (2 * b * c)))
            angle_ce = math.degrees(math.acos((c**2 + e**2 - b**2) / (2 * c * e)))
            angle_be = 180 - angle_bc - angle_ce
        except ValueError:
            angle_bc += 2
            continue
        angle_ab = angle_ae + angle_be
        angle_cd = angle_ce + angle_de

        print(f"Calculated angles: angle_ab={angle_ab}, angle_bc={angle_bc}, angle_cd={angle_cd}, angle_ad={angle_ad}")

        # Check if the sum of angles CE and DE is greater than 90 degrees
        if angle_cd > 90 and angle_cd < 180:
            return angle_ab, angle_bc, angle_cd, angle_ad
        else:
            # Increment assumed angle between b and c by 2 degrees
            angle_bc += 2

    return 90,90,30,135

def inverse_kinematics(x, y, z):
# Function to calculate inverse kinematics
    # x, y, z: Desired position of the end effector

    # Calculate distance from origin to the wrist
    r = math.sqrt(x**2 + y**2)

    # Calculate theta1
    theta1 = math.degrees(math.atan2(y, x))

    a = math.sqrt(r**2 + z**2)

    theta2_, theta3_, theta4_, _ = compute_angles(a,L1,L2,L3)

    theta2 = (theta2_ + math.degrees(math.atan2(z,r)))
    theta3 = theta3_
    theta4 = theta4_
    print(f"Robot angles: axis1={theta1} axis2={theta2}, axis3={theta3}, axis4={theta4}")
    return theta1, theta2, theta3, theta4

def robot_to(x,y,z,filename="0.png"):
    axis1, axis2, axis3, axis5 = inverse_kinematics(x, y, z)
    axis4 =0
    theta1, theta2, theta3, theta4, theta5 = math.radians(axis1), math.radians(axis2), math.radians(axis3), math.radians(axis4), math.radians(axis5)

    xl1,yl1,zl1 = L1* np.cos(theta1)*np.cos(theta2), L1 * np.sin(theta1)*np.cos(theta2), L1*np.sin(theta2)
    print(f"First Line: {int(xl1)}, {int(yl1)}, {int(zl1)}")
    angle2 = theta3+theta2-np.pi
    xl2, yl2, zl2 = xl1 + np.cos(theta1)*L2*np.cos(angle2),yl1 + np.sin(theta1)*L2*np.cos(angle2), zl1 + L2*np.sin(angle2)
    print(f"Second Line: {int(xl2)}, {int(yl2)}, {int(zl2)}")
    angle3 = 2*np.pi - theta2 -theta3-theta4
    xl3, yl3, zl3 = xl2 - L3* np.cos(theta1)*np.cos(angle3), yl2 - L3*np.sin(theta1)*np.cos(angle3), zl2 + L3*np.sin(angle3)
    print(f"Third Line: {int(xl3)}, {int(yl3)}, {int(zl3)}")

    # Plot the arm configuration
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim(0, 30)
    ax.set_ylim(0, 30)
    ax.set_zlim(0, 30)
    # Plot arm links

    ax.plot([0, xl1 ], [0,yl1 ], [0, zl1], color='blue')  # Link 1
    ax.plot([xl1, xl2 ], [yl1, yl2], [zl1, zl2], color='green')  # Link 2
    ax.plot([xl2, xl3 ], [yl2, yl3], [zl2, zl3], color='red')  # Link 3

    ax.scatter(x, y, z, color='orange', label='Point')

    ax.scatter(0, 0, 0, color='black')
    ax.scatter(xl1, yl1, zl1, color='blue')
    ax.scatter(xl2, yl2, zl2, color='green')
    ax.scatter(xl3, yl3, zl3, color='red')

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('SCARA 6-Axis Arm Configuration')
    ax.legend()

    gap = np.sqrt((xl3-x)**2 + (yl3-y)**2 + (zl3-z)**2)
    print(f"Gap Distance: {int(gap*10)} mm")

    ax.text(x=30, y=30, z=30, s=f"Gap: {int(gap*10)} mm", fontsize=12, color='red', ha='right', va='top')
    plt.savefig(filename)
    plt.show()
    print(f"Saved image to {filename}")

    CL1 = np.sqrt((xl3-xl2)**2 + (yl3-yl2)**2 + (zl3-zl2)**2)
    CL2 = np.sqrt((xl2-xl1)**2 + (yl2-yl1)**2 + (zl2-zl1)**2)
    CL3 = np.sqrt((xl1)**2 + (yl1)**2 + (zl1)**2)

    robo1 = axis1
    robo2 = 210 - axis2
    robo3 = 30 + axis3
    robo4 = 90 + axis4
    robo5 = 270 - axis5

    print(f"Robot Angles: {robo1}, {robo2}, {robo3}, {robo4}, {robo5}")

    return filename

def process_coordinates(data):
    IMAGES = []

    delay = data.get('delay', 0)  # Default delay is 0 if not specified

    for index, coord in enumerate(data.get('coordinates', [])):  # Default to an empty list if 'c>
        x = coord.get('x')
        y = coord.get('y')
        z = coord.get('z')

        # Calculate servo angles
        IMAGES.append(robot_to(x, y, z, f"{index}.png"))

        # Wait for the specified delay before processing the next set of coordi>
        time.sleep(delay)

    return IMAGES, delay

# def create_video(IMAGES, delay=1):
#   # Create an imageio writer to save the frames as a video
#   fps = int(1/delay)
#   print(f"processing {IMAGES} into a {fps} fps video")
#   output_file = 'robot_video.mp4'

#   # Read images and create video frames
#   video_frames = [imageio.imread(str(image)) for image in IMAGES]

#   # Create video
#   imageio.mimsave(output_file, video_frames, fps=10)

#   print(f'Video saved as: {output_file}')
#   return output_file

# data = {
# "delay": 0.05,
# "coordinates": [
# {
#     "x": 0,
#     "y": 10,
#     "z": 15
# },{
#     "x": 0,
#     "y": 22,
#     "z": 16
# },
# {
#     "x": 0,
#     "y": 23,
#     "z": 17
# },
# {
#     "x": 0,
#     "y": 24,
#     "z": 18
# },
# {
#     "x": 0,
#     "y": 25,
#     "z": 19
# },{
#     "x": 0,
#     "y": 26,
#     "z": 20
# },{
#     "x": 0,
#     "y": 27,
#     "z": 21
# },{
#     "x": 0,
#     "y": 28,
#     "z": 22
# },{
#     "x": 0,
#     "y": 29,
#     "z": 23
# },{
#     "x": 0,
#     "y": 30,
#     "z": 24
# },{
#     "x": 0,
#     "y": 30,
#     "z": 30
# },
# {
#     "x": 0,
#     "y": 30,
#     "z": 30
# }
# ]
# }

# images, delay = process_coordinates(data)


# video = create_video(images, delay)

"""### rectangle coordinates"""

import os
import imageio

def create_rectangle_video(IMAGES, delay=1, video_output_dir='rectangle_videos', images_output_dir='rectangle_images'):
    # Create output directories if they don't exist
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # Create an imageio writer to save the frames as a video
    fps = int(1/delay)
    print(f"processing {len(IMAGES)} images into a {fps} fps video")
    video_filename = os.path.join(video_output_dir, 'robot_video.mp4')

    # Read images and create video frames
    video_frames = [imageio.imread(str(image)) for image in IMAGES]

    # Create video
    imageio.mimsave(video_filename, video_frames, fps=10)

    print(f'Video saved as: {video_filename}')

    # Saving images separately
    for idx, image_path in enumerate(IMAGES):
        image = imageio.imread(str(image_path))  # Read image data
        image_filename = os.path.join(images_output_dir, f'image_{idx}.png')
        imageio.imwrite(image_filename, image)
        print(f'Image {idx+1} saved as: {image_filename}')

    return video_filename


# ======================================================
# coordinates generates

data = {
    "delay": 0.05,
    "coordinates": []
}

# Define the dimensions of the rectangle
# width = 10
# height = 5

# # Starting coordinates
# x_start = 0
# y_start = 10
# z = 0

width = 10
height = 5


# Starting coordinates
x_start = 0
y_start = 20
z = 0

# Generate coordinates for the first side of the rectangle
for i in range(width):
    data["coordinates"].append({"x": x_start + i, "y": y_start, "z": z})

# Move along the second side of the rectangle
for i in range(height):
    data["coordinates"].append({"x": x_start + width, "y": y_start - i, "z": z})

# Move along the third side of the rectangle
for i in range(width):
    data["coordinates"].append({"x": x_start + width - i, "y": y_start - height, "z": z})

# Move along the fourth side of the rectangle
for i in range(height):
    data["coordinates"].append({"x": x_start, "y": y_start - height + i, "z": z})

# Add the starting point to close the rectangle
data["coordinates"].append({"x": x_start, "y": y_start, "z": z})


json_data = json.dumps(data, indent=4)

# # Print JSON data
print(json_data)

images, delay = process_coordinates(data)

video = create_rectangle_video(images, delay)



# ============================================

"""### rectangle video"""

from IPython.display import HTML
from base64 import b64encode
mp4 = open(video,'rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mp4">
</video>
""" % data_url)






"""### trangle coordiantes"""

import os
import imageio

def create_triangle_video(IMAGES, delay=1, video_output_dir='triangle_videos', images_output_dir='triangle_images'):
    # Create output directories if they don't exist
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # Create an imageio writer to save the frames as a video
    fps = int(1/delay)
    print(f"processing {len(IMAGES)} images into a {fps} fps video")
    video_filename = os.path.join(video_output_dir, 'robot_video.mp4')

    # Read images and create video frames
    video_frames = [imageio.imread(str(image)) for image in IMAGES]

    # Create video
    imageio.mimsave(video_filename, video_frames, fps=10)

    print(f'Video saved as: {video_filename}')

    # Saving images separately
    for idx, image_path in enumerate(IMAGES):
        image = imageio.imread(str(image_path))  # Read image data
        image_filename = os.path.join(images_output_dir, f'image_{idx}.png')
        imageio.imwrite(image_filename, image)
        print(f'Image {idx+1} saved as: {image_filename}')

    return video_filename

# =================================
# coordinates generates

data = {
    "delay": 0.05,
    "coordinates": []
}

# Define the side length of the triangle
side_length = 10

# Starting coordinates
x_start = 0
y_start = 10
z = 0

# Generate coordinates for one side of the triangle
for i in range(side_length + 1):
    data["coordinates"].append({"x": x_start + i, "y": y_start, "z": z})

# Move along the next side of the triangle
for i in range(1, side_length + 1):
    data["coordinates"].append({"x": x_start + side_length, "y": y_start + i, "z": z})

# Move along the third side of the triangle
for i in range(1, side_length):
    data["coordinates"].append({"x": x_start + side_length - i, "y": y_start + side_length - i, "z": z})

# Add the starting point to close the triangle
data["coordinates"].append({"x": x_start, "y": y_start, "z": z})


json_data = json.dumps(data, indent=4)

# # Print JSON data
print(json_data)

images, delay = process_coordinates(data)
video = create_triangle_video(images, delay)

"""### trangle video"""

from IPython.display import HTML
from base64 import b64encode
mp4 = open(video,'rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mp4">
</video>
""" % data_url)

# =================================

"""### circle coordinates"""


def create_circle_video(IMAGES, delay=1, video_output_dir='circle_videos', images_output_dir='circle_images'):
    # Create output directories if they don't exist
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # Create an imageio writer to save the frames as a video
    fps = int(1/delay)
    print(f"processing {len(IMAGES)} images into a {fps} fps video")
    video_filename = os.path.join(video_output_dir, 'robot_video.mp4')

    # Read images and create video frames
    video_frames = [imageio.imread(str(image)) for image in IMAGES]

    # Create video
    imageio.mimsave(video_filename, video_frames, fps=10)

    print(f'Video saved as: {video_filename}')

    # Saving images separately
    for idx, image_path in enumerate(IMAGES):
        image = imageio.imread(str(image_path))  # Read image data
        image_filename = os.path.join(images_output_dir, f'image_{idx}.png')
        imageio.imwrite(image_filename, image)
        print(f'Image {idx+1} saved as: {image_filename}')

    return video_filename


# ==================================
# generate circle coordinates
import json

data = {
    "delay": 0.05,
    "coordinates": []
}

# # Define the circle parameters
# radius = 10
# num_points = 36

# # Starting coordinates
# x_center = 0
# y_center = 0
# z = 0

# Define the circle parameters
radius = 6
num_points = 20

# Starting coordinates
x_center = 10
y_center = 10
z = 0

# Generate coordinates for the circle
for i in range(num_points):
    theta = 2 * math.pi * i / num_points
    x = x_center + radius * math.cos(theta)
    y = y_center + radius * math.sin(theta)
    data["coordinates"].append({"x": x, "y": y, "z": z})

# Add the starting point to close the circle
data["coordinates"].append({"x": x_center + radius, "y": y_center, "z": z})

json_data = json.dumps(data, indent=4)

# # Print JSON data
print(json_data)

# Process coordinates and create video
images, delay = process_coordinates(data)
video = create_circle_video(images, delay)

"""### circle video"""

from IPython.display import HTML
from base64 import b64encode
mp4 = open(video,'rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mp4">
</video>
""" % data_url)



# ===============================


"""### square coordinates"""



def create_square_video(IMAGES, delay=1, video_output_dir='square_videos', images_output_dir='square_images'):
    # Create output directories if they don't exist
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # Create an imageio writer to save the frames as a video
    fps = int(1/delay)
    print(f"processing {len(IMAGES)} images into a {fps} fps video")
    video_filename = os.path.join(video_output_dir, 'robot_video.mp4')

    # Read images and create video frames
    video_frames = [imageio.imread(str(image)) for image in IMAGES]

    # Create video
    imageio.mimsave(video_filename, video_frames, fps=10)

    print(f'Video saved as: {video_filename}')

    # Saving images separately
    for idx, image_path in enumerate(IMAGES):
        image = imageio.imread(str(image_path))  # Read image data
        image_filename = os.path.join(images_output_dir, f'image_{idx}.png')
        imageio.imwrite(image_filename, image)
        print(f'Image {idx+1} saved as: {image_filename}')

    return video_filename

# generate square coordinates

data = {
    "delay": 0.05,
    "coordinates": []
}

# Define the side length of the square
side_length = 10

# Starting coordinates
x_start = 0
y_start = 10
z = 0

# Generate coordinates for one side of the square
for i in range(side_length):
    data["coordinates"].append({"x": x_start, "y": y_start + i * 0.5, "z": z})

# Move along the next side of the square
for i in range(side_length):
    data["coordinates"].append({"x": x_start + i * 0.5, "y": y_start + side_length * 0.5, "z": z})

# Move along the third side of the square
for i in range(side_length):
    data["coordinates"].append({"x": x_start + side_length * 0.5, "y": y_start + side_length * 0.5 - i * 0.5, "z": z})

# Move along the fourth side of the square
for i in range(side_length):
    data["coordinates"].append({"x": x_start + side_length * 0.5 - i * 0.5, "y": y_start, "z": z})

# Add the starting point to close the square
data["coordinates"].append({"x": x_start, "y": y_start, "z": z})
json_data = json.dumps(data, indent=4)

# # Print JSON data
print(json_data)
images, delay = process_coordinates(data)
video = create_square_video(images, delay)

"""### square video"""

from IPython.display import HTML
from base64 import b64encode
mp4 = open(video,'rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mp4">
</video>
""" % data_url)



# =========================
# pentagonal 
import os
import imageio

def create_pentagon_video(IMAGES, delay=1, video_output_dir='pentagon_videos', images_output_dir='pentagon_images'):
    # Create output directories if they don't exist
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # Create an imageio writer to save the frames as a video
    fps = int(1/delay)
    print(f"processing {len(IMAGES)} images into a {fps} fps video")
    video_filename = os.path.join(video_output_dir, 'robot_video.mp4')

    # Read images and create video frames
    video_frames = [imageio.imread(str(image)) for image in IMAGES]

    # Create video
    imageio.mimsave(video_filename, video_frames, fps=10)

    print(f'Video saved as: {video_filename}')

    # Saving images separately
    for idx, image_path in enumerate(IMAGES):
        image = imageio.imread(str(image_path))  # Read image data
        image_filename = os.path.join(images_output_dir, f'image_{idx}.png')
        imageio.imwrite(image_filename, image)
        print(f'Image {idx+1} saved as: {image_filename}')

    return video_filename
# =====================
# generate pentagonal coordinates
data = {
    "delay": 0.1,
    "coordinates": []
}

# Define the side length of the pentagon
side_length = 5

# Starting coordinates
x_start = 10
y_start = 20
z = 0

# Calculate angles for pentagon
angle = 360 / 5

# Generate coordinates for pentagon
for i in range(5):
    x = x_start + side_length * math.cos(math.radians(i * angle))
    y = y_start + side_length * math.sin(math.radians(i * angle))
    data["coordinates"].append({"x": x, "y": y, "z": z})

# Add the starting point to close the pentagon
data["coordinates"].append(data["coordinates"][0])

json_data = json.dumps(data, indent=4)

# Print JSON data
print(json_data)

images, delay = process_coordinates(data)
video = create_pentagon_video(images, delay)


# ==========
# create video
from IPython.display import HTML
from base64 import b64encode
mp4 = open(video,'rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mp4">
</video>
""" % data_url)

