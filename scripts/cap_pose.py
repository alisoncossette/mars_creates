#!/usr/bin/env python3
"""Capture the arm's current end-effector pose via the Innate ManipulationInterface and save it.
Run on the robot with ROS sourced:  python3 /tmp/cap_pose.py
"""
import json
import logging
import sys
import time

sys.path.insert(0, "/home/jetson1/mars_lib")

import rclpy
from brain_client.manipulation_interface import ManipulationInterface

OUT = "/home/jetson1/mars_lib/selfie_pose.json"


def main():
    rclpy.init()
    node = rclpy.create_node("cap_pose")
    mi = ManipulationInterface(node, logging.getLogger("cap"))
    time.sleep(1.0)

    pose = mi.get_current_end_effector_pose()
    rpy = mi.get_current_orientation_rpy()
    print("POSE:", json.dumps(pose, default=str))
    print("RPY:", json.dumps(rpy, default=str))

    if pose:
        with open(OUT, "w") as f:
            json.dump({"pose": pose, "rpy": rpy}, f, default=str, indent=2)
        print("SAVED", OUT)
    else:
        print("POSE_IS_NONE")

    node.destroy_node()
    rclpy.shutdown()


main()
