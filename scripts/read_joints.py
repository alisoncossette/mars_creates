#!/usr/bin/env python3
"""Read the arm's current joint positions (radians) off ROS, best-effort QoS.
Run on the robot with ROS sourced:  python3 /tmp/read_joints.py
"""
import time

import rclpy
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState

TOPICS = ["/mars/arm/state", "/joint_states"]


def read_one(topic, secs=6.0):
    node = rclpy.create_node("read_joints_" + topic.strip("/").replace("/", "_"))
    box = {"m": None}
    qos = QoSProfile(
        depth=10,
        reliability=ReliabilityPolicy.BEST_EFFORT,
        durability=DurabilityPolicy.VOLATILE,
        history=HistoryPolicy.KEEP_LAST,
    )
    node.create_subscription(JointState, topic, lambda m: box.__setitem__("m", m), qos)
    end = time.time() + secs
    while rclpy.ok() and box["m"] is None and time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    return box["m"]


def main():
    rclpy.init()
    for t in TOPICS:
        m = read_one(t)
        if m and len(m.position):
            print("TOPIC", t)
            print("NAMES", list(m.name))
            print("POS", [round(float(p), 4) for p in m.position])
            rclpy.shutdown()
            return
    print("NO_DATA: no JointState on", TOPICS)
    rclpy.shutdown()


main()
