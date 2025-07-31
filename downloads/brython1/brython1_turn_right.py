# extended_robot.py
import brython_robot as robot

# 繼承 AnimatedRobot 並擴充 turn_right()
class MyRobot(robot.AnimatedRobot):
    def turn_right(self):
        def action(done):
            idx = self.facing_order.index(self.facing)
            self.facing = self.facing_order[(idx - 1) % 4]
            self._draw_robot()
            robot.timer.set_timeout(done, 300)
        self.queue.append(action)
        self._run_queue()

# 建立世界
w = robot.World(10, 10)
w.robot(1, 1)

# 使用擴充後的 MyRobot 類別
r = MyRobot(w, 1, 1)
r.move(5)       # 向右走 5 格（東）
r.turn_left()   # 左轉（北）
r.move(5)
r.turn_right()  # 右轉（東）
r.move(2)
r.turn_right()  # 右轉（南）
r.move(2)
r.turn_left()   # 左轉（東）
r.move(1)