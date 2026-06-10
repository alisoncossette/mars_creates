#!/usr/bin/env python3
"""Read the arm's current joint positions (radians) off ROS, trying several QoS profiles.
Run on the robot with ROS sourced:  python3 /tmp/read_joints.py
"""
import time

import rclpy
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState

TOPICS = ["/mars/arm/state", "/joint_states"]
COMBOS = [
    (ReliabilityPolicy.BEST_EFFORT, DurabilityPolicy.TRANSIENT_LOCAL),
    (ReliabilityPolicy.RELIABLE, DurabilityPolicy.TRANSIENT_LOCAL),
    (ReliabilityPolicy.BEST_EFFORT, DurabilityPolicy.VOLATILE),
    (ReliabilityPolicy.RELIABLE, DurabilityPolicy.VOLATILE),
]


def try_read(topic, rel, dur, secs=3.0):
    node = rclpy.create_node("rj")
    box = {"m": None}
    qos = QoSProfile(depth=10, reliability=rel, durability=dur, history=HistoryPolicy.KEEP_LAST)
    node.create_subscription(JointState, topic, lambda m: box.__setitem__("m", m), qos)
    end = time.time() + secs
    while rclpy.ok() and box["m"] is None and time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    return box["m"]


def main():
    rclpy.init()
    for t in TOPICS:
        for rel, dur in COMBOS:
            m = try_read(t, rel, dur)
            if m and len(m.position):
                print("TOPIC", t, "| REL", rel.name, "| DUR", dur.name)
                print("NAMES", list(m.name))
                print("POS", [round(float(p), 4) for p in m.position])
                rclpy.shutdown()
                return
    print("NO_DATA")
    rclpy.shutdown()


main()
