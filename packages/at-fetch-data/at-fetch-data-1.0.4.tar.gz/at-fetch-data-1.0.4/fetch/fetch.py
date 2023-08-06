from typing import List
import asyncio
from .const import CHUNK_SIZE, CONCURRENT_LIMIT, INTERVAL
import httpx
import pandas as pd


class Fetch:
    def __init__(self) -> None:
        self.semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    async def get(self, url: str, params):
        # 错误重试3次
        max_retries = 3
        async with self.semaphore:
            for i in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        res = await client.get(url, params=params)
                        res.raise_for_status()
                        return res
                except Exception as e:
                    print(f"Request failed with error {e}, retrying... (attempt {i + 1})")
                    if i < max_retries - 1:
                        await asyncio.sleep(2**i)  # Exponential backoff
                    else:
                        raise

    def split_large_number(self, number: int, size: int) -> List[int]:
        if number < size:
            return [number]
        else:
            chunks = number // size
            result = [size] * chunks
            remainder = number % size
            if remainder > 0:
                result.append(remainder)
            return result

    async def get_all_klines_data(
        self, url: str, symbol: str, interval: str, start_time: int, end_time: int
    ):
        #    1. 根据start_time到end_time的时间戳算出来，然后根据interval，把对应的count数量计算
        #    2. count值等于limit数据
        #    3. 切片对应的数据
        #    4. 通过异步请求，并发，async.gather的方案实现对应的逻辑，然后等所有数据返回以后拼装数据
        #    5. 中间如果有对应的数据出错，就做重试操作，如果重试失败超过对应的次数，则raise error出来
        interval_timestamp = INTERVAL[interval]

        diff = end_time - start_time + interval_timestamp
        if diff < 0:
            raise Exception("start time gt end time")
        
        limit = diff // interval_timestamp
        limit_chunks = self.split_large_number(limit, CHUNK_SIZE)
        async_tasks = []
        new_start_time = start_time
        for i, chunk in enumerate(limit_chunks):
            new_start_time = start_time + i * CHUNK_SIZE * interval_timestamp
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": chunk,
                "start_time": new_start_time,
            }
            task = self.get(url, params)
            async_tasks.append(task)
        res = await asyncio.gather(*async_tasks)
        df = []
        for item in res:
            obj = item.json()
            data = pd.DataFrame(obj["data"])
            df.append(data)
        df_res = pd.concat(df)
        return df_res.drop_duplicates()

    
    async def get_kline_count(
        self, url: str, symbol: str, interval: str, start_time: int, end_time: int
    ):
        params = {
            "symbol": symbol,
            "interval": interval,
            "start_time": start_time,
            "end_time": end_time,
        }
        res = await self.get(url, params)
        return res.json()["data"]