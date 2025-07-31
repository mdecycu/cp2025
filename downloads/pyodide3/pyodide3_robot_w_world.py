import js, asyncio
import json

CELL_SIZE = 40
WALL_THICKNESS = 6
IMG_PATH = "https://mde.tw/cp2025/reeborg/src/images/"

class World:
    _image_cache = {}
    _temp_canvas = None # 用於像素處理的臨時 Canvas
    _temp_ctx = None    # 用於像素處理的臨時 Context

    def __init__(self, width, height, walls=None, objects=None, robot_start=None):
        self.width = width
        self.height = height
        self.walls_data = walls or {}
        self.objects_data = objects or {}
        self.robot_start = robot_start or (1, 1)
        self.layers = self._create_layers()
        self._init_html()

        # 初始化臨時 Canvas，只創建一次
        if World._temp_canvas is None:
            World._temp_canvas = js.document.createElement("canvas")
            World._temp_ctx = World._temp_canvas.getContext("2d")


    def _create_layers(self):
        # 注意：Z-index 的順序很重要
        # grid (網格線) -> objects (背景草地 + 實際物件) -> walls (牆壁) -> numbers (數字) -> robots (機器人)
        return {
            "grid": js.document.createElement("canvas"),
            "objects": js.document.createElement("canvas"),
            "walls": js.document.createElement("canvas"),
            "numbers": js.document.createElement("canvas"), # 新增數字圖層
            "robots": js.document.createElement("canvas"),
        }

    def _init_html(self):
        container = js.document.createElement("div")
        container.style.position = "relative"
        container.style.width = f"{self.width * CELL_SIZE}px"
        container.style.height = f"{self.height * CELL_SIZE}px"

        layer_order = ["grid", "objects", "walls", "numbers", "robots"]
        for z, layer_name in enumerate(layer_order):
            canvas = self.layers[layer_name]
            canvas.width = self.width * CELL_SIZE
            canvas.height = self.height * CELL_SIZE
            canvas.style.position = "absolute"
            canvas.style.top = "0px"
            canvas.style.left = "0px"
            canvas.style.zIndex = str(z)
            container.appendChild(canvas)

        button_container = js.document.createElement("div")
        button_container.style.marginTop = "10px"
        button_container.style.textAlign = "center"

        move_button = js.document.createElement("button")
        move_button.innerHTML = "Move Forward"
        move_button.style.margin = "5px"
        move_button.style.padding = "10px 20px"
        move_button.style.fontSize = "16px"
        button_container.appendChild(move_button)

        turn_button = js.document.createElement("button")
        turn_button.innerHTML = "Turn Left"
        turn_button.style.margin = "5px"
        turn_button.style.padding = "10px 20px"
        turn_button.style.fontSize = "16px"
        button_container.appendChild(turn_button)

        brython_div = js.document.getElementById("brython_div1")
        if not brython_div:
            raise RuntimeError("🚨 'brython_div1' element not found in HTML!")
        brython_div.innerHTML = ""
        brython_div.appendChild(container)
        brython_div.appendChild(button_container)

        self.move_button = move_button
        self.turn_button = turn_button

    def _draw_grid(self):
        ctx = self.layers["grid"].getContext("2d")
        ctx.clearRect(0, 0, self.width * CELL_SIZE, self.height * CELL_SIZE)

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

    # 修改 _draw_image 函數以處理關鍵色透明
    def _draw_image(self, ctx, img_key, x, y, w, h, offset_x=0, offset_y=0, use_chroma_key=False, chroma_key_rgb=(255, 255, 255)):
        img = World._image_cache.get(img_key)
        if not (img and img.complete and img.naturalWidth > 0):
            return False

        px = x * CELL_SIZE + offset_x
        py = (self.height - 1 - y) * CELL_SIZE + offset_y

        if use_chroma_key:
            # 設置臨時 Canvas 的大小與圖片繪製區域相同
            World._temp_canvas.width = w
            World._temp_canvas.height = h
            World._temp_ctx.clearRect(0, 0, w, h) # 清除臨時 Canvas
            
            # 將圖片繪製到臨時 Canvas 上
            World._temp_ctx.drawImage(img, 0, 0, w, h)
            
            # 獲取像素數據
            img_data = World._temp_ctx.getImageData(0, 0, w, h)
            pixels = img_data.data # 這是 Uint8ClampedArray，RGBA 順序

            # 遍歷像素，將關鍵色設置為透明
            for i in range(0, len(pixels), 4):
                r = pixels[i]
                g = pixels[i+1]
                b = pixels[i+2]
                # a = pixels[i+3] # alpha 值

                if r == chroma_key_rgb[0] and g == chroma_key_rgb[1] and b == chroma_key_rgb[2]:
                    pixels[i+3] = 0 # 將 Alpha 值設為 0 (完全透明)
            
            # 將修改後的像素數據放回臨時 Canvas
            World._temp_ctx.putImageData(img_data, 0, 0)
            
            # 將處理後的臨時 Canvas 繪製到目標 Canvas 上
            ctx.drawImage(World._temp_canvas, px, py, w, h)
        else:
            # 直接繪製，不進行像素處理
            ctx.drawImage(img, px, py, w, h)
        return True

    async def _draw_walls(self):
        ctx = self.layers["walls"].getContext("2d")
        ctx.clearRect(0, 0, self.width * CELL_SIZE, self.height * CELL_SIZE)
        success = True
        
        # --- 1. 繪製外部邊界牆 ---
        # 牆壁通常不是關鍵色透明，所以這裡保持 use_chroma_key=False
        for x_coord in range(self.width):
            success &= self._draw_image(ctx, "north", x_coord, self.height - 1, CELL_SIZE, WALL_THICKNESS, offset_y=0)
        
        for x_coord in range(self.width):
            success &= self._draw_image(ctx, "north", x_coord, 0, CELL_SIZE, WALL_THICKNESS, offset_y=CELL_SIZE - WALL_THICKNESS)
            
        for y_coord in range(self.height):
            success &= self._draw_image(ctx, "east", self.width - 1, y_coord, WALL_THICKNESS, CELL_SIZE, offset_x=CELL_SIZE - WALL_THICKNESS)

        for y_coord in range(self.height):
            success &= self._draw_image(ctx, "east", 0, y_coord, WALL_THICKNESS, CELL_SIZE, offset_x=0)

        # --- 2. 疊加 JSON 中定義的牆壁 ---
        for coord_str, directions in self.walls_data.items():
            x, y = map(int, coord_str.split(","))

            for d in directions:
                if d == "north":
                    success &= self._draw_image(ctx, "north", x - 1, y - 1, CELL_SIZE, WALL_THICKNESS, offset_y=0)
                elif d == "east":
                    success &= self._draw_image(ctx, "east", x - 1, y - 1, WALL_THICKNESS, CELL_SIZE, offset_x=CELL_SIZE - WALL_THICKNESS)
        return success

    async def _draw_objects(self):
        ctx_objects = self.layers["objects"].getContext("2d")
        ctx_numbers = self.layers["numbers"].getContext("2d")

        ctx_objects.clearRect(0, 0, self.width * CELL_SIZE, self.height * CELL_SIZE)
        ctx_numbers.clearRect(0, 0, self.width * CELL_SIZE, self.height * CELL_SIZE)
        
        success = True
        
        for y_cell in range(self.height):
            for x_cell in range(self.width):
                coord_str_1_based = f"{x_cell + 1},{y_cell + 1}"
                items_in_cell = self.objects_data.get(coord_str_1_based, {})
                
                if "carrot" in items_in_cell:
                    success &= self._draw_image(ctx_objects, "pale_grass", x_cell, y_cell, CELL_SIZE, CELL_SIZE)
                else:
                    success &= self._draw_image(ctx_objects, "grass", x_cell, y_cell, CELL_SIZE, CELL_SIZE)
                
                for item, count in items_in_cell.items():
                    if item not in ["pale_grass", "grass"]:
                        success &= self._draw_image(ctx_objects, item, x_cell, y_cell, CELL_SIZE, CELL_SIZE)
                    
                    if item == "carrot" and isinstance(count, int) and 1 <= count <= 9:
                        num_size = CELL_SIZE // 2
                        offset_x = CELL_SIZE - num_size - 2
                        offset_y = CELL_SIZE - num_size - 2 
                        
                        # 這裡將 use_chroma_key 設為 True，處理數字圖片的透明背景
                        success &= self._draw_image(ctx_numbers, str(count), x_cell, y_cell, num_size, num_size, 
                                                    offset_x=offset_x, offset_y=offset_y, use_chroma_key=True)

        return success

    async def _preload_images(self):
        image_files = {
            "blue_robot_e": "blue_robot_e.png",
            "blue_robot_n": "blue_robot_n.png",
            "blue_robot_w": "blue_robot_w.png",
            "blue_robot_s": "blue_robot_s.png",
            "north": "north.png",
            "east": "east.png",
            "carrot": "carrot.png",
            "token": "token.png",
            "leaf": "leaf.png",
            "star": "star.png",
            "pale_grass": "pale_grass.png",
            "grass": "grass.png",
        }

        for i in range(1, 10):
            image_files[str(i)] = f"{i}.png"


        promises = []
        for key, filename in image_files.items():
            if key in World._image_cache and World._image_cache[key].complete:
                continue
            img = js.document.createElement("img")
            img.crossOrigin = "Anonymous"
            img.src = IMG_PATH + filename
            World._image_cache[key] = img

            def make_promise(img_element):
                def executor(resolve, reject):
                    def on_load(event):
                        img_element.removeEventListener("load", on_load)
                        img_element.removeEventListener("error", on_error)
                        resolve(img_element)
                    def on_error(event):
                        img_element.removeEventListener("load", on_load)
                        img_element.removeEventListener("error", on_error)
                        reject(f"Failed to load image: {img_element.src}")
                    img_element.addEventListener("load", on_load)
                    img_element.addEventListener("error", on_error)
                    if img_element.complete and img_element.naturalWidth > 0:
                        resolve(img_element)
                return js.Promise.new(executor)
            promises.append(make_promise(img))

        if not promises:
            return True
        try:
            await js.await_promise(js.Promise.all(promises))
            return True
        except Exception as e:
            print(f"🚨 Error during image preloading: {str(e)}")
            return False

    async def setup(self):
        for _ in range(3):
            if await self._preload_images():
                break
            await asyncio.sleep(0.5)
        else:
            print("🚨 Failed to preload images after retries.")
            return False

        await asyncio.sleep(0)
        self._draw_grid()
        
        for _ in range(3):
            if await self._draw_objects():
                break
            await asyncio.sleep(0.5)
        else:
            print("🚨 Failed to draw objects and background grass after retries.")
            return False

        for _ in range(3):
            if await self._draw_walls():
                break
            await asyncio.sleep(0.5)
        else:
            print("🚨 Failed to draw walls after retries.")
            return False
        return True

