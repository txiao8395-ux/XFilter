# -*- coding: utf-8 -*-

"""
XFilter V8.0 ADS版本

功能:

1. 读取 accounts.csv
2. 启动ADS池
3. 8窗口并发检测
4. activity_checker负责筛选
5. 只保存符合条件客户 success.csv

已删除:

- done缓存
- fail.csv
- 历史跳过
- 删除记录
"""


import asyncio
import csv
import os


from modules.activity_checker import run_checker
from modules.ads_browser import auto_connect_ads



# ==========================
# 配置
# ==========================


MAX_ADS = 8


INPUT_DIR = "筛选文件"

SUCCESS_FILE = "筛选完成.csv"





# ==========================
# 读取账号CSV
# ==========================


def read_accounts():

    accounts = []


    # ==========================
    # 自动寻找CSV文件
    # ==========================

    csv_files = [

    os.path.join(
        INPUT_DIR,
        x
    )

    for x in os.listdir(INPUT_DIR)

    if x.lower().endswith(".csv")

]



    if not csv_files:


        print(
            "没有找到CSV文件"
        )


        return []



    print()

    print(
        "发现CSV文件:",
        csv_files
    )

    print()



    # ==========================
    # 读取所有CSV
    # ==========================

    for file in csv_files:


        try:


            with open(

                file,

                "r",

                encoding="utf-8-sig"

            ) as f:


                reader = csv.DictReader(f)



                print(

                    file,

                    "字段:",

                    reader.fieldnames

                )




                for row in reader:



                    username = (

                        row.get("username")

                        or

                        row.get("Username")

                        or

                        row.get("用户名")

                        or

                        ""

                    ).strip()



                    if not username:


                        continue




                    accounts.append(

                        {

                            "username": username

                        }

                    )




        except UnicodeDecodeError:


            print(

                file,

                "UTF-8读取失败，尝试GBK"

            )


            try:


                with open(

                    file,

                    "r",

                    encoding="gbk"

                ) as f:



                    reader = csv.DictReader(f)



                    for row in reader:



                        username = (

                            row.get("username")

                            or

                            row.get("Username")

                            or

                            row.get("用户名")

                            or

                            ""

                        ).strip()



                        if username:


                            accounts.append(

                                {

                                    "username": username

                                }

                            )



            except Exception as e:


                print(

                    file,

                    "读取失败:",

                    e

                )




        except Exception as e:


            print(

                file,

                "读取异常:",

                e

            )




    print()

    print(

        "进入检测队列:",

        len(accounts)

    )

    print()



    return accounts






# ==========================
# 保存最终结果
# 只保存符合条件客户
# ==========================


def save_success(data):


    if not data:

        return



    exists = os.path.exists(
        SUCCESS_FILE
    )



    with open(
        SUCCESS_FILE,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:


        writer = csv.DictWriter(

            f,

            fieldnames=data.keys()

        )


        if not exists:

            writer.writeheader()



        writer.writerow(
            data
        )
        # ==========================
# ADS检测 worker
# ==========================


async def worker(
        wid,
        browser,
        queue
):


    while True:


        task = await queue.get()



        if task is None:


            queue.task_done()

            break



        username = task["username"]



        print()

        print(
            "ADS线程",
            wid,
            "检测:",
            username
        )



        result = None



        # ==========================
        # 自动重试
        # ==========================


        for retry in range(2):


            try:


                print(

                    f"{username} 第 {retry+1} 次检测"

                )



                result = await asyncio.wait_for(
    run_checker(
        browser,
        username
    ),
    timeout=30
)



                # checker返回结果
                # 代表符合筛选条件


                if result:


                    break




            except Exception as e:


                print(

                    f"{username} 检测异常:",
                    e

                )



                if retry == 0:


                    print(

                        "等待3秒重试"

                    )


                    await asyncio.sleep(3)





        # ==========================
        # 只保存符合条件账号
        # ==========================


        if result:


            try:


                save_success(

                    result

                )


                print()

                print(

                    "保留:",
                    username

                )



            except Exception as e:


                print(

                    "保存异常:",
                    e

                )



        else:


            print()

            print(

                "跳过:",
                username

            )



        queue.task_done()
        # ==========================
# 关闭ADS
# ==========================


async def close_ads(browsers):


    print()

    print(
        "释放ADS资源"
    )


    for browser in browsers:


        try:


            page = browser.get(
                "page"
            )


            if page:


                await page.close()



        except Exception as e:


            print(

                "关闭ADS异常:",
                e

            )



    await asyncio.sleep(1)



    print(

        "ADS释放完成"

    )







# ==========================
# 主程序
# ==========================


async def main():


    print()

    print(
        "启动 ADS检测池"
    )



    # ==========================
    # 启动ADS
    # ==========================


    browsers = await auto_connect_ads(

        MAX_ADS

    )



    print()


    print(

        "成功ADS数量:",

        len(browsers)

    )



    if not browsers:


        print(

            "没有可用ADS窗口"

        )


        return





    # ==========================
    # 读取账号
    # ==========================


    accounts = read_accounts()



    print(

        "账号数量:",

        len(accounts)

    )



    if not accounts:


        print(

            "没有账号"

        )


        return





    # ==========================
    # 创建队列
    # ==========================


    queue = asyncio.Queue()



    for account in accounts:


        await queue.put(

            account

        )



    print(

        "进入队列:",

        queue.qsize()

    )






    # ==========================
    # 创建ADS worker
    # ==========================


    workers = []



    for index, browser in enumerate(browsers):


        task = asyncio.create_task(

            worker(

                index + 1,

                browser,

                queue

            )

        )


        workers.append(

            task

        )







    # ==========================
    # 等待检测完成
    # ==========================


    await queue.join()



    print()


    print(

        "全部账号检测完成"

    )







    # ==========================
    # 停止worker
    # ==========================


    for _ in workers:


        await queue.put(

            None

        )




    await asyncio.gather(

        *workers,

        return_exceptions=True

    )





    # ==========================
    # 释放ADS
    # ==========================


    await close_ads(

        browsers

    )




    print()


    print(
    "最终筛选完成"
)


# 不自动关闭ADS
# await close_ads(
#     browsers
# )






# ==========================
# 程序入口
# ==========================


if __name__ == "__main__":


    try:


        asyncio.run(

            main()

        )


    except KeyboardInterrupt:


        print(

            "用户停止程序"

        )


    except Exception as e:


        print()

        print(

            "程序异常:",

            e

        )