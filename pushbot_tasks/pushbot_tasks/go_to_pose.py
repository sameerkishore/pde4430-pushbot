"""Send PushBot to one pose with Nav2 and report progress.

    ros2 run pushbot_tasks go_to_pose --ros-args -p x:=6.2 -p y:=2.2 -p yaw:=0.0

Coordinates are in the map frame, whose origin is where the robot starts.
(6.2, 2.2) is the centre of the green goal zone.
"""
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from pushbot_tasks.nav_utils import make_pose, wait_for_nav2


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.declare_parameter('x', 6.2)
    nav.declare_parameter('y', 2.2)
    nav.declare_parameter('yaw', 0.0)
    x = nav.get_parameter('x').value
    y = nav.get_parameter('y').value
    yaw = nav.get_parameter('yaw').value

    wait_for_nav2(nav)

    goal = make_pose(nav, x, y, yaw)
    nav.info(f'Going to ({x:.2f}, {y:.2f}, yaw {yaw:.2f})')
    nav.goToPose(goal)

    # goToPose returns straight away; the robot drives while we poll for feedback
    i = 0
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback and i % 10 == 0:
            nav.info(f'Distance remaining: {feedback.distance_remaining:.2f} m, '
                     f'recoveries: {feedback.number_of_recoveries}')
        i += 1
        rclpy.spin_once(nav, timeout_sec=0.1)

    result = nav.getResult()
    if result == TaskResult.SUCCEEDED:
        nav.info('Goal reached')
    elif result == TaskResult.CANCELED:
        nav.warn('Goal was cancelled')
    else:
        nav.error('Goal failed')

    nav.destroyNode()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