class Robot:
    _facing_order = ["E", "N", "W", "S"]

    def __init__(self, world, x, y, initial_facing="E"):
        self.world = world
        self.x = x - 1
        self.y = y - 1
        self.facing = initial_facing
        self.robot_ctx = world.layers["robots"].getContext("2d")
        self.trace_ctx = world.layers["objects"].getContext("2d")
        self._draw_robot()

    def _robot_image_key(self):
        return f"blue_robot_{self.facing.lower()}"

    def _draw_robot(self):
        self.robot_ctx.clearRect(0, 0, self.world.width * CELL_SIZE, self.world.height * CELL_SIZE)
        self.world._draw_image(self.robot_ctx, self._robot_image_key(), self.x, self.y, CELL_SIZE, CELL_SIZE)

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

    async def walk(self, steps=1):
        for _ in range(steps):
            from_x, from_y = self.x, self.y
            dx, dy = 0, 0
            if self.facing == "E": dx = 1
            elif self.facing == "W": dx = -1
            elif self.facing == "N": dy = 1
            elif self.facing == "S": dy = -1
            next_x = self.x + dx
            next_y = self.y + dy

            if not (0 <= next_x < self.world.width and 0 <= next_y < self.world.height):
                print(f"🚨 撞到邊界牆，無法移動。當前位置 ({from_x+1},{from_y+1})，朝向 {self.facing}。")
                break

            current_cell_walls_1_based = self.world.walls_data.get(f"{from_x+1},{from_y+1}", [])
            
            hit_json_wall = False
            
            if self.facing == "E":
                if "east" in current_cell_walls_1_based:
                    hit_json_wall = True
            elif self.facing == "W":
                if from_x > 0:
                    left_cell_walls_1_based = self.world.walls_data.get(f"{from_x},{from_y+1}", [])
                    if "east" in left_cell_walls_1_based:
                        hit_json_wall = True
            elif self.facing == "N":
                if "north" in current_cell_walls_1_based:
                    hit_json_wall = True
            elif self.facing == "S":
                if from_y > 0:
                    bottom_cell_walls_1_based = self.world.walls_data.get(f"{from_x+1},{from_y}", [])
                    if "north" in bottom_cell_walls_1_based:
                        hit_json_wall = True
            
            if hit_json_wall:
                print(f"🚨 撞到 JSON 定義的牆壁，無法移動。當前位置 ({from_x+1},{from_y+1})，朝向 {self.facing}。")
                break

            self.x, self.y = next_x, next_y
            self._draw_trace(from_x, from_y, self.x, self.y)
            self._draw_robot()
            await asyncio.sleep(0.2)

    async def turn_left(self):
        idx = self._facing_order.index(self.facing)
        self.facing = self._facing_order[(idx + 1) % 4]
        self._draw_robot()
        await asyncio.sleep(0.3)

