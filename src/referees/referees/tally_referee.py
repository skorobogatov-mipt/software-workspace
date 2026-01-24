import rclpy
from rclpy.node import Node
from std_msgs.msg import String

PICKUP_SCORE_CYL = 5
PICKUP_SCORE_BOX = 15

CONTAINER_SCORE_CYL = 10
CONTAINER_SCORE_BOX = 20

class TallyReferee(Node):
    def __init__(self):
        super().__init__('tally_referee')

        self.container_sub = self.create_subscription(
            String,
            '/referee/container',
            self.container_cb,
            10
        )
        self.pickup_sub = self.create_subscription(
            String,
            '/referee/pickup',
            self.pickup_cb,
            10
        )

        self.PICKUP_SCORE = 0
        self.CONTAINER_SCORE = 0

    def print_score(self):
        self.get_logger().info(
                f'TOTAL:\n PICKUP   : {self.PICKUP_SCORE}\n CONTAINER: {self.CONTAINER_SCORE}'
        )


    def pickup_cb(self, msg:String):
        obj = msg.data.lower()
        award_score = 0
        if 'cylinder' in obj:
            award_score = PICKUP_SCORE_CYL
        elif 'box' in obj:
            award_score = PICKUP_SCORE_BOX

        if award_score == 0:
            return
        self.PICKUP_SCORE += award_score
        self.get_logger().info(f'PICKUP: {award_score} POINTS FOR {obj}')
        self.print_score()


    def container_cb(self, msg:String):
        obj = msg.data.lower()
        award_score = 0
        if 'cylinder' in obj:
            award_score = CONTAINER_SCORE_CYL
        elif 'box' in obj:
            award_score = CONTAINER_SCORE_BOX

        if award_score == 0:
            return
        self.CONTAINER_SCORE += award_score
        self.get_logger().info(f'CONTAINER: {award_score} POINTS FOR {obj}')
        self.print_score()
        
def main():
    rclpy.init()
    node = TallyReferee()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

