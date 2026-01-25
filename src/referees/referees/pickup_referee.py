import re
from numpy import result_type
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from functools import partial
from .object_referee import ObjectReferee, DEFAULT_REGEXPS

ZERO_LEVEL = 1.11
ZERO_LEVEL_EPS = 0.001

class PickupRefereeNode(ObjectReferee):
    def __init__(self):
        super().__init__(
                'pickup_referee',
                taget_object_regexps=DEFAULT_REGEXPS
        )
        self.report_pub = self.create_publisher(
            String,
            '/referee/pickup',
            qos_profile=10
        )
        self.get_logger().info('### PICKUP REFEREE READY ###')

    
    def process_odom_cb(self, topic_name: str, msg: Odometry):
        below_zero_level = msg.pose.pose.position.z < ZERO_LEVEL + ZERO_LEVEL_EPS
        # if 'box' in topic_name and 'big' in topic_name:
        #     self.get_logger().info(str(msg.pose.pose.position.z))
        if below_zero_level or not topic_name in self.subs.keys():
            return
        object_name = topic_name.removesuffix('/true_odom').removeprefix('/')
        result = String()
        result.data = object_name
        self.report_pub.publish(result)

        award_line = 'POINT AWARDED FOR ' + object_name
        self.get_logger().info(f'### {award_line} ###')
        self.destroy_subscription(self.subs[topic_name])
        del self.subs[topic_name]

def main():
    rclpy.init()
    node = PickupRefereeNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
