import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Header
from bitbots_msgs.msg import JointCommand

class GripperNode(Node):
    def __init__(self):
        super().__init__('gripper_node')
        self.state_sub = self.create_subscription(
            Bool,
            '/piper/gripper_state',
            callback=self.state_cb,
            qos_profile=10
        )
        self.gripper_pub = self.create_publisher(
            JointCommand,
            '/piper/DynamixelController_parallel/command',
            10
        )

    def state_cb(self, msg:Bool):
        result = JointCommand(
            header=Header(
                stamp=self.get_clock().now().to_msg(),
            ),
        )
        result.joint_names = ['piper/gripper']

        if msg.data:
            result.positions = [0.035]
        else:
            result.positions = [0.0]

        self.gripper_pub.publish(result)

def main():
    rclpy.init()
    node = GripperNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
