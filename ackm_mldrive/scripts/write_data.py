#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import cv2
import numpy as np
import pandas as pd
import os
import uuid
import pathlib
import signal
import sys
import datetime

from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from PIL import Image as Image_pil

class WriteDataNode(Node):

    def __init__(self):
        super().__init__('write_data')

        # Params
        self.declare_parameter('image_raw_topic', '/camera_front/image_raw')
        self.declare_parameter('twist_cmd_topic', '/cmd_vel')
        self.declare_parameter('base_folder', 'set3')

        image_raw_topic = self.get_parameter('image_raw_topic').get_parameter_value().string_value
        twist_cmd_topic = self.get_parameter('twist_cmd_topic').get_parameter_value().string_value
        base_folder = self.get_parameter('base_folder').get_parameter_value().string_value

        # Paths
        #s = str(pathlib.Path(__file__).parent.absolute())
        #self.data_path = s + '/../data' + base_folder
        
        base_path = '/ws/data/ackm_mldrive'
        self.data_path = base_path + '/' + base_folder        

        if os.path.exists(self.data_path):
            self.get_logger().error('SET EXISTS SELECT RANDOM NAME')
            while True:
                random_folder = str(uuid.uuid4())[:8]
                candidate = os.path.join(base_path, random_folder)
                if not os.path.exists(candidate):
                    self.data_path = candidate
                    break

        os.makedirs(os.path.join(self.data_path, 'IMG'), exist_ok=True)    
        print(self.data_path)

        # State
        self.angular = 0.0
        self.linear = 0.0
        self.begin_cmd = False
        self.begin_img = False

        self.bridge = CvBridge()
        self.img_rgb = None

        self.driving_log = pd.DataFrame(columns=['Center', 'Steering'])

        # Subs
        self.create_subscription(Twist, twist_cmd_topic, self.cmd_callback, 10)
        self.create_subscription(Image, image_raw_topic, self.img_callback, 10)

        # Timer (equivalente ao Rate loop)
        self.timer = self.create_timer(0.1, self.loop)  # 10 Hz

        signal.signal(signal.SIGINT, self.signal_handler)

    def cmd_callback(self, msg):
        self.angular = float(msg.angular.z)
        self.linear = float(msg.linear.x)
        self.begin_cmd = True

    def img_callback(self, msg):
        self.img_rgb = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        self.begin_img = True

    def loop(self):
        if not (self.begin_cmd and self.begin_img):
            return

        if abs(self.linear) < 1e-3:   # threshold evita floats ~0
            return
            
        curr_time = datetime.datetime.now()
        image_name = f"{curr_time.year}_{curr_time.month}_{curr_time.day}__{curr_time.hour}_{curr_time.minute}_{curr_time.second}__{curr_time.microsecond}.jpg"

        row = pd.DataFrame([[image_name, self.angular]], columns=['Center', 'Steering'])
        self.driving_log = pd.concat([self.driving_log, row], ignore_index=True)

        # Save image
        dim = (320, 160)
        img = cv2.resize(self.img_rgb, dim, interpolation=cv2.INTER_AREA)
        image_saved = Image_pil.fromarray(img)
        image_saved.save(self.data_path + '/IMG/' + image_name)

        self.get_logger().info('Image Saved')

    def signal_handler(self, sig, frame):
        self.driving_log.to_csv(self.data_path + '/driving_log.csv', mode='a', index=False, header=False)
        rclpy.shutdown()
        sys.exit(0)


def main(args=None):
    rclpy.init(args=args)
    node = WriteDataNode()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
    
