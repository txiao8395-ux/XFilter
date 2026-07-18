import asyncio
import aiohttp

from playwright.async_api import async_playwright


ADS_API = "http://local.adspower.net:50325"


# ================================
# 获取全部ADS账号
# ================================

async def get_ads_profiles():

    result = []

    try:

        page = 1

        while True:

            url = ADS_API + "/api/v1/user/list"

            params = {
                "page": page,
                "page_size": 100
            }


            async with aiohttp.ClientSession() as session:

                async with session.get(
                    url,
                    params=params
                ) as resp:

                    data = await resp.json()



            if data.get("code") != 0:
                break



            users = (
                data
                .get("data", {})
                .get("list", [])
            )


            if not users:
                break



            for user in users:

                uid = user.get(
                    "user_id"
                )


                if uid:

                    result.append(
                        {
                            "ads_id": uid,
                            "name": user.get(
                                "name",
                                ""
                            )
                        }
                    )



            if len(users) < 100:

                break


            page += 1



    except Exception as e:

        print(
            "读取ADS失败:",
            e
        )


    return result





# ================================
# 连接单个ADS
# ================================

async def connect_ads_id(
        ads_id
):

    pw = None


    try:

        print(
            "连接ADS:",
            ads_id
        )


        url = ADS_API + "/api/v1/browser/start"


        params = {

            "user_id": ads_id,

            "open_tabs": 1

        }



        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                params=params
            ) as resp:

                data = await resp.json()



        print(
            "ADS返回:",
            data
        )



        ws = (
            data
            .get("data", {})
            .get("ws", {})
            .get("puppeteer")
        )



        if not ws:

            raise Exception(
                "没有CDP地址"
            )



        print(
            "CDP:",
            ws
        )



        pw = await async_playwright().start()



        browser = await pw.chromium.connect_over_cdp(
            ws
        )



        pages=[]


        for c in browser.contexts:

            pages.extend(
                c.pages
            )



        if pages:

            page = pages[0]

        else:

            page = await browser.new_page()



        print(
            "ADS连接成功:",
            ads_id
        )


        return {

            "ads_id": ads_id,

            "browser": browser,

            "page": page,

            "playwright": pw

        }



    except Exception as e:


        print(
            "ADS连接失败:",
            ads_id,
            e
        )



        if pw:

            try:

                await pw.stop()

            except:

                pass



        return None







# ================================
# 8窗口连接池
# ================================

async def connect_multiple_ads(
        ads_ids,
        max_workers=8
):


    results=[]


    for index, ads_id in enumerate(ads_ids):


        # 控制启动速度

        if index > 0:

            await asyncio.sleep(
                3
            )


        retry = 3



        for i in range(retry):


            browser = await connect_ads_id(
                ads_id
            )



            if browser:

                results.append(
                    browser
                )

                break



            print(
                "重试:",
                ads_id,
                i+1
            )



            await asyncio.sleep(
                5
            )



    return results







# ================================
# 自动连接
# ================================

async def auto_connect_ads(
        limit=8
):


    profiles = await get_ads_profiles()



    print()

    print(
        "ADS原始数量:",
        len(profiles)
    )



    for p in profiles:

        print(
            "ADS:",
            p
        )



    if not profiles:

        print(
            "没有ADS账号"
        )

        return []



    ads_ids=[
        x["ads_id"]
        for x in profiles
    ]



    ads_ids = ads_ids[:limit]



    print(
        "连接数量:",
        len(ads_ids)
    )



    return await connect_multiple_ads(
        ads_ids,
        limit
    )







# ================================
# 旧接口
# ================================

async def connect_ads():


    profiles = await get_ads_profiles()



    if not profiles:

        return None



    return await connect_ads_id(
        profiles[0]["ads_id"]
    )








# ================================
# 页面检测
# ================================

async def check_page(page):

    try:

        return {

            "url": page.url,

            "title": await page.title()

        }


    except:

        return {

            "url":"",

            "title":""

        }








# ================================
# 测试
# ================================

async def test_ads():


    print(
        "开始测试ADS连接"
    )


    browsers = await auto_connect_ads(
        8
    )



    print(
        "成功连接窗口:",
        len(browsers)
    )



    for b in browsers:


        print(
            await check_page(
                b["page"]
            )
        )



    # 测试阶段不关闭





if __name__=="__main__":

    asyncio.run(
        test_ads()
    )