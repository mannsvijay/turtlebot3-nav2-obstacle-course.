#!/usr/bin/env bash
# Install everything this demo needs on Ubuntu 22.04 with ROS 2 Humble.
# Usage: ./setup.sh   (run from inside the cloned repo)
set -euo pipefail

if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "ROS 2 Humble not found. Install it first (Desktop variant):"
  echo "  https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html"
  exit 1
fi

sudo apt update
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-gazebo \
  ros-humble-slam-toolbox \
  python3-colcon-common-extensions \
  python3-yaml

# Build the package in the workspace that contains this repo (…/ws/src/<repo>).
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "Building workspace: $WS_DIR"
source /opt/ros/humble/setup.bash
cd "$WS_DIR"
colcon build --symlink-install --packages-select tb3_nav2_demo

echo
echo "Done. In every new terminal run:"
echo "  source /opt/ros/humble/setup.bash && source $WS_DIR/install/setup.bash"
echo "Then: ros2 launch tb3_nav2_demo demo.launch.py"
