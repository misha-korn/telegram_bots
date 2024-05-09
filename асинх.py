import time


def foo1():
    time.sleep(3)
    print(1)

def foo2():
    time.sleep(2)
    print(2)


# foo1()
# foo2()

# CPUbound нагрузка - нагрузка на процессор - вычисления
# IObound нагрузка - нагрузка на сеть — тупо ждем ответа

import asyncio

async def foo1():
    print(1)
    await asyncio.sleep(10)
    print(19)

async def foo2():
    print(2)
    await asyncio.sleep(2)
    print(29)

async def foo3():
    print(3)
    await asyncio.sleep(4)
    print(39)

async def main():
    
    task1 = asyncio.create_task(foo1())
    task2 = asyncio.create_task(foo2())
    task3 = asyncio.create_task(foo3())

    await task1
    await task2
    await task3
    

    
asyncio.run(main())

