#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import cv2
import numpy as np
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from tensorflow.keras.models import load_model

import pathlib
import os


def preProcess(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img / 255
    return img


class MLDriveNode(Node):

    def __init__(self):
        super().__init__('ml_driving')

        # Params
        self.declare_parameter('image_raw_topic', '/camera_front/image_raw')
        self.declare_parameter('twist_cmd_topic', '/cmd_vel')
        self.declare_parameter('twist_linear_x', 0.5)
        self.declare_parameter('modelname', 'set2.keras')

        image_topic = self.get_parameter('image_raw_topic').value
        cmd_topic = self.get_parameter('twist_cmd_topic').value
        self.twist_linear_x = self.get_parameter('twist_linear_x').value
        modelname = self.get_parameter('modelname').value

        # Model path (alinha com train)
        model_path = os.path.join('/ws/models/ackm_mldrive', modelname)
        self.get_logger().info(f'Loading model: {model_path}')

        self.model = load_model(model_path)

        # State
        self.bridge = CvBridge()
        self.img = None
        self.begin_img = False

        # Subs / pubs
        self.create_subscription(Image, image_topic, self.img_callback, 10)
        self.pub = self.create_publisher(Twist, cmd_topic, 10)

        # Timer (10 Hz)
        self.timer = self.create_timer(0.1, self.loop)

    def img_callback(self, msg):
        self.img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        self.begin_img = True

    def loop(self):
        if not self.begin_img:
            return

        processed = preProcess(self.img)

        # Debug view (opcional)
        cv2.imshow('Processed', processed)
        cv2.imshow('Raw', self.img)
        cv2.waitKey(1)

        # ✔ FIX TF 2.21
        image = np.asarray([processed], dtype=np.float32)
        steering = float(self.model.predict(image, verbose=0)[0][0])

        twist = Twist()
        twist.linear.x = self.twist_linear_x
        twist.angular.z = steering

        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = MLDriveNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    
