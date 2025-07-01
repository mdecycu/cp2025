from browser import document, html

GRID_SIZE = 10
CELL_SIZE = 40
IMG_PATH = "IMG_PATH = "https://mde.tw/cp2025/reeborg/src/images/"
"

# 建立圖層：格線、牆面、物件、機器人
layers = {
    "grid": html.CANVAS(width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE),
    "walls": html.CANVAS(width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE),
    "objects": html.CANVAS(width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE),
    "robot": html.CANVAS(width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE),
}

# 圖層加入 container
container = html.DIV(style={"position": "relative", "width": f"{GRID_SIZE * CELL_SIZE}px", "height": f"{GRID_SIZE * CELL_SIZE}px"})
for z, canvas in enumerate(layers.values()):
    canvas.style = {"position": "absolute", "top": "0px", "left": "0px", "zIndex": str(z)}
    container <= canvas
document["brython_div1"] <= container

# 圖片繪製函式
def draw_image(ctx, img_path, x, y, width, height, offset_x=0, offset_y=0):
    img = html.IMG()
    img.src = img_path
    def onload(evt):
        px = x * CELL_SIZE + offset_x
        py = (GRID_SIZE - 1 - y) * CELL_SIZE + offset_y
        ctx.drawImage(img, px, py, width, height)
    img.bind("load", onload)

# 畫格線
def draw_grid():
    ctx = layers["grid"].getContext("2d")
    ctx.strokeStyle = "#cccccc"
    for i in range(GRID_SIZE + 1):
        ctx.beginPath()
        ctx.moveTo(i * CELL_SIZE, 0)
        ctx.lineTo(i * CELL_SIZE, GRID_SIZE * CELL_SIZE)
        ctx.stroke()
        ctx.beginPath()
        ctx.moveTo(0, i * CELL_SIZE)
        ctx.lineTo(GRID_SIZE * CELL_SIZE, i * CELL_SIZE)
        ctx.stroke()

def draw_border_walls():
    ctx = layers["walls"].getContext("2d")
    wall_thickness = 6  # 像素厚度

    # 北牆：畫在最頂的 y = GRID_SIZE - 1，再往下一點讓它可見
    for x in range(GRID_SIZE):
        draw_image(ctx, IMG_PATH + "north.png", x, GRID_SIZE - 1,
                   width=CELL_SIZE, height=wall_thickness, offset_y=0)

    # 南牆：畫在 y = 0 的下邊界
    for x in range(GRID_SIZE):
        draw_image(ctx, IMG_PATH + "north.png", x, 0,
                   width=CELL_SIZE, height=wall_thickness, offset_y=CELL_SIZE - wall_thickness)

    # 東牆：畫在最右邊 x = GRID_SIZE - 1 的右側
    for y in range(GRID_SIZE):
        draw_image(ctx, IMG_PATH + "east.png", GRID_SIZE - 1, y,
                   width=wall_thickness, height=CELL_SIZE, offset_x=CELL_SIZE - wall_thickness)

    # 西牆：畫在 x = 0 的內側邊緣，向右內縮一點
    for y in range(GRID_SIZE):
        draw_image(ctx, IMG_PATH + "east.png", 0, y,
                   width=wall_thickness, height=CELL_SIZE, offset_x=0)

# 畫機器人：貼在 (1,1) → 座標轉為 (0,0)
def draw_robot():
    ctx = layers["robot"].getContext("2d")
    draw_image(ctx, IMG_PATH + "blue_robot_e.png", 0, 0,
               width=CELL_SIZE, height=CELL_SIZE)

# 初始化畫面
draw_grid()
draw_border_walls()
draw_robot()