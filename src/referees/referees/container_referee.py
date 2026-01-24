import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import numpy as np

from .object_referee import ObjectReferee, DEFAULT_REGEXPS

CONTAINER_POS_3D = np.array([-0.6, -0.5, 0.25])

# note that these are half dimensions
CONTAINER_DIMS = np.array([0.25, 0.25, 0.25])

class ContainerReferee(ObjectReferee):
    def __init__(self):
        super().__init__(
                'box_referee',
                taget_object_regexps=DEFAULT_REGEXPS
        )
        self.report_pub = self.create_publisher(
            String,
            '/referee/container',
            qos_profile=10
        )
        self.get_logger().info('### CONTAINER REFEREE READY ###')

    def process_odom_cb(self, topic_name: str, msg: Odometry):
        msg_pos = np.array([
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z
        ])
        diff = np.abs(CONTAINER_POS_3D - msg_pos)
        if (diff < CONTAINER_DIMS).all():
            object_name = topic_name.removesuffix('/true_odom').removeprefix('/')
            result = String()
            result.data = object_name
            self.report_pub.publish(result)

            award_msg = object_name + ' IS IN THE CONTAINER'
            self.get_logger().info(award_msg)
            self.destroy_subscription(self.subs[topic_name])
            del self.subs[topic_name]


        
def main():
    rclpy.init()
    node = ContainerReferee()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
