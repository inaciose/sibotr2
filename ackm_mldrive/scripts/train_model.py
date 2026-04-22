#!/usr/bin/env python3

from utils import *
from sklearn.model_selection import train_test_split
import os

import rclpy
from rclpy.node import Node

from tensorflow.keras.models import load_model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class TrainNode(Node):

    def __init__(self):
        super().__init__('ml_training')

        # Params
        self.declare_parameter('base_folder', 'set2')
        self.declare_parameter('modelname', 'set2.keras')
        self.declare_parameter('epochs', 10)
        self.declare_parameter('steps_per_epoch', 100)
        self.declare_parameter('batch_size', 20)
        self.declare_parameter('validation_steps', 50)
        self.declare_parameter('new_model', True)

        base_folder = self.get_parameter('base_folder').value
        modelname = self.get_parameter('modelname').value
        epochs = self.get_parameter('epochs').value
        steps_per_epoch = self.get_parameter('steps_per_epoch').value
        batch_size = self.get_parameter('batch_size').value
        validation_steps = self.get_parameter('validation_steps').value
        new_model = self.get_parameter('new_model').value

        print('base_folder:', base_folder)
        print('modelname:', modelname)

        path_data = '/ws/data/ackm_mldrive/' + base_folder
        data = importDataInfo(path_data + '/')

        print('\nData loadind')

        # Balance
        balanceData(data, display=True)

        # Load
        imagesPath, steerings = loadData(path_data, data)

        # Split
        xTrain, xVal, yTrain, yVal = train_test_split(
            imagesPath, steerings, test_size=0.01, random_state=5)

        print('Train:', len(xTrain))
        print('Val:', len(xVal))

        # Model path
        model_path = os.path.join('/ws/models/ackm_mldrive', modelname)
        os.makedirs('/ws/models/ackm_mldrive', exist_ok=True)

        if new_model:
            model = createModel()
        else:
            model = load_model(model_path)

        model.summary()

        # ✔ TRAINING CORRIGIDO
        history = model.fit(
            batchGen(xTrain, yTrain, batch_size, True),
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_data=batchGen(xVal, yVal, batch_size, False),
            validation_steps=validation_steps
        )

        #model.save(model_path)
        model.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error')
        model.save(model_path)

        print('\nModel saved to', model_path)

        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.legend(['Training', 'Validation'])
        plt.title('Loss')
        plt.xlabel('Epoch')
        plt.show()


def main(args=None):
    rclpy.init(args=args)
    node = TrainNode()
    rclpy.spin_once(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

