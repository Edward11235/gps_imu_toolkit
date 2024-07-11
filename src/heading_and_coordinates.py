#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Imu, NavSatFix
from std_msgs.msg import Float32MultiArray
from tf.transformations import euler_from_quaternion
import geodesy.utm

IMU_TOPIC = '/imu/data'
GPS_TOPIC = '/gps/fix'
STATE_TOPIC = '/state'

class HeadingAndCoordinates:
    def __init__(self):
        rospy.init_node('heading_and_coordinates', anonymous=True)
        
        self.initial_utm = None

        rospy.Subscriber(IMU_TOPIC, Imu, self.imu_callback)
        rospy.Subscriber(GPS_TOPIC, NavSatFix, self.gps_callback)

        self.state_pub = rospy.Publisher(STATE_TOPIC, Float32MultiArray, queue_size=10)
        
        self.heading = None
        self.x = None
        self.y = None

    def imu_callback(self, data):
        orientation_q = data.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, yaw) = euler_from_quaternion(orientation_list)
        self.heading = yaw  # Yaw is the heading in radians

    def gps_callback(self, data):
        current_utm = geodesy.utm.fromLatLong(data.latitude, data.longitude).toPoint()
        if self.initial_utm is None:
            self.initial_utm = current_utm

        self.x = current_utm.x - self.initial_utm.x
        self.y = current_utm.y - self.initial_utm.y

        rospy.loginfo("Coordinates (meters): x: {:.2f}, y: {:.2f}".format(self.x, self.y))
        self.publish_state()

    def publish_state(self):
        if self.heading is not None and self.x is not None and self.y is not None:
            state = Float32MultiArray()
            state.data = [self.x, self.y, self.heading]
            self.state_pub.publish(state)

    def run(self):
        rate = rospy.Rate(10)  # 10 Hz
        while not rospy.is_shutdown():
            if self.heading is not None:
                rospy.loginfo("Heading: {:.2f} radians".format(self.heading))
            rate.sleep()

if __name__ == '__main__':
    try:
        hc = HeadingAndCoordinates()
        hc.run()
    except rospy.ROSInterruptException:
        pass
