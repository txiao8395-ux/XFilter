"""
XFilter V6.5
Cache Manager

功能:

- 保存账号检测结果
- 读取缓存
- 判断是否缓存
- 更新缓存
"""


import json

from pathlib import Path

from datetime import datetime



from config import CACHE_DIR





CACHE_FILE = CACHE_DIR / "activity_cache.json"






# ==========================
# 读取缓存
# ==========================


def load_cache():


    if not CACHE_FILE.exists():


        return {}



    try:


        with open(

            CACHE_FILE,

            "r",

            encoding="utf-8"

        ) as f:


            return json.load(f)



    except Exception:


        return {}








# ==========================
# 保存缓存
# ==========================


def save_cache(cache):


    CACHE_FILE.parent.mkdir(

        parents=True,

        exist_ok=True

    )



    with open(

        CACHE_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            cache,

            f,

            ensure_ascii=False,

            indent=2

        )








# ==========================
# 判断缓存
# ==========================


def is_cached(username, cache):


    return username in cache







# ==========================
# 获取缓存数据
# ==========================


def get_cache(username, cache):


    return cache.get(

        username,

        None

    )







# ==========================
# 写入缓存
# ==========================


def set_cache(

    username,

    data,

    cache

):


    data["cache_time"]=(

        datetime.now()

        .strftime(

            "%Y-%m-%d %H:%M:%S"

        )

    )



    cache[username]=data



    return cache