def _bind_controls(robot: Robot):
    def handle_key(event):
        try:
            if event.key == 'j':
                asyncio.create_task(robot.walk(1))
            elif event.key == 'i':
                asyncio.create_task(robot.turn_left())
        except Exception as e:
            print(f"🚨 Error in key handler: {e}")

    def handle_move_button(event):
        try:
            asyncio.create_task(robot.walk(1))
        except Exception as e:
            print(f"🚨 Error in move button handler: {e}")

    def handle_turn_button(event):
        try:
            asyncio.create_task(robot.turn_left())
        except Exception as e:
            print(f"🚨 Error in turn button handler: {e}")

    js.window.py_handle_key = handle_key
    js.document.addEventListener('keydown', js.Function("event", "py_handle_key(event);"))

    js.window.py_handle_move_button = handle_move_button
    js.window.py_handle_turn_button = handle_turn_button

    robot.world.move_button.addEventListener('click', js.Function("event", "py_handle_move_button(event);"))
    robot.world.turn_button.addEventListener('click', js.Function("event", "py_handle_turn_button(event);"))

def _estimate_world_size(walls, objects, robots):
    max_x = max_y = 1
    for key in walls.keys():
        x, y = map(int, key.split(','))
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    for key in objects.keys():
        x, y = map(int, key.split(','))
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    for r in robots:
        max_x = max(max_x, r.get("x", 1))
        max_y = max(max_y, r.get("y", 1))
    return max_x, max_y

