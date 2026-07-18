import asyncio

from modules.ads_browser import connect_ads



async def main():


    print("开始连接ADS...")


    ads = await connect_ads()


    print("ADS连接成功")


    page = ads["page"]


    print(
        "页面数量:",
        len(ads["context"].pages)
    )


    for i,p in enumerate(
        ads["context"].pages
    ):

        print(
            i,
            p.url
        )



    print(
        "当前页面:",
        page.url
    )


    try:

        title = await page.title()

        print(
            "标题:",
            title
        )

    except Exception as e:

        print(
            "标题读取失败:",
            e
        )



    await asyncio.sleep(10)




asyncio.run(main())