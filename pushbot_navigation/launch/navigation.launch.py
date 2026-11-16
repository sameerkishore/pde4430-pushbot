"""Localise PushBot on a saved map and start Nav2, with an RViz window set up for navigation.

Start the simulation first, without its own RViz:
    ros2 launch pushbot_gazebo sim.launch.py rviz:=false
Then in a second terminal:
    ros2 launch pushbot_navigation navigation.launch.py                          # your map: maps/arena.yaml
    ros2 launch pushbot_navigation navigation.launch.py map:=reference_arena.yaml  # the reference map

In RViz, click "Nav2 Goal" and then click-and-drag on the map to send a goal.

This includes nav2_bringup's bringup_launch.py, which starts:
  - localisation: map_server + amcl
  - navigation: planner, controller, smoother, behaviours, bt_navigator,
    waypoint_follower, velocity_smoother, collision_monitor (and two servers
    this module doesn't use: route_server, docking_server)
all configured from config/nav2_params.yaml.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('pushbot_navigation')
    nav2_bringup = get_package_share_directory('nav2_bringup')
    maps_dir = os.path.join(pkg, 'maps', '')

    map_arg = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    rviz = LaunchConfiguration('rviz')

    # map:=arena.yaml (a file in this package's maps/ folder) or a full path
    map_file = PythonExpression([
        "'", map_arg, "' if '/' in '", map_arg, "' else '", maps_dir, "' + '", map_arg, "'"
    ])

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_file,
            'params_file': params_file,
            'use_sim_time': 'true',
            'autostart': 'true',
            'slam': 'False',
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg, 'rviz', 'nav.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value='arena.yaml',
                              description='Map yaml: a name in pushbot_navigation/maps or a full path'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(pkg, 'config', 'nav2_params.yaml'),
                              description='Nav2 parameter file'),
        DeclareLaunchArgument('rviz', default_value='true', description='Start RViz'),
        nav2,
        rviz_node,
    ])
