#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32
import tf

def imu_callback(data):
    quaternion = (
        data.orientation.x,
        data.orientation.y,
        data.orientation.z,
        data.orientation.w
    )
    yaw = tf.transformations.euler_from_quaternion(quaternion)[2]
    pub.publish(yaw)

rospy.init_node('simple_imu_to_yaw')
pub = rospy.Publisher('yaw_angle', Float32, queue_size=10)
rospy.Subscriber('/imu/data', Imu, imu_callback)
rospy.spin()
