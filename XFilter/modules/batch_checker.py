# -*- coding: utf-8 -*-

import asyncio
asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)
import csv
import os
import json


from modules.activity_checker import run_checker
from modules.ads_browser import auto_connect_ads



# =========================
# 配置
# =========================


MAX_ADS = 8

INPUT_FILE = "accounts.csv"

SUCCESS_FILE = "success.csv"

FAIL_FILE = "fail.csv"

DONE_FILE = "done.json"





# =========================
# DONE
# =========================


def load_done():

    if not os.path.exists(DONE_FILE):

        return set()


    try:

        with open(
            DONE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return set(
                json.load(f)
            )


    except:

        return set()



def save_done(done):

    with open(
        DONE_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            list(done),

            f,

            ensure_ascii=False

        )





# =========================
# CSV读取
# =========================


def read_accounts():


    if not os.path.exists(INPUT_FILE):

        print(
            "没有找到:",
            INPUT_FILE
        )

        return



    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:


        reader = csv.DictReader(f)


        print(
            "CSV字段:",
            reader.fieldnames
        )


        for row in reader:


            username = (

                row.get("username")

                or

                row.get("用户名")

                or

                row.get("user")

            )


            ads_id = (

                row.get("ads_id")

                or ""

            )


            if not username:

                continue



            yield {

                "username":
                    username.strip(),


                "ads_id":
                    ads_id.strip()

            }






# =========================
# 保存CSV
# =========================


def save_csv(
        filename,
        data
):


    exists = os.path.exists(
        filename
    )


    with open(
        filename,
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





# =========================
# ADS工作线程
# =========================


async def ads_worker(
        worker_id,
        browser,
        queue,
        done
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
            worker_id,
            "检测:",
            username
        )



        try:



            result = await run_checker(

                browser,

                username

            )



            if result:


                save_csv(

                    SUCCESS_FILE,

                    result

                )


                print(

                    "成功:",

                    username

                )



            else:


                save_csv(

                    FAIL_FILE,

                    {

                        "用户名":
                            username,


                        "原因":
                            "无返回"

                    }

                )



        except Exception as e:



            print(

                username,

                "失败:",

                e

            )


            save_csv(

                FAIL_FILE,

                {

                    "用户名":
                        username,


                    "原因":
                        str(e)

                }

            )



        finally:



            done.add(
                username
            )


            save_done(
                done
            )


            queue.task_done()







# =========================
# 主程序
# =========================


async def main():


    print(
        "启动8 ADS检测池"
    )



    # 启动ADS池

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
            "没有可用ADS"
        )

        return




    done = load_done()



    queue = asyncio.Queue()



    count = 0



    for account in read_accounts():


        username = account["username"]



        if username in done:

            continue



        await queue.put(
            account
        )


        count += 1



    print(

        "进入队列:",

        count

    )




    workers=[]



    for i,browser in enumerate(browsers):


        workers.append(

            asyncio.create_task(

                ads_worker(

                    i+1,

                    browser,

                    queue,

                    done

                )

            )

        )




    await queue.join()



    for _ in browsers:

        await queue.put(
            None
        )



    await asyncio.gather(
        *workers
    )



    print()

    print(
        "全部完成"
    )







if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass