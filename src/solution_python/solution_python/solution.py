import time
import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from std_msgs.msg import Header, Bool
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose
from bitbots_msgs.msg import JointCommand
from scipy.spatial.transform import Rotation, rotation
from copy import copy, deepcopy

def image_msg_to_numpy(msg):
    if msg.encoding == 'rgb8' or msg.encoding == 'bgr8':
        # 3 channels, uint8
        dtype = np.uint8
        channels = 3
    elif msg.encoding == 'mono8':
        # 1 channel, uint8
        dtype = np.uint8
        channels = 1
    elif msg.encoding == 'mono16':
        # 1 channel, uint16
        dtype = np.uint16
        channels = 1
    else:
        raise NotImplementedError(f"Encoding {msg.encoding} not supported without cv_bridge.")

    # Convert bytes to 1D NumPy array
    img_np = np.frombuffer(msg.data, dtype=dtype)

    # Reshape to (height, width, channels)
    if channels == 1:
        img_np = img_np.reshape((msg.height, msg.width))
    else:
        img_np = img_np.reshape((msg.height, msg.width, channels))

    return img_np

# y=230 start
# y=850 end
# conveyor width is 0.5 m
CONV_TOP = 230
CONV_BOT = 850
CONV_WIDTH = 0.5
CONV_CENTER = np.array([1920/2, (CONV_BOT - CONV_TOP) / 2], float)
METERS_PER_PX = CONV_WIDTH/(CONV_BOT - CONV_TOP)
MANIP_POS = np.array([0, -0.8, -0.05])

class Manip(Node):
    def __init__(self):
        super().__init__('solution')

        self.image_listener = self.create_subscription(
            Image,
            '/conveyor/conveyor_camera/raw',
            self.image_callback,
            1
        )

        self.ik_pub = self.create_publisher(
            Pose,
            '/piper/ik_target',
            10
        )

        self.gripper_pub = self.create_publisher(
            Bool,
            '/piper/gripper_state',
            10
        )

        self.get_logger().info('SUBSCRITPTIONS AND PUBLISHERS CREATED')
        self.create_poses()
        self.return_to_wait()
        time.sleep(1)
        self.pickup()
        time.sleep(5)
    def create_poses(self):
        self.default_rot = Rotation.from_euler('zyx', [np.pi/2, 0, np.pi/2])
        additional_rotation = Rotation.from_euler('zyx', [-np.pi/6, 0, 0])
        self.home_rot = self.default_rot * additional_rotation
        home_quat = self.home_rot.as_quat()

        # idle pose
        self.wait_pose = Pose()
        self.wait_pose.position.x = 0.55
        self.wait_pose.position.y = 0.
        self.wait_pose.position.z = 0.3
        self.wait_pose.orientation.x = copy(home_quat[0])
        self.wait_pose.orientation.y = copy(home_quat[1])
        self.wait_pose.orientation.z = copy(home_quat[2])
        self.wait_pose.orientation.w = copy(home_quat[3])

    def return_to_wait(self):
        self.ik_pub.publish(self.wait_pose)
        self.open_gripper()

    def open_gripper(self):
        msg = Bool()
        msg.data = True
        self.gripper_pub.publish(msg)

    def close_gripper(self):
        msg = Bool()
        msg.data = False
        self.gripper_pub.publish(msg)

    def pickup(self):
        result = Pose()
        # self.get_logger().info('PICKING UP')

        # move to target item
        self.open_gripper()
        result.position.x = 0.7
        result.position.y = 0.2
        result.position.z = 0.1
        result.orientation = deepcopy(self.wait_pose.orientation)
        self.ik_pub.publish(result)
        time.sleep(2)

        # move home
        self.return_to_wait()
        time.sleep(0.1)

    def image_callback(self, msg:Image):
        pass

def main():
    rclpy.init()
    node = Manip()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
