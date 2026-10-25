"""Drop obstacles that are NOT on the map into the running simulation.

Run this in a second terminal while the robot is driving:
    ros2 launch tb3_nav2_demo surprise_obstacles.launch.py

Both obstacles sit on the robot's planned route. Nav2 sees them only through
the lidar (costmap obstacle layers), so the robot has to replan around them.
To reset, delete them in Gazebo (right-click -> Delete) or restart the demo.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

# (entity name, sdf file, x, y): positions chosen to block the default routes
SURPRISES = [
    ('surprise_box', 'surprise_box.sdf', '0.8', '-1.0'),
    ('surprise_cylinder', 'surprise_cylinder.sdf', '2.75', '0.8'),
]


def generate_launch_description():
    models = os.path.join(get_package_share_directory('tb3_nav2_demo'), 'models')
    return LaunchDescription([
        Node(package='gazebo_ros', executable='spawn_entity.py', output='screen',
             arguments=['-entity', name, '-file', os.path.join(models, sdf),
                        '-x', x, '-y', y, '-z', '0.0'])
        for name, sdf, x, y in SURPRISES
    ])
