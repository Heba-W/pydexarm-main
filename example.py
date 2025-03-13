from pydexarm import Dexarm
import time

'''windows'''
dexarm = Dexarm(port="COM6")
'''mac & linux'''
# device = Dexarm(port="/dev/tty.usbmodem3086337A34381")

dexarm.go_home()

dexarm.move_to(50, 300, 0)
dexarm.move_to(50, 300, -65)
dexarm.air_picker_pick()
dexarm.move_to(50, 300, 0)
dexarm.move_to(-50, 300, 0)
dexarm.move_to(-50, 300, -65)
dexarm.air_picker_place()
dexarm.air_picker_stop()
time.sleep(2)

dexarm.go_home()


dexarm.close()