async def _fetch_world_data(url):
    """從 URL 獲取 world JSON 數據並確保轉換為 Python 原生型別"""
    try:
        print(f"嘗試從 URL 獲取內容: {url}")
        response = await js.fetch(url)
        
        if not response.ok:
            print(f"🚨 HTTP 錯誤! 狀態碼: {response.status}")
            return None

        json_data = await response.json()
        return json_data.to_py()
        
    except Exception as e:
        print(f"🚨 獲取或解析 JSON 發生錯誤: {e}")
        return None

def init(world_width=10, world_height=10, robot_x=1, robot_y=1):
    """
    方便快速建立一個world和robot，並且綁定控制。
    若呼叫執行的 URL 中沒有 world 變數, 則使用內部自帶的 world json 檔案內容建立 world 環境,
    但是若 URL 有 world 變數, 則場景畫面以 world 變數所取得的 .json 內容為主。
    建立後回傳(world, robot) tuple，方便調用。
    """
    async def _inner():
        embedded_world_data = {
            "robots": [{
                "x": 1,
                "y": 1,
                "orientation": 0,
                "objects": {
                    "carrot": "infinite"
                }
            }],
            "walls": {
                "10,1": ["east"], "10,2": ["east"], "10,3": ["east"], "10,4": ["east"], "10,5": ["east"],
                "10,6": ["east"], "10,7": ["east"], "10,8": ["east"], "10,9": ["east"],
                "10,10": ["east", "north"], "9,10": ["north"], "8,10": ["north"], "7,10": ["north"],
                "6,10": ["north"], "5,10": ["north"], "4,10": ["north"], "3,10": ["north"],
                "2,10": ["north"], "1,10": ["north"]
            },
            "goal": {
                "objects": {}
            },
            "objects": {
                "5,3": {"carrot": 1}, "5,4": {"carrot": 1}, "5,5": {"carrot": 1},
                "5,6": {"carrot": 1}, "5,7": {"carrot": 1}, "5,8": {"carrot": 1},
                "4,8": {"carrot": 1}, "4,7": {"carrot": 1}, "4,6": {"carrot": 1},
                "4,5": {"carrot": 1}, "4,4": {"carrot": 1}, "4,3": {"carrot": 1},
                "6,8": {"carrot": 1}, "6,7": {"carrot": 1}, "6,6": {"carrot": 1},
                "6,5": {"carrot": 1}, "6,4": {"carrot": 1}, "6,3": {"carrot": 1},
                "7,8": {"carrot": 1}, "7,7": {"carrot": 1}, "7,6": {"carrot": 1},
                "7,5": {"carrot": 1}, "7,4": {"carrot": 1}, "8,7": {"carrot": 1},
                "8,6": {"carrot": 1}, "8,5": {"carrot": 1}, "3,8": {"carrot": 1},
                "3,7": {"carrot": 1}, "3,6": {"carrot": 1}, "3,5": {"carrot": 1},
                "3,4": {"carrot": 1}, "8,8": {"carrot": 1}, "8,4": {"carrot": 1},
                "7,3": {"carrot": 1}, "3,3": {"carrot": 1}, "8,3": {"carrot": 1}
            }
        }
        
        data = None
        search_params = js.URLSearchParams.new(js.window.location.search)
        world_url = search_params.get("world")

        if world_url:
            print(f"檢測到 URL 中包含 'world' 參數：{world_url}")
            data = await _fetch_world_data(world_url)
            if data is None:
                print("從 URL 載入世界數據失敗，將使用內部自帶的世界設定。")
                data = embedded_world_data
            else:
                print("成功從 URL 載入世界數據。")
        else:
            print("URL 中未發現 'world' 參數，將使用內部自帶的世界設定。")
            data = embedded_world_data

        if not data:
            print("🚨 無法取得任何世界數據，無法初始化。")
            return None, None
        
        if not isinstance(data, dict):
            print(f"🚨 載入的世界數據格式不正確 (非字典類型): {type(data)}。將使用內部自帶的世界設定。")
            data = embedded_world_data
            if not data:
                print("🚨 內建世界數據也無法使用，無法初始化。")
                return None, None

        json_walls = data.get("walls", {})
        json_objects = data.get("objects", {})
        robots_data = data.get("robots", [])

        rx, ry = robot_x, robot_y
        initial_facing = "E"

        if robots_data:
            robot_start_data = robots_data[0]
            rx = robot_start_data.get("x", robot_x)
            ry = robot_start_data.get("y", robot_y)
            initial_orientation_idx = robot_start_data.get("orientation", None)
            
            if initial_orientation_idx is not None and 0 <= initial_orientation_idx < len(Robot._facing_order):
                initial_facing = Robot._facing_order[initial_orientation_idx]
            else:
                print(f"警告: 機器人數據中缺少或 'orientation' 值無效。使用預設方向: {initial_facing}")
        else:
            print("警告: 世界數據中的 'robots' 列表為空。使用預設機器人起始位置和方向。")

        estimated_width, estimated_height = _estimate_world_size(json_walls, json_objects, robots_data)
        
        width = max(world_width, estimated_width, rx + 1)
        height = max(world_height, estimated_height, ry + 1)
        
        world = World(width, height, walls=json_walls, objects=json_objects, robot_start=(rx, ry))
        
        if not await world.setup():
            raise RuntimeError("世界初始化失敗！")
        
        bot = Robot(world, rx, ry, initial_facing=initial_facing)
        
        _bind_controls(bot)
        return world, bot
    return asyncio.create_task(_inner())