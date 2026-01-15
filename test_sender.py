import time
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose

INIT_TIME = time.time()

class TestSender(Node):
    def __init__(self):
        super().__init__('TestSender')
        self.ik_pub = self.create_publisher(
            msg_type=Pose,
            topic='/piper/ik_target',
            qos_profile=10
        )

    def send(self):
        msg = Pose()
        msg.orientation.w =  1.
        msg.orientation.x =  0.
        msg.orientation.y =  0.
        msg.orientation.z =  0.

        msg.position.x = 0.5 + 0.1 * np.cos(time.time() - INIT_TIME)
        msg.position.y = 0.0 + 0.1 * np.sin(time.time() - INIT_TIME)
        msg.position.z = 0.2152
        self.ik_pub.publish(msg)
        
def main():
    rclpy.init()
    node = TestSender()
    t0 = time.time()
    while True:
        node.send()
        time.sleep(0.001)
        

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
