import nxt
import nxt.usbsock
import nxt.locator
from nxt.motor import *

nxt.locator.make_config()

def spin_around(b):
    m_left = Motor(b, PORT_B)
    m_left.turn(100, 360)
    m_right = Motor(b, PORT_C)
    m_right.turn(-100, 360)

b = nxt.locator.find_one_brick(debug=True)
#spin_around(b)
#"Dan's NX", '00:16:53:11:58:AB', 0, 82516