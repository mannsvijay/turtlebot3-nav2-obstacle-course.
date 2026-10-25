"""One-command demo: Gazebo obstacle course + TurtleBot3 Burger + Nav2 + RViz.

    ros2 launch tb3_nav2_demo demo.launch.py
    ros2 launch tb3_nav2_demo demo.launch.py headless:=true    # no Gazebo GUI
    ros2 launch tb3_nav2_demo demo.launch.py slam:=true        # map with SLAM Toolbox
"""
import os
import tempfile

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable, TimerAction)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# Must match amcl.initial_pose in config/nav2_overrides.yaml.
SPAWN_X, SPAWN_Y = '-3.0', '-2.0'
ROBOT_MODEL = 'burger'  # params are tuned for the Burger footprint and speed


def deep_merge(base, override):
    """Recursively merge `override` into `base` (in place) and return it."""
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def build_params_file(default_params, overrides_file):
    """Write Nav2's stock params + our overrides to a temp file, return its path."""
    with open(default_params, 'r') as f:
        params = yaml.safe_load(f)
    with open(overrides_file, 'r') as f:
        overrides = yaml.safe_load(f) or {}
    deep_merge(params, overrides)
    out = tempfile.NamedTemporaryFile(
        'w', prefix='tb3_nav2_params_', suffix='.yaml', delete=False)
    yaml.safe_dump(params, out, sort_keys=False)
    out.close()
    return out.name


def generate_launch_description():
    pkg = get_package_share_directory('tb3_nav2_demo')
    gazebo_ros = get_package_share_directory('gazebo_ros')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    nav2_bringup = get_package_share_directory('nav2_bringup')

    world = os.path.join(pkg, 'worlds', 'obstacle_course.world')
    default_map = os.path.join(pkg, 'maps', 'obstacle_course.yaml')
    default_params = build_params_file(
        os.path.join(nav2_bringup, 'params', 'nav2_params.yaml'),
        os.path.join(pkg, 'config', 'nav2_overrides.yaml'))
    rviz_config = os.path.join(nav2_bringup, 'rviz', 'nav2_default_view.rviz')

    headless = LaunchConfiguration('headless')
    use_rviz = LaunchConfiguration('use_rviz')
    slam = LaunchConfiguration('slam')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    # Gazebo needs the TurtleBot3 meshes on its model path. Keep whatever the
    # user already has, plus the system default models.
    model_path = os.pathsep.join(filter(None, [
        os.environ.get('GAZEBO_MODEL_PATH', ''),
        os.path.join(tb3_gazebo, 'models'),
        '/usr/share/gazebo-11/models',
    ]))

    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='false',
                              description='Run Gazebo without its GUI'),
        DeclareLaunchArgument('use_rviz', default_value='true',
                              description='Start RViz'),
        DeclareLaunchArgument('slam', default_value='false',
                              description='Build a map with SLAM Toolbox instead of AMCL'),
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Map yaml used for localization'),
        DeclareLaunchArgument('params_file', default_value=default_params,
                              description='Full Nav2 params file'),

        SetEnvironmentVariable('TURTLEBOT3_MODEL', ROBOT_MODEL),
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path),
        # Stop Gazebo from trying to reach the online model database on start-up
        # (a common cause of a 30+ second hang on first launch).
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),

        # --- Simulation -------------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_ros, 'launch', 'gzserver.launch.py')),
            launch_arguments={'world': world}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_ros, 'launch', 'gzclient.launch.py')),
            condition=UnlessCondition(headless)),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(tb3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')),
            launch_arguments={'x_pose': SPAWN_X, 'y_pose': SPAWN_Y}.items()),

        # --- Navigation (delayed so the robot and /clock exist first) ---------
        TimerAction(period=5.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')),
                launch_arguments={
                    'map': map_yaml,
                    'slam': slam,
                    'use_sim_time': 'true',
                    'params_file': params_file,
                    'autostart': 'true',
                }.items()),
        ]),

        TimerAction(period=3.0, actions=[
            Node(package='rviz2', executable='rviz2', name='rviz2',
                 arguments=['-d', rviz_config],
                 parameters=[{'use_sim_time': True}],
                 output='screen',
                 condition=IfCondition(use_rviz)),
        ]),
    ])
