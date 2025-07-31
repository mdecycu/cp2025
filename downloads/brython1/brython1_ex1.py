import brython_robot as robot
                         
w = robot.World(10, 10)    # 建立 10x10 的世界
w.robot(1, 1)        # 在 (1,1) 放置一台 robot

r = robot.AnimatedRobot(w, 1, 1)
r.move(9)  # robot 動畫式向右走 5 步，途中留下 trace 線
r.turn_left()
r.move(9)
r.turn_left()
r.move(9)
r.turn_left()
r.move(9)