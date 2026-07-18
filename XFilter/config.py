"""
XFilter V6.5
Global Configuration
"""


from pathlib import Path

import os



# ==========================
# 项目路径
# ==========================


BASE_DIR = Path(__file__).parent



DATA_DIR = BASE_DIR / "data"


OUTPUT_DIR = BASE_DIR / "output"



CACHE_DIR = DATA_DIR / "cache"



STATE_FILE = (

    DATA_DIR

    /

    "browser_state"

    /

    "state.json"

)





# ==========================
# 活跃检测
# ==========================


ACTIVE_DAYS = 30



# 最新检测帖子数量

CHECK_POST_LIMIT = 3






# ==========================
# 账号规则
# ==========================


# 允许注册年份


ALLOW_JOIN_YEAR = [

    2024,

    2025,

    2026

]




# 美国关键词


USA_KEYWORDS = [

    "usa",

    "united states",

    "america",

    "california",

    "texas",

    "new york",

    "florida",

    "washington",

    "chicago",

]





# 排除地区


BLOCK_COUNTRY = [

    "china",

    "japan",

    "india",

    "russia",

]








# ==========================
# 性能
# ==========================


def get_workers():


    cpu=os.cpu_count() or 4



    if cpu >= 16:


        return 48



    if cpu >= 8:


        return 32



    if cpu >= 4:


        return 16



    return 8





WORKERS = get_workers()





# 浏览器设置


HEADLESS = True



TIMEOUT = 15000





# ==========================
# CSV
# ==========================


RESULT_FILE = (

    OUTPUT_DIR

    /

    "result.csv"

)





# ==========================
# 创建目录
# ==========================


for folder in [

    DATA_DIR,

    OUTPUT_DIR,

    CACHE_DIR,

    STATE_FILE.parent

]:


    folder.mkdir(

        parents=True,

        exist_ok=True

    )