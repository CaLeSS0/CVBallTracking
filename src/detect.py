"""

The following is using the model and some code basis from https://github.com/eriklindernoren/PyTorch-YOLOv3

It is a modification of his code to read in and use the pre-trained YOLOv3 model, modified to do video tracking.

"""


from yolo.models import *
from yolo.utils.utils import *
from yolo.utils.datasets import *

import os
import sys
import time
import datetime
import argparse
from pathlib import Path

from PIL import Image

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator

import numpy as np

import cv2 as cv2

"""
detect(image) returns [bounding boxes]

Detect takes in an image and returns the bounding boxes of all balls in the image

"""

def detect(image):
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_folder", type=str, default="data/samples", help="path to dataset")
    parser.add_argument("--model_def", type=str, default="config/yolov3.cfg", help="path to model definition file")
    parser.add_argument("--weights_path", type=str, default="weights/yolov3.weights", help="path to weights file")
    parser.add_argument("--class_path", type=str, default="data/coco.names", help="path to class label file")
    parser.add_argument("--conf_thres", type=float, default=0.8, help="object confidence threshold")
    parser.add_argument("--nms_thres", type=float, default=0.4, help="iou thresshold for non-maximum suppression")
    parser.add_argument("--batch_size", type=int, default=1, help="size of the batches")
    parser.add_argument("--n_cpu", type=int, default=0, help="number of cpu threads to use during batch generation")
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    parser.add_argument("--checkpoint_model", type=str, help="path to checkpoint model")
    opt = parser.parse_args()
    print(opt)
    """

    model_def = 'yolo/config/yolov3.cfg'
    weights_path = 'yolo/weights/yolov3.weights'
    class_path = 'yolo/data/coco.names'
    conf_threshold = 0.8
    nms_threshold = 0.4
    batch_size = 1
    n_cpu = 0
    image_size = 416 #320 #416    

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    os.makedirs("output", exist_ok=True)

    # Set up model
    model = Darknet(model_def, img_size=image_size).to(device)

    if weights_path.endswith(".weights"):
        # Load darknet weights
        model.load_darknet_weights(weights_path)
    else:
        # Load checkpoint weights
        model.load_state_dict(torch.load(weights_path))

    model.eval()  # Set in evaluation mode

    # Resize the image
    image = cv2.resize(image, (image_size, image_size))

    # Write the image to a temporary file to put into the dataloader
    path = Path(__file__).parent.absolute()
    path = os.path.join(path, 'temp')
    cv2.imwrite(os.path.join(path, 'in.jpg'), image)

    image_folder = 'temp'

    dataloader = DataLoader(
        ImageFolder(image_folder, img_size=image_size),
        batch_size=batch_size,
        shuffle=False,
        num_workers=n_cpu,
    )

    classes = load_classes(class_path)  # Extracts class labels from file

    Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor

    imgs = []  # Stores image paths
    img_detections = []  # Stores detections for each image index

    """
    #print("\nPerforming object detection:")
    prev_time = time.time()
    # Should only run once (one image in the DataLoader)
    for batch_i, (img_paths, input_imgs) in enumerate(dataloader):
        # Configure input
        input_imgs = Variable(input_imgs.type(Tensor))

        # Get detections
        with torch.no_grad():
            detections = model(input_imgs)
            detections = non_max_suppression(detections, conf_thres, nms_thres)

        # Log progress
        #current_time = time.time()
        #inference_time = datetime.timedelta(seconds=current_time - prev_time)
        #prev_time = current_time
        print("\t+ Batch %d, Inference Time: %s" % (batch_i, inference_time))

        # Save image and detections
        #imgs.extend(img_paths)
        #img_detections.extend(detections)
    """

    
    image = np.array([image])
    image = torch.from_numpy(image)
    image = image.reshape(1, 3, image_size, image_size)
    
    image = image.float()
    image = Variable(image)

    # Array of bounding boxes of balls to return
    boxes = np.array([])

    images = []
    iter_detections =[]

    # Go through dataloader
    for batch_i, (img_paths, input_imgs) in enumerate(dataloader):
        input_imgs = Variable(input_imgs.type(Tensor))

        with torch.no_grad():
            detections = model(input_imgs)
            detections = non_max_suppression(detections, conf_threshold, nms_threshold)

        images.extend(img_paths)
        iter_detections.extend(detections)


    for imgi, (path, detections) in enumerate(zip(images,iter_detections)):
        for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
            if classes[int(cls_pred)] == 'Sports Ball':
                boxes = np.append(boxes, [x1, y1, x2-x1, y2-y1])

    return boxes

    """
    # Bounding-box colors
    cmap = plt.get_cmap("tab20b")
    colors = [cmap(i) for i in np.linspace(0, 1, 20)]

    print("\nSaving images:")
    # Iterate through images and save plot of detections
    for img_i, (path, detections) in enumerate(zip(images,iter_detections)):#in enumerate(zip(imgs, img_detections)):

        print("(%d) Image: '%s'" % (img_i, path))

        # Create plot
        print(path)
        img = img_i#np.array(Image.open(path))
        plt.figure()
        fig, ax = plt.subplots(1)
        ax.imshow(img)

        # Draw bounding boxes and labels of detections
        if detections is not None:
            # Rescale boxes to original image
            detections = rescale_boxes(detections, opt.img_size, img.shape[:2])
            unique_labels = detections[:, -1].cpu().unique()
            n_cls_preds = len(unique_labels)
            bbox_colors = random.sample(colors, n_cls_preds)
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:

                print("\t+ Label: %s, Conf: %.5f" % (classes[int(cls_pred)], cls_conf.item()))

                # See if this is a ball
                if classes[int(cls_pred)] == 'Sports Ball':
                    # If so, append to our list of (x,y,w,h) bounding boxes to return
                    boxes = np.append(boxes, [x1, y1, x2-x1, y2-y1])

                box_w = x2 - x1
                box_h = y2 - y1

                color = bbox_colors[int(np.where(unique_labels == int(cls_pred))[0])]
                # Create a Rectangle patch
                bbox = patches.Rectangle((x1, y1), box_w, box_h, linewidth=2, edgecolor=color, facecolor="none")
                # Add the bbox to the plot
                ax.add_patch(bbox)
                # Add label
                plt.text(
                    x1,
                    y1,
                    s=classes[int(cls_pred)],
                    color="white",
                    verticalalignment="top",
                    bbox={"color": color, "pad": 0},
                )

        # Save generated image with detections
        plt.axis("off")
        plt.gca().xaxis.set_major_locator(NullLocator())
        plt.gca().yaxis.set_major_locator(NullLocator())
        filename = path.split("/")[-1].split(".")[0]
        plt.savefig(f"output/{filename}.png", bbox_inches="tight", pad_inches=0.0)
        plt.close()
        
    return boxes
    """
