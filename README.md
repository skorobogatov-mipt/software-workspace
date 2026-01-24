# Running the whole thing
To run the whole thing, type:
```
ros2 launch olympiad_env olympiad.launch.py
```
It will launch everything EXCEPT THE SOLUTION.

# `manip_controller`

To run this package, type
```
ros2 launch manip_controller manip_controller.launch.py
```
and it will launch the two nodes described below.

## `ik_node.py`
This node subscribes to a topic called `/piper/ik_target` with type `Pose`. After
receiving a message on this topic, it will move the manipulator's end-effector
to the target location. The origin is manipulator's base.

> There's a catch with rotation. The default rotatio for the manipulator's
> end-effector is not [0, 0, 0] in Euler's angles, it's [$\pi/2$, 0, $\pi/2$]
> in ZYX Euler's angles.

## `gripper_node.py`
This node subscribes to a topic `/piper/gripper_state` with msg_type being
`Bool`. If 'True' is received on this topic, this node opens manipulator's
griper. If `False` is received, it closes the gripper.

# `conveyor_controller'
This package is a single node written in `conveyor_controller.py`. It just
starts conveyor with a constant speed of 0.01 parrots.

To run it:
```
ros2 run conveyor_controller constant_speed
```

# `referees`

This package consists of three referees:
* `pickup_referee`
* `container_referee`
* `tally_referee`

To run them all:
```
ros2 launch referees referees.launch.py
```

## SELECTING OBJECTS
Both pickup_referee and container_referee require a list of regexps that will
match target objects' names. **THE REGEXP HAS TO MATCH ANY PART OF THE NAME**.

## `tally_referee.py`
This referee subscribes to two topics:
* `/refere/container`
* `/refere/pickup`

Both of them have msg_type of `String`. The messages that arrive on these topics are names of objects.

For now, it just accumulates score and prints updates.

### `/refere/pickup` 
If a message arrived on this topic, it means that object with a name from the
message was just picked up.

### `/refere/container` 
If a message arrived on this topic, it means that object with a name from the message has just fallen into the container.
## `pickup_referee.py`
This referee just checks if an object was raised above a certain level. If it
happened, it sends the name of this object to `/refere/pickup`.

## `container_referee.py`
This referee checks if any of the target objects are located in some range of
the container's center. If it is so, it sends the name of this object to
`/referee/container` and stops tracking it.

> [!IMPORTANT]
> If you want to move the container, change it's position in
> `container_referee.py`, otherwise it will not work.

# Solution
An example solution is located in `src/solution/solution/solution.py`
