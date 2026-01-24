from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('manip_controller'),
                    'launch',
                    'manip_controller.launch.py'
                ])
            ])
        ),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('referees'),
                    'launch',
                    'referees.launch.py'
                ])
            ])
        ),
        Node(
            package='conveyor_controller',
            executable='constant_speed',
            name='conveyor_controller',
            output='screen'
        ),

    ])
