import numpy as np
import time
import rclpy
from rclpy.node import Node
from bitbots_msgs.msg import JointCommand, IntCommand
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import Header
import os
import pinocchio as pin
import pink
from numpy.linalg import solve, norm
from scipy.spatial.transform import Rotation
import qpsolvers

import meshcat_shapes
# from pink.visualization import start_meshcat_visualizer

# TODO: make device selection better
TORCH_DEVICE = 'cpu'

def point2list(p:Point):
    return [p.x, p.y, p.z]

def quat2list_scalar_last(q:Quaternion):
    return [q.x, q.y, q.z, q.w]

# FIXME make path a part of some config
PATH_TO_PIPER = '/root/workspace/src/manip_controller/manip_controller/robot_descriptions/mjcf/agilex-piper/piper.xml'

class IKNode(Node):
    def __init__(self, path_to_mjcf=PATH_TO_PIPER) -> None:
        super().__init__('IKNode')
        self.robot_name = 'piper'
        self.path_to_mjcf = os.path.abspath(path_to_mjcf)
        self.__create_ik()
        # self.viz = start_meshcat_visualizer(self.robot_wrapper)

        joint_control_topic = self.robot_name + "/DynamixelController_parallel/command"
        self.joint_control_publisher = self.create_publisher(
            JointCommand,
            joint_control_topic,
            10
        )

        ik_target_topic = f'{self.robot_name}/ik_target'
        self.ik_target_subscription = self.create_subscription(
            Pose,
            ik_target_topic,
            self.ik_target_cb,
            10
        )

        print('####################### IK NODE READY ########################')

    def __load_model(self):
        self.robot_wrapper = pin.RobotWrapper.BuildFromMJCF(self.path_to_mjcf)
        # just aliases
        self.robot_model = self.robot_wrapper.model
        self.robot_data = self.robot_wrapper.data

        self.joint_names = list(self.robot_model.names)
        # TODO: make it prettier
        self.joint_names = self.joint_names[1:] # remove 'universe' joint
        self.joint_names = self.joint_names[:-1] # remove gripper joint
        for i, name in enumerate(self.joint_names):
            self.joint_names[i] = self.robot_name + '/' + name
            # FIXME this is ugly as fuck. i don't know how to read actuator names using pinocchio
            self.joint_names[i] = self.joint_names[i].removesuffix('_joint')
        
    def __create_ik(self):
        self.__load_model()
        q0 = pin.neutral(self.robot_model)
        ee_name = 'end_effector'
        self.ik_configuration = pink.Configuration(
            model=self.robot_model, 
            data=self.robot_data,
            q=q0
        )
        if not self.robot_model.existFrame(ee_name):
            print(f'ERROR: model must have frame "{ee_name}"')
            raise ValueError(f'model must have frame "{ee_name}", but it was not found in {self.path_to_mjcf}')
        
        self.ee_task = pink.FrameTask(
            frame=ee_name,
            position_cost=10.,
            orientation_cost=1.
        )
        self.posture_task = pink.PostureTask(1e-3)
        self.tasks:list[pink.Task] = [self.ee_task, self.posture_task]

        for task in self.tasks:
            task.set_target_from_configuration(self.ik_configuration)

        self.solver = qpsolvers.available_solvers[0]
        if "osqp" in qpsolvers.available_solvers:
            self.solver = "osqp"
            
    def ik_target_cb(self, msg:Pose):
        target_pos = msg.position
        target_quat = msg.orientation
        # Update task targets
        ee_target = self.ee_task.transform_target_to_world

        ee_target.translation[0] = target_pos.x
        ee_target.translation[1] = target_pos.y
        ee_target.translation[2] = target_pos.z
        

        # Update visualization frames
        # viewer["end_effector_target"].set_transform(end_effector_target.np)
        # viewer["end_effector"].set_transform(
        #     configuration.get_transform_frame_to_world(
        #         end_effector_task.frame
        #     ).np
        # )

        # Compute velocity and integrate it into next configuration
        dt = 0.005
        try:
            velocity = pink.solve_ik(
                self.ik_configuration, 
                self.tasks, 
                dt, 
                solver=self.solver
            )
        except pink.exceptions.NotWithinConfigurationLimits as e:
            print('err')
            return
        self.ik_configuration.integrate_inplace(velocity, dt)
        q = self.ik_configuration.q
        # self.viz.display(q)
        # TODO make it prettier
        q = q[:-1] # remove gripper joint
        q = q.astype(float).tolist()

        return_msg = JointCommand(
            header=Header(
                stamp=self.get_clock().now().to_msg(),
            ),
        )
        print(self.joint_names)
        return_msg.joint_names = self.joint_names
        return_msg.positions = q
        print('publishing')
        self.joint_control_publisher.publish(return_msg)
        # time.sleep(0.001)

def main(args=None):
    rclpy.init(args=args)
    ik_node = IKNode()
    try:
        rclpy.spin(ik_node)
    except KeyboardInterrupt as e:
        print('Keyboard interrupt caught')
    ik_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
