#!/usr/bin/env python3
"""
Composed nav2 bringup — run all nav2 nodes in ONE process / one DDS participant.

Why: the default bringup (`nav2_bringup/navigation_launch.py`) spawns ~8 separate
processes. Each is its own DDS participant and independently builds discovery/matching
state for the entire ROS graph, so memory scales badly with stack size — on a busy
graph the startup transient reaches multiple GB and gets OOM-killed inside a
memory-limited container. Composition loads every nav2 node into a single component
container, so that per-graph cost is paid once: the startup peak drops sharply and
steady-state settles under ~100 MB. This is nav2's recommended efficient deployment and
keeps the default RMW (Fast DDS).

Behaves like the default navigation_launch.py (same args/defaults), just composed.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    container_name = 'nav2_container'

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use the /clock topic (simulation time) if true')
    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(nav2_bringup_dir, 'params', 'nav2_params.yaml'),
        description='Full path to the ROS 2 parameters file for all nav2 nodes')
    declare_autostart = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically bring the nav2 lifecycle nodes to active')

    # Single process to host every nav2 node as a composable component.
    container = Node(
        package='rclcpp_components',
        executable='component_container_isolated',
        name=container_name,
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # Reuse nav2's own launch, which (with use_composition) loads the nodes into the
    # container above instead of spawning separate processes.
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'use_composition': 'True',
            'container_name': container_name,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
        }.items(),
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_params_file,
        declare_autostart,
        container,
        navigation,
    ])
