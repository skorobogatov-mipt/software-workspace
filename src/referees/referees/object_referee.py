import rclpy
from rclpy.node import Node
import re
from nav_msgs.msg import Odometry
from abc import ABC, abstractmethod

DEFAULT_REGEXPS = [
    "\/cylinder_[a-z|A-Z]*_[a-z]*_rgb[0-9]{3}\/true_odom",
    "\/box_[a-z|A-Z]*_id[1-3]_rgb[0-9]{3}\/true_odom"
]

class ObjectReferee(Node, ABC):
    def __init__(
            self, name:str,
            taget_object_regexps:list[str]
            ):
        super().__init__(name)
        target_topics = self.get_target_topics(taget_object_regexps)
        self.subs = {}
        for topic in target_topics:
            self.get_logger().info('creating sub for:' + str(topic))
            self.subs[topic] = self.create_subscription(
                msg_type=Odometry,
                topic=topic,
                callback=self.create_callback(topic),
                qos_profile=10
            )
        self.get_logger().info('### TOPICS SUBSCRIBED ###')

    def get_target_topics(self, taget_object_regexps:list[str]):
        available_topics = self.get_topic_names_and_types()
        target_topics = []
        for name, msg_type in available_topics:
            for regexp in taget_object_regexps:
                if re.match(regexp, name) is not None:
                    target_topics.append(name)
        return target_topics

    @abstractmethod
    def process_odom_cb(self, topic_name:str, msg:Odometry):
        raise NotImplementedError

    def create_callback(self, topic_name):
        # override this method in a child class 
        # by filling odom_cb IN A CHILD CLASS
        def odom_cb(msg:Odometry):
            self.process_odom_cb(topic_name, msg)
        return odom_cb
        

        

