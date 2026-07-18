import pandas as pd
import asyncio

from modules.activity_checker import check_account



async def main():


    account = {


        "用户名":"JamcdKoch",


        "主页链接":"https://x.com/JamcdKoch",


        "ADS_ID":"k1bjaq2b"


    }



    result = await check_account(

        account

    )


    print()

    print("================")

    print(result)

    print("================")




asyncio.run(main())