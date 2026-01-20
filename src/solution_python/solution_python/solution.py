import time
import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from std_msgs.msg import Header
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose
from bitbots_msgs.msg import JointCommand

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

        self.wait_pose = Pose()
        self.wait_pose.position.x = 0.55
        self.wait_pose.position.y = 0.
        self.wait_pose.position.z = 0.2
        self.ik_pub.publish(self.wait_pose)

        self.gripper_pub = self.create_publisher(
            JointCommand,
            '/piper/DynamixelController_parallel/command',
            10
        )

    def return_to_wait(self):
        self.ik_pub.publish(self.wait_pose)
        self.open_gripper()

    def open_gripper(self):
        msg = JointCommand(
            header=Header(
                stamp=self.get_clock().now().to_msg(),
            ),
        )
        msg.joint_names = ['piper/gripper']
        msg.positions = [0.035]
        self.gripper_pub.publish(msg)

    def close_gripper(self):
        msg = JointCommand(
            header=Header(
                stamp=self.get_clock().now().to_msg(),
            ),
        )
        msg.joint_names = ['piper/gripper']
        msg.positions = [0.]
        self.gripper_pub.publish(msg)

    def pickup(self, position_2d):
        result = Pose()
        print('PICKING UP')

        # move to target item
        result.position.x = float(position_2d[1] - MANIP_POS[1]) - 0.25
        result.position.y = position_2d[0] + 0.002
        result.position.z = 0.07
        self.open_gripper()
        self.ik_pub.publish(result)
        time.sleep(0.5)

        # grab target item
        self.close_gripper()
        time.sleep(0.15)

        # raise the item
        result.position.z += 0.2
        self.ik_pub.publish(result)
        time.sleep(1)

        # move to throw the item away
        print('THROWING AWAY')
        result.orientation.z = 1.
        result.position.y = result.position.x
        result.position.x = 0.
        result.position.z += 0.1
        self.ik_pub.publish(result)
        time.sleep(1)

        # drow item
        self.open_gripper()
        time.sleep(0.5)

        # move home
        self.return_to_wait()
        time.sleep(0.1)

    def image_callback(self, msg:Image):
        image = image_msg_to_numpy(msg)
        image = self.crop_image(image)
        centers = self.get_centers(image)
        if centers is None:
            self.return_to_wait()
            return
        centers = centers[centers[:, 0] < 0.05]
        centers = centers[centers[:, 0] > -0.05]
        # for center in centers:
        #     cv2.circle(
        #             image, 
        #             center=self.m_to_px(center),
        #             radius=10, 
        #             color=(0,0,255), 
        #             thickness=-1
        #     )
            # print(center)
        # cv2.imshow('huh', image)
        # cv2.waitKey(1)
        if len(centers) != 1:
            self.return_to_wait()
            return
        center = centers[0]
        self.pickup(center)
        # result = Pose()
        # print('PICKING UP')
        # result.position.x = float(center[1] - MANIP_POS[1]) - 0.25
        # result.position.y = center[0] + 0.002
        # result.position.z = 0.1
        # self.open_gripper()
        # self.ik_pub.publish(result)
        # time.sleep(0.5)
        # self.close_gripper()
        # time.sleep(0.15)
        # result.position.z += 0.2
        # self.ik_pub.publish(result)
        # time.sleep(1)
        # result.position.y = result.position.x
        # result.position.x = 0.
        # result.position.z += 0.1
        # self.ik_pub.publish(result)
        # time.sleep(1)
        # self.open_gripper()
        # time.sleep(0.05)
        # self.return_to_wait()
        


    def crop_image(self, image:np.ndarray):
        return image[CONV_TOP:CONV_BOT]

    def get_mask(self, image:np.ndarray):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        SAT_THRESH = 25
        mask = (hsv[:, :, 1] > SAT_THRESH).astype(np.uint8) * 255
        return mask

    def find_large_cc_centers(
            self,
            mask:np.ndarray,
            min_area:float=100.0,
            connectivity: int=8
        ) -> list[tuple[int, int]]:
        if mask.ndim != 2:
            raise ValueError("Mask must be a 2D array.")
        
        mask = mask.astype(np.uint8)
        
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=connectivity
        )
        centers = []
        for label in range(1, num_labels):  # Skip background (label 0)
            area = stats[label, cv2.CC_STAT_AREA]
            if area > min_area:
                cx, cy = centroids[label]
                centers.append((int(cx), int(cy)))
        
        return centers

    def px_to_m(self, point_px):
        point_m = np.array(point_px, float)
        point_m -= CONV_CENTER
        point_m *= METERS_PER_PX
        point_m *= -1
        return point_m

    def m_to_px(self, point_m):
        point_px = np.array(point_m, float)
        point_px *= -1
        point_px /= METERS_PER_PX
        point_px += CONV_CENTER
        return point_px.astype(int)
        
    def get_centers(self, image:np.ndarray):
        image = self.get_mask(image)
        centers = self.find_large_cc_centers(mask=image)
        if len(centers) == 0:
            return None
        centers = self.px_to_m(centers)
        
        return centers


def main():
    rclpy.init()
    node = Manip()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
