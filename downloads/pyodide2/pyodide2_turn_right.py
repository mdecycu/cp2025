import robot
import asyncio

# 定義右轉的非同步函式
async def turn_right(bot):
    for _ in range(3):
        await bot.turn_left()

async def main():
    world, bot = await robot.init(10, 10, 1, 1)
    print("機器人開始行動")
    await bot.turn_left()
    await bot.walk(9)
    await turn_right(bot) 
    print("機器人完成行動")

# main() 讓出執行控制權，由頁面中的 even loop 決定何時執行 main()
await main()
