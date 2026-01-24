from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='referees',
            executable='pickup_referee',
            name='pickup_referee',
            output='screen'
        ),
        Node(
            package='referees',
            executable='container_referee',
            name='container_referee',
            output='screen'
        ),
        Node(
            package='referees',
            executable='tally_referee',
            name='tally_referee',
            output='screen'
        ),
    ])
