from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    return LaunchDescription([

        ExecuteProcess(
            cmd=[
                '/ws/venv/bin/python3',
                '/ws/ros_ws/src/sibotr2/ackm_mldrive/scripts/train_model.py',
                '--ros-args',
                '-p', 'base_folder:=5e421e69',
                '-p', 'modelname:=set0.keras',
                '-p', 'epochs:=10',
                '-p', 'steps_per_epoch:=100',
                '-p', 'batch_size:=20',
                '-p', 'validation_steps:=50',
            ],
            output='screen',
            emulate_tty=True
        )

    ])
    
