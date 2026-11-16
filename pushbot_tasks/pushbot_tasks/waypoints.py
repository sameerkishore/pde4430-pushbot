"""Session 2 home task: patrol the arena through a list of waypoints.

    ros2 run pushbot_tasks waypoints

Complete the TODOs. See the Session 2 handout, Part B.
Coordinates are in the map frame (origin = where the robot starts).
"""
import time

import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from pushbot_tasks.nav_utils import make_pose, wait_for_nav2

# (x, y, yaw) in the map frame.
# TODO 1: choose at least four waypoints that take the robot around the
# divider and the pillar and finish in the goal zone at (6.2, 2.2).
# Use "Publish Point" in RViz to read coordinates off the map.
WAYPOINTS = [
    (1.5, 0.0, 0.0),
]


def main():
    rclpy.init()
    nav = BasicNavigator()
    wait_for_nav2(nav)

    # TODO 2: turn WAYPOINTS into a list of PoseStamped with make_pose()
    poses = []

    start = time.time()
    # TODO 3: send the poses with nav.followWaypoints(poses)
    #         (it stops at each one; nav.goThroughPoses(poses) is the
    #         alternative that drives through them without stopping)

    # TODO 4: while the task is running, print which waypoint the robot is on
    #         (nav.getFeedback().current_waypoint) whenever it changes

    # TODO 5: when it finishes, print the result (nav.getResult()), how long it
    #         took, and which waypoints were missed. getResult() only says
    #         SUCCEEDED / FAILED / CANCELED; the full result message is
    #         nav.result_future.result().result, whose missed_waypoints list
    #         holds the index of each waypoint the robot could not reach.

    nav.destroyNode()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
