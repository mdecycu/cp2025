from browser import document, html, timer

CELL_SIZE = 40
WALL_THICKNESS = 6
IMG_PATH = "https://mde.tw/cp2025/reeborg/src/images/"

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = self._create_layers()
        self._init_html()
        self._draw_grid()
        self._draw_walls()
    def _create_layers(self):
        return {
            "grid": html.CANVAS(width=self.width * CELL_SIZE, height=self.height * CELL_SIZE),
            "walls": html.CANVAS(width=self.width * CELL_SIZE, height=self.height * CELL_SIZE),
            "objects": html.CANVAS(width=self.width * CELL_SIZE, height=self.height * CELL_SIZE),
            "robots": html.CANVAS(width=self.width * CELL_SIZE, height=self.height * CELL_SIZE),
        }

    def _init_html(self):
        container = html.DIV(style={
            "position": "relative",
            "width": f"{self.width * CELL_SIZE}px",
            "height": f"{self.height * CELL_SIZE}px"
        })
        for z, canvas in enumerate(self.layers.values()):
            canvas.style = {
                "position": "absolute",
                "top": "0px",
                "left": "0px",
                "zIndex": str(z)
            }
            container <= canvas
        document["brython_div1"].clear()
        document["brython_div1"] <= container
    def _draw_grid(self):
        ctx = self.layers["grid"].getContext("2d")
        ctx.strokeStyle = "#cccccc"
        for i in range(self.width + 1):
            ctx.beginPath()
            ctx.moveTo(i * CELL_SIZE, 0)
            ctx.lineTo(i * CELL_SIZE, self.height * CELL_SIZE)
            ctx.stroke()
        for j in range(self.height + 1):
            ctx.beginPath()
            ctx.moveTo(0, j * CELL_SIZE)
            ctx.lineTo(self.width * CELL_SIZE, j * CELL_SIZE)
            ctx.stroke()

    def _draw_image(self, ctx, src, x, y, w, h, offset_x=0, offset_y=0):
        img = html.IMG()
        img.src = src
        def onload(evt):
            px = x * CELL_SIZE + offset_x
            py = (self.height - 1 - y) * CELL_SIZE + offset_y
            ctx.drawImage(img, px, py, w, h)
        img.bind("load", onload)
    def _draw_walls(self):
        ctx = self.layers["walls"].getContext("2d")
        for x in range(self.width):
            # 北牆：最上方（貼在頂格子正上緣）
            self._draw_image(ctx, IMG_PATH + "north.png", x, self.height - 1,
                             CELL_SIZE, WALL_THICKNESS, offset_y=0)
            # 南牆：最下方（貼在底格子正下緣）
            self._draw_image(ctx, IMG_PATH + "north.png", x, 0,
                             CELL_SIZE, WALL_THICKNESS, offset_y=CELL_SIZE - WALL_THICKNESS)
        for y in range(self.height):
            # 西牆：最左邊（貼格子內側左緣）
            self._draw_image(ctx, IMG_PATH + "east.png", 0, y,
                             WALL_THICKNESS, CELL_SIZE, offset_x=0)
            # 東牆：最右邊（貼格子內側右緣）
            self._draw_image(ctx, IMG_PATH + "east.png", self.width - 1, y,
                             WALL_THICKNESS, CELL_SIZE, offset_x=CELL_SIZE - WALL_THICKNESS)

    def robot(self, x, y):
        ctx = self.layers["robots"].getContext("2d")
        self._draw_image(ctx, IMG_PATH + "blue_robot_e.png", x - 1, y - 1,
                         CELL_SIZE, CELL_SIZE)

class AnimatedRobot:
    def __init__(self, world, x, y):
        self.world = world
        self.x = x - 1  # convert to 0-indexed
        self.y = y - 1
        self.facing = "E"
        self.robot_ctx = world.layers["robots"].getContext("2d")
        self.trace_ctx = world.layers["objects"].getContext("2d")
        self._draw_robot()

    def _draw_robot(self):
        self.robot_ctx.clearRect(0, 0, self.world.width * CELL_SIZE, self.world.height * CELL_SIZE)
        self.world._draw_image(self.robot_ctx, IMG_PATH + "blue_robot_e.png",
                               self.x, self.y, CELL_SIZE, CELL_SIZE)

    def _draw_trace(self, from_x, from_y, to_x, to_y):
        ctx = self.trace_ctx
        ctx.strokeStyle = "#d33"
        ctx.lineWidth = 2
        ctx.beginPath()
        fx = from_x * CELL_SIZE + CELL_SIZE / 2
        fy = (self.world.height - 1 - from_y) * CELL_SIZE + CELL_SIZE / 2
        tx = to_x * CELL_SIZE + CELL_SIZE / 2
        ty = (self.world.height - 1 - to_y) * CELL_SIZE + CELL_SIZE / 2
        ctx.moveTo(fx, fy)
        ctx.lineTo(tx, ty)
        ctx.stroke()

    def move(self, steps):
        def step():
            nonlocal steps
            if steps == 0:
                return
            from_x, from_y = self.x, self.y
            if self.facing == "E":
                self.x += 1
            elif self.facing == "W":
                self.x -= 1
            elif self.facing == "N":
                self.y += 1
            elif self.facing == "S":
                self.y -= 1
            self._draw_trace(from_x, from_y, self.x, self.y)
            self._draw_robot()
            steps -= 1
            timer.set_timeout(step, 200)  # 200ms per step
        step()

                         
w = World(10, 10)    # 建立 10x10 的世界
w.robot(1, 1)        # 在 (1,1) 放置一台 robot

r = AnimatedRobot(w, 1, 1)
r.move(5)  # robot 動畫式向右走 5 步，途中留下 trace 線
