"""Start Gazebo Harmonic with the arena, spawn PushBot and bridge topics to ROS 2.

    ros2 launch pushbot_gazebo sim.launch.py
    ros2 launch pushbot_gazebo sim.launch.py rviz:=false
    ros2 launch pushbot_gazebo sim.launch.py headless:=true   # no Gazebo window
    ros2 launch pushbot_gazebo sim.launch.py world:=arena_empty.sdf   # no boxes, for mapping

Then drive it from a second terminal:
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_pkg = get_package_share_directory('pushbot_description')
    gz_pkg = get_package_share_directory('pushbot_gazebo')
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(desc_pkg, 'urdf', 'pushbot.urdf.xacro')
    bridge_config = os.path.join(gz_pkg, 'config', 'bridge.yaml')
    rviz_config = os.path.join(gz_pkg, 'rviz', 'sim.rviz')

    # world:=arena_empty.sdf (a file in this package's worlds/ folder) or a full path
    world_arg = LaunchConfiguration('world')
    world = PythonExpression([
        "'", world_arg, "' if '/' in '", world_arg, "' else '",
        os.path.join(gz_pkg, 'worlds', ''), "' + '", world_arg, "'"
    ])
    rviz = LaunchConfiguration('rviz')
    headless = LaunchConfiguration('headless')
    x, y, yaw = LaunchConfiguration('x'), LaunchConfiguration('y'), LaunchConfiguration('yaw')

    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    # -r starts the simulation running; -s runs the server only (no GUI window)
    gz_args = PythonExpression([
        "'-r -s --headless-rendering ' if '", headless, "' == 'true' else '-r '"
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': [gz_args, world], 'on_exit_shutdown': 'true'}.items(),
    )

    # Publishes /robot_description and the TF for every fixed and moving joint
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        output='screen',
    )

    # Reads /robot_description and asks Gazebo to create the robot
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'pushbot',
                   '-x', x, '-y', y, '-z', '0.01', '-Y', yaw],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config, 'use_sim_time': True}],
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='arena.sdf',
                              description='World file: a name in pushbot_gazebo/worlds or a full path'),
        DeclareLaunchArgument('rviz', default_value='true', description='Start RViz'),
        DeclareLaunchArgument('headless', default_value='false',
                              description='Run Gazebo without its GUI window'),
        DeclareLaunchArgument('x', default_value='-3.0', description='Spawn x (m)'),
        DeclareLaunchArgument('y', default_value='0.0', description='Spawn y (m)'),
        DeclareLaunchArgument('yaw', default_value='0.0', description='Spawn heading (rad)'),
        gazebo,
        robot_state_publisher,
        spawn,
        bridge,
        rviz_node,
    ])
