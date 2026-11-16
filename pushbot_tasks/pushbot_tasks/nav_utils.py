"""Small helpers shared by the PushBot task scripts."""
import math

import rclpy
from geometry_msgs.msg import PoseStamped


def make_pose(navigator, x, y, yaw=0.0, frame='map'):
    """A PoseStamped at (x, y) facing yaw (radians), stamped now, in the map frame."""
    pose = PoseStamped()
    pose.header.frame_id = frame
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    # A rotation of yaw about z, as a quaternion
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def wait_for_nav2(navigator, timeout_s=3.0):
    """Wait until Nav2 is active, without resetting AMCL's pose estimate.

    BasicNavigator.waitUntilNav2Active() publishes a default initial pose of
    (0, 0) until it hears from AMCL. AMCL already knows where the robot is
    (set_initial_pose in nav2_params.yaml, or 2D Pose Estimate in RViz), so we
    first listen for AMCL's latest pose. If it arrives, the navigator does not
    publish its default, and running a script twice cannot teleport the
    robot's estimate back to the start.
    """
    steps = int(timeout_s / 0.1)
    for _ in range(steps):
        if navigator.initial_pose_received:
            break
        rclpy.spin_once(navigator, timeout_sec=0.1)
    navigator.waitUntilNav2Active()
