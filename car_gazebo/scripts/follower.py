#!/usr/bin/env python
# BEGIN ALL
import sys
import rospy, cv2, cv_bridge, numpy, roslib
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
roslib.load_manifest('follow_bot')

class Follower:
	def __init__(self):
		self.bridge = cv_bridge.CvBridge()
		cv2.namedWindow("window", 1)
		self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image, self.image_callback)
		self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
		self.twist = Twist()
	def image_callback(self, msg):
		image = self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		lower_yellow = numpy.array([ 10,  10,  10])
		upper_yellow = numpy.array([255, 255, 250])
		mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
		h, w, d = image.shape
		search_top = 3*h/4
		search_bot = 3*h/4 + 20
		mask[0:int(search_top), 0:w] = 0
		mask[int(search_bot):h, 0:w] = 0
		M = cv2.moments(mask)
		if M['m00'] > 0:
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
			cv2.circle(image, (cx, cy), 20, (0,0,255), -1)
			# BEGIN CONTROL
			err = cx - w/2
			self.twist.linear.x = 0.1
			self.twist.angular.z = -float(err) / 500
			self.cmd_vel_pub.publish(self.twist)
			# END CONTROL
		image = cv2.resize(image, (960, 540))
		cv2.imshow("window", image)
		cv2.waitKey(3)

def main(args):
	rospy.init_node('follower', anonymous=True)
	follower = Follower()
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print("Shutting down")
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main(sys.argv)
