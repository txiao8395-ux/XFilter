import aiohttp
import asyncio


ADS_API = "http://local.adspower.net:50325"



async def start_ads(
    ads_id
):


    url = (
        ADS_API +
        "/api/v1/browser/start"
    )


    params = {

        "user_id": ads_id

    }



    async with aiohttp.ClientSession() as session:


        try:


            async with session.get(
                url,
                params=params
            ) as resp:


                data = await resp.json()


                print(
                    "启动ADS:",
                    ads_id,
                    data
                )



                if data.get("code") == 0:


                    return True



                return False



        except Exception as e:


            print(
                "ADS启动失败:",
                ads_id,
                e
            )


            return False






async def start_multiple_ads(
    accounts
):


    tasks = []


    for account in accounts:


        tasks.append(

            start_ads(
                account["ads_id"]
            )

        )



    results = await asyncio.gather(
        *tasks
    )


    return results