"""Run slam_toolbox (online async mapping) for PushBot.

Start the simulation first (the empty arena is best for mapping):
    ros2 launch pushbot_gazebo sim.launch.py world:=arena_empty.sdf
Then in a second terminal:
    ros2 launch pushbot_navigation slam.launch.py
Drive around with teleop, then save the map:
    cd ~/pde4430_ws/src/pde4430_pushbot/pushbot_navigation/maps
    ros2 run nav2_map_server map_saver_cli -f arena

In Jazzy, slam_toolbox is a lifecycle node: it must be configured and then
activated before it does anything. slam_toolbox's own launch file does this,
so we include it and only swap in our parameter file.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg = get_package_share_directory('pushbot_navigation')
    slam_pkg = get_package_share_directory('slam_toolbox')

    return LaunchDescription([
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(pkg, 'config', 'slam_params.yaml'),
                              description='slam_toolbox parameter file'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
            launch_arguments={
                'slam_params_file': LaunchConfiguration('params_file'),
                'use_sim_time': 'true',
            }.items(),
        ),
    ])
