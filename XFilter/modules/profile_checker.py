"""
XFilter V6.5
Profile Checker

功能:

- 美国地区识别
- 注册年份识别
- 用户主页资料解析

"""


import re


from datetime import datetime



from config import (

    USA_KEYWORDS,

    BLOCK_COUNTRY,

    ALLOW_JOIN_YEAR

)






# ==========================
# 地区检测
# ==========================


def check_usa(location):


    if not location:


        return False



    text=location.lower().strip()





    # 排除地区


    for item in BLOCK_COUNTRY:


        if item in text:


            return False






    # 美国关键词


    for item in USA_KEYWORDS:


        if item in text:


            return True





    return False








# ==========================
# 注册年份
# ==========================


def extract_join_year(text):


    if not text:


        return None





    text=text.lower()






    patterns=[


        r'joined\s+\w+\s+(\d{4})',


        r'加入.*?(\d{4})',


        r'(\d{4})年加入'


    ]






    for pattern in patterns:


        result=re.search(

            pattern,

            text,

            re.I

        )



        if result:


            try:


                return int(

                    result.group(1)

                )



            except:


                pass






    return None







# ==========================
# 注册年份过滤
# ==========================


def check_join_year(year):


    if not year:


        return False





    return year in ALLOW_JOIN_YEAR








# ==========================
# 用户资料结果
# ==========================


def profile_result():


    return {


        "location":"",


        "join_year":None,


        "usa":False,


        "year_ok":False,


        "active":False


    }








# ==========================
# 页面文字解析
# ==========================


def parse_profile(text):


    result=profile_result()





    if not text:


        return result






    # 地区


    location=""




    lines=text.splitlines()



    for line in lines:


        line=line.strip()



        if not line:


            continue




        low=line.lower()



        for key in USA_KEYWORDS:


            if key in low:


                location=line


                break






        if location:


            break







    result["location"]=location



    result["usa"]=check_usa(

        location

    )







    # 注册年份


    year=extract_join_year(

        text

    )



    result["join_year"]=year



    result["year_ok"]=check_join_year(

        year

    )





    # 最终


    if (

        result["usa"]

        and

        result["year_ok"]

    ):


        result["active"]=True





    return result