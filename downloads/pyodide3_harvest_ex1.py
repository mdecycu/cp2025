import robot
import asyncio
from pyodide.ffi import create_proxy  # 修正 create_proxy 未定義的錯誤
import js

class SmartRobot(robot.Robot):
    def __init__(self, world, x, y, initial_facing="E"):
        self.carrots_collected = 0
        super().__init__(world, x, y, initial_facing)

    def _draw_robot(self):
        super()._draw_robot()
        if self.carrots_collected > 0:
            ctx = self.robot_ctx
            num_size = 20
            offset_x = robot.CELL_SIZE - num_size - 2
            offset_y = robot.CELL_SIZE - num_size - 2
            robot.World._image_cache[str(self.carrots_collected)]  # 確保已載入圖片
            self.world._draw_image(
                ctx, str(self.carrots_collected), self.x, self.y,
                num_size, num_size, offset_x, offset_y, use_chroma_key=True
            )

    async def pick_carrot(self):
        coord_str = f"{self.x + 1},{self.y + 1}"
        cell = self.world.objects_data.get(coord_str, {})
        if "carrot" in cell and cell["carrot"] > 0:
            cell["carrot"] -= 1
            if cell["carrot"] == 0:
                del cell["carrot"]
            self.carrots_collected += 1
            await self.world._draw_objects()
            self._draw_robot()

def _bind_controls(bot: SmartRobot):
    async def move_forward(event=None):
        await bot.walk(1)

    async def turn_left(event=None):
        await bot.turn_left()

    js.window.py_smart_move = create_proxy(move_forward)
    js.window.py_smart_turn = create_proxy(turn_left)

    js.document.removeEventListener('keydown', js.window.py_handle_key)
    js.document.addEventListener('keydown', create_proxy(
        lambda e: asyncio.create_task(move_forward()) if e.key == 'j' else asyncio.create_task(turn_left()) if e.key == 'i' else None
    ))

    bot.world.move_button.onclick = js.window.py_smart_move
    bot.world.turn_button.onclick = js.window.py_smart_turn

async def init_smart_world():
    world, _ = await robot.init()
    bot = SmartRobot(world, 1, 1, initial_facing="E")
    _bind_controls(bot)
    return world, bot

async def main():
    print("🚀 啟動 SmartRobot")
    world, bot = await init_smart_world()

    # 確保朝東
    while bot.facing != "E":
        await bot.turn_left()
    await asyncio.sleep(0.5)

    # 走到 (3, 3)
    await bot.walk(2)
    await bot.turn_left()  # 向北
    await bot.walk(2)

    # 採收 carrot
    await bot.pick_carrot()
    await bot.walk()
    await bot.pick_carrot()
    print("✅ 採收完成，carrots:", bot.carrots_collected)

await main()
