# extended_robot.py
import brython_robot as robot
from browser import document, timer

# 擴充 AnimatedRobot，加入 turn_right() 和 backward()
class MyRobot(robot.AnimatedRobot):
    def turn_right(self):
        def action(done):
            idx = self.facing_order.index(self.facing)
            self.facing = self.facing_order[(idx - 1) % 4]
            self._draw_robot()
            timer.set_timeout(done, 300)
        self.queue.append(action)
        self._run_queue()

    def backward(self):
        def action(next_done):
            from_x, from_y = self.x, self.y
            dx, dy = 0, 0
            if self.facing == "E":
                dx = -1
            elif self.facing == "W":
                dx = 1
            elif self.facing == "N":
                dy = -1
            elif self.facing == "S":
                dy = 1
            next_x = self.x + dx
            next_y = self.y + dy

            if 0 <= next_x < self.world.width and 0 <= next_y < self.world.height:
                self.x, self.y = next_x, next_y
                self._draw_trace(from_x, from_y, self.x, self.y)
                self._draw_robot()
                timer.set_timeout(next_done, 200)
            else:
                print("🚨 已經撞牆，停止移動！")
                next_done()
        self.queue.append(action)
        self._run_queue()

# 建立世界與機器人
w = robot.World(10, 10)
w.robot(1, 1)
r = MyRobot(w, 1, 1)

# 鍵盤控制函式，改用 i, j, k, m
def handle_key(event):
    key = event.key.lower()
    if key == "i":
        r.move(1)
    elif key == "m":
        r.backward()
    elif key == "j":
        r.turn_left()
    elif key == "k":
        r.turn_right()

# 綁定鍵盤事件
document.bind("keydown", handle_key)
