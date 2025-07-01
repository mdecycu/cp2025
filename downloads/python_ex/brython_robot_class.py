from browser import document, html

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
            # 北牆（最上列的格子頂部）
            self._draw_image(ctx, IMG_PATH + "north.png", x, self.height - 1, CELL_SIZE, WALL_THICKNESS, offset_y=0)
            # 南牆（最下列的底部）
            self._draw_image(ctx, IMG_PATH + "north.png", x, 0, CELL_SIZE, WALL_THICKNESS, offset_y=CELL_SIZE - WALL_THICKNESS)
        for y in range(self.height):
            # 西牆（最左列格子的左邊）
            self._draw_image(ctx, IMG_PATH + "east.png", 0, y, WALL_THICKNESS, CELL_SIZE, offset_x=0)
            # 東牆（最右列格子的右邊）
            self._draw_image(ctx, IMG_PATH + "east.png", self.width - 1, y, WALL_THICKNESS, CELL_SIZE, offset_x=CELL_SIZE - WALL_THICKNESS)

    def robot(self, x, y):
        ctx = self.layers["robots"].getContext("2d")
        self._draw_image(ctx, IMG_PATH + "blue_robot_e.png", x - 1, y - 1, CELL_SIZE, CELL_SIZE)
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
            # 北牆：最頂格子的上邊緣
            self._draw_image(ctx, IMG_PATH + "north.png", x, self.height - 1,
                             CELL_SIZE, WALL_THICKNESS, offset_y=0)
            # 南牆：最底格子的下邊緣
            self._draw_image(ctx, IMG_PATH + "north.png", x, 0,
                             CELL_SIZE, WALL_THICKNESS, offset_y=CELL_SIZE - WALL_THICKNESS)

        for y in range(self.height):
            # 西牆：最左格子的左邊
            self._draw_image(ctx, IMG_PATH + "east.png", 0, y,
                             WALL_THICKNESS, CELL_SIZE, offset_x=0)
            # 東牆：最右格子的右邊
            self._draw_image(ctx, IMG_PATH + "east.png", self.width - 1, y,
                             WALL_THICKNESS, CELL_SIZE, offset_x=CELL_SIZE - WALL_THICKNESS)

    def robot(self, x, y):
        ctx = self.layers["robots"].getContext("2d")
        self._draw_image(ctx, IMG_PATH + "blue_robot_e.png", x - 1, y - 1,
                         CELL_SIZE, CELL_SIZE)
w = World(20, 20)     # 建立一個 10x6 的世界（寬10，高6）
w.robot(1, 1)        # 在 (1,1) 放一台 robot
w.robot(20, 4)        # 在 (5,4) 再放一台
