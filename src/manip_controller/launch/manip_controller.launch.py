from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='manip_controller',
            executable='gripper_node',
            name='gripper_node',
            output='screen'
        ),
        Node(
            package='manip_controller',
            executable='ik_node',
            name='gripper_node',
            output='screen'
        ),
    ])
