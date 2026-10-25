import os
from glob import glob

from setuptools import setup

package_name = 'tb3_nav2_demo'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        (os.path.join('share', package_name, 'models'), glob('models/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Manan Vijay',
    maintainer_email='you@example.com',
    description='TurtleBot3 + Nav2 autonomous navigation demo in Gazebo',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'send_goals = tb3_nav2_demo.send_goals:main',
        ],
    },
)
