import rospy
import csv
from time import sleep
from geometry_msgs.msg import PoseStamped
import numpy as np
def coords(s):
    ncols = 20
    return (s % ncols - 9.45 , -s / ncols + 6.5)

def talker():
    pub = rospy.Publisher('/bot_1/command/pose', PoseStamped, queue_size=10)
    pub_2 = rospy.Publisher('/bot_2/command/pose', PoseStamped, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(18) # 10hz
    
    interp = 28

    with open("statehistory15x20.csv") as f:
        data = csv.reader(f)
        bot_1_coords_x = []
        bot_2_coords_x = []
        bot_1_coords_y = []
        bot_2_coords_y = []
        for row in data:
            print row[1]
            print coords(float(row[1]))[0]
            bot_1_coords_x.append(coords(float(row[1]))[0])
            bot_1_coords_y.append(coords(float(row[1]))[1])
            bot_2_coords_x.append(coords(float(row[2]))[0])
            bot_2_coords_y.append(coords(float(row[2]))[1])

        bot_1_coords_x_fine = []
        bot_1_coords_y_fine = []
        bot_2_coords_x_fine = []
        bot_2_coords_y_fine = []
        for ind in range(len(bot_1_coords_x)-1):
            for fine_coords in np.linspace(bot_1_coords_x[ind],bot_1_coords_x[ind+1],interp):
                bot_1_coords_x_fine.append(fine_coords)
            for fine_coords in np.linspace(bot_1_coords_y[ind],bot_1_coords_y[ind+1],interp):
                bot_1_coords_y_fine.append(fine_coords)
            for fine_coords in np.linspace(bot_2_coords_x[ind],bot_2_coords_x[ind+1],interp):
                bot_2_coords_x_fine.append(fine_coords)
            for fine_coords in np.linspace(bot_2_coords_y[ind],bot_2_coords_y[ind+1],interp):
                bot_2_coords_y_fine.append(fine_coords)


        for ind in range(len(bot_1_coords_x_fine)):
            coordiantes_bot_1 = PoseStamped()
            coordinates_bot_2 = PoseStamped()
            coordiantes_bot_1.pose.position.x = bot_1_coords_x_fine[ind]
            coordiantes_bot_1.pose.position.y = bot_1_coords_y_fine[ind]
            coordiantes_bot_1.pose.position.z = 1.5
            coordinates_bot_2.pose.position.x = bot_2_coords_x_fine[ind]
            coordinates_bot_2.pose.position.y = bot_2_coords_y_fine[ind]
            coordinates_bot_2.pose.position.z = 1.5
            rospy.loginfo(coordiantes_bot_1)
            rospy.loginfo(coordinates_bot_2)
            pub.publish(coordiantes_bot_1)
            pub_2.publish(coordinates_bot_2)
            rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
        
