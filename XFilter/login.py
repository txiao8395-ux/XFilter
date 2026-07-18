"""
XFilter V6.5
Login Manager

功能:

- 打开X登录页面
- 保存浏览器状态
- 后续自动登录

"""


import asyncio


from pathlib import Path


from playwright.async_api import async_playwright



from config import STATE_FILE





LOGIN_URL = "https://x.com/login"







async def save_login():



    async with async_playwright() as p:



        browser = await p.chromium.launch(

            headless=False

        )



        context = await browser.new_context()





        page = await context.new_page()





        await page.goto(

            LOGIN_URL

        )






        print()

        print("="*50)

        print(

            "浏览器已经打开"

        )

        print()

        print(

            "请完成："

        )

        print(

            "1. 登录 X"

        )

        print(

            "2. 确认主页可以正常打开"

        )

        print(

            "3. 登录完成后回到终端"

        )

        print()

        print(

            "按 Enter 保存登录状态"

        )

        print("="*50)






        input()






        STATE_FILE.parent.mkdir(

            parents=True,

            exist_ok=True

        )





        await context.storage_state(

            path=str(

                STATE_FILE

            )

        )





        print()

        print("="*50)

        print(

            "登录状态保存成功"

        )

        print(

            STATE_FILE

        )

        print("="*50)







        await browser.close()








def main():


    asyncio.run(

        save_login()

    )





if __name__=="__main__":


    main()