import time
import rclpy
from rclpy.node import Node
from bitbots_msgs.msg import JointCommand
from std_msgs.msg import Header

class ConveyorController(Node):
    def __init__(self):
        super().__init__('conveyor_controller')

        self.speed_pub = self.create_publisher(
            JointCommand,
            '/conveyor/DynamixelController_parallel/command',
            10
        )

    def set_speed(self, new_speed):
        self.speed = new_speed
        return_msg = JointCommand(
            header=Header(
                stamp=self.get_clock().now().to_msg(),
            ),
        )
        return_msg.joint_names = ['conveyor/conveyor_motor']
        return_msg.positions = [self.speed]
        for _ in range(10):
            self.speed_pub.publish(return_msg)
            time.sleep(0.01)
        self.get_logger().info('SPEED SET FOR: ', new_speed)

def main():
    rclpy.init()
    cc = ConveyorController()
    cc.set_speed(0.01)
    rclpy.spin(cc)
    cc.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
