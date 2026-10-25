#!/usr/bin/env python3
"""Drive the robot through a patrol of goals with the Nav2 Simple Commander API.

    ros2 run tb3_nav2_demo send_goals          # run the patrol once
    ros2 run tb3_nav2_demo send_goals --loop   # repeat until Ctrl+C

Goals are in the map frame and match the obstacle_course world layout.
"""
import math
import sys

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration

SPAWN = (-3.0, -2.0, 0.0)  # x, y, yaw: must match the spawn pose in demo.launch.py

# (x, y, yaw, label)
GOALS = [
    (3.0, 2.2, math.pi / 2, 'G1: far corner of the east room (S-shaped route)'),
    (0.8, 0.5, math.pi, 'G2: middle room, between the pillars'),
    (-3.0, -2.0, 0.0, 'Home: back to the start'),
]

GOAL_TIMEOUT = Duration(seconds=180.0)


def make_pose(navigator, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def navigate_to(navigator, x, y, yaw, label):
    print(f'\n-> {label}  ({x:.1f}, {y:.1f})')
    if not navigator.goToPose(make_pose(navigator, x, y, yaw)):
        print('   goal was rejected by Nav2')
        return False

    ticks = 0
    while not navigator.isTaskComplete():  # spins ~10 Hz internally
        ticks += 1
        feedback = navigator.getFeedback()
        if feedback and ticks % 10 == 0:
            print(f'   {feedback.distance_remaining:5.2f} m remaining | '
                  f'recoveries: {feedback.number_of_recoveries}')
            if Duration.from_msg(feedback.navigation_time) > GOAL_TIMEOUT:
                print('   timed out, cancelling goal')
                navigator.cancelTask()

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('   reached goal')
        return True
    print(f'   goal ended with status: {result}')
    return False


def main():
    loop = '--loop' in sys.argv
    rclpy.init()
    navigator = BasicNavigator()

    # Publishing the initial pose explicitly keeps AMCL consistent with the
    # spawn pose (waitUntilNav2Active re-sends this pose until AMCL answers).
    navigator.setInitialPose(make_pose(navigator, *SPAWN))
    navigator.waitUntilNav2Active()

    try:
        while True:
            results = [navigate_to(navigator, *goal) for goal in GOALS]
            print(f'\nPatrol finished: {sum(results)}/{len(results)} goals reached')
            if not loop:
                break
    except KeyboardInterrupt:
        navigator.cancelTask()
    finally:
        navigator.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
