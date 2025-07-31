import robot
import asyncio

async def main():
    world, bot = await robot.init(10, 10, 1, 1)
    print("機器人開始行動")
    # 繞場一圈
    for i in range(3):
        await bot.walk(9)
        await bot.turn_left()
    await bot.walk(9)
    print("🚩 巡邏完成！")

await main()