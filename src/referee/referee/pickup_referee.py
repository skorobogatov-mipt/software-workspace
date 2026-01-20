import re
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from functools import partial

TARGET_TOPIC_RE = [
    "\/cylinder_[a-z|A-Z]*_[a-z]*_rgb[0-9]{3}\/true_odom"
]

ZERO_LEVEL = 1.05
ZERO_LEVEL_EPS = 0.001

class PickupRefereeNode(Node):
    def __init__(self):
        super().__init__('referee_node')

        target_topics = self.get_target_topics()
        self.subs = {}
        for topic in target_topics:
            self.subs[topic] = self.create_subscription(
                msg_type=Odometry,
                topic=topic,
                callback=self.create_callback(topic),
                qos_profile=10
            )

        print('### REFEREE READY ###')
    
    def get_target_topics(self):
        available_topics = self.get_topic_names_and_types()
        target_topics = []
        for name, msg_type in available_topics:
            for regexp in TARGET_TOPIC_RE:
                if re.match(regexp, name) is not None:
                    target_topics.append(name)
        return target_topics

    def create_callback(self, topic_name):
        def odom_cb(msg:Odometry):
            if msg.pose.pose.position.z < ZERO_LEVEL + ZERO_LEVEL_EPS or not topic_name in self.subs.keys():
                return
            award_line = 'POINT AWARDED FOR ' + topic_name.removesuffix('/true_odom')
            print('#' * (len(award_line) + 8))
            print('###', award_line, '###')
            print('#' * (len(award_line) + 8))
            self.destroy_subscription(self.subs[topic_name])
            del self.subs[topic_name]
        return odom_cb

def main():
    rclpy.init()
    node = PickupRefereeNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
