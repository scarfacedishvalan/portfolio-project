import asyncio

async def fetch_data(delay, id):
    print(f"Fetching data for {id}")
    await asyncio.sleep(delay)
    print("Data fetched")
    if id==0:
        raise ValueError("Not alloweed")
    return {"data": "some data", "id": id}


async def main():
    print("Start of main coroutine")
    # task1 = asyncio.create_task(fetch_data(2, 1))
    # task2 = asyncio.create_task(fetch_data(2, 2))
    
    # result1 = await task1
    # # print(f"Received {result1}")

    # result2 = await task2
    results = await asyncio.gather(fetch_data(1,1), fetch_data(1,3), fetch_data(1,0))
    # print(f"Received {result2}")
    print(results)

asyncio.run(main())