# -*- coding: utf-8 -*-

"""
XFilter Activity Checker V9

最终规则

1. Joined:
   2024~2026

2. About this account:
   Account based in
   必须 == United States

3. Posts + Replies

4. Tweet
   Reply
   Repost

5. 最近30天

6. 职业过滤
"""

import asyncio
import os
import re
import sys

from datetime import datetime
from datetime import timedelta


# ===========================================
# 项目路径
# ===========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:

    sys.path.insert(
        0,
        BASE_DIR
    )


from modules.ads_browser import auto_connect_ads


# ===========================================
# 常量
# ===========================================

RESULT_OK = "检测-保留"

RESULT_BAD = "检测-异常"


# 最近活动

MAX_DAYS = 30


# Joined

MIN_JOIN_YEAR = 2024

MAX_JOIN_YEAR = 2026


# 程序启动时间

CHECK_START_TIME = datetime.now()


# 地区

KEEP_COUNTRY = "United States"


# 职业过滤

BAD_PROFESSION = {

    # Marketing

    "marketing",

    "marketer",

    "agency",

    "seo",

    "advertising",

    "promotion",

    "growth",

    "brand",

    # Trading

    "trader",

    "trading",

    "forex",

    "crypto",

    "stocks",

    "options",

    "investor",

    # Analyst

    "analyst",

    "research",

    "market analyst",

    # Bot

    "bot",

    "automated",

    "ai bot"

}



# ===========================================
# 页面读取
# ===========================================

async def get_page_text(page):

    try:

        return await page.locator(
            "body"
        ).inner_text(
            timeout=10000
        )

    except Exception as e:

        print(
            "读取页面失败:",
            e
        )

        return ""


# ===========================================
# 打开主页
# ===========================================

async def open_profile(
    page,
    username
):

    try:

        url = f"https://x.com/{username}"

        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        await page.wait_for_timeout(
            3000
        )

        return True

    except Exception as e:

        print(
            "打开主页失败:",
            e
        )

        return False


# ===========================================
# About this account
# ===========================================

async def open_about_account(page):

    try:

        # 点击更多按钮
        more_btn = page.locator(
            '[aria-label*="More"],[aria-label*="更多"]'
        )

        if await more_btn.count() > 0:

            await more_btn.first.click()

            await page.wait_for_timeout(1200)

        # About this account
        about = page.get_by_text(
            "About this account",
            exact=False
        )

        if await about.count() == 0:

            about = page.get_by_text(
                "关于此账户",
                exact=False
            )

        if await about.count() == 0:

            return ""

        await about.first.click()

        await page.wait_for_timeout(
            2000
        )

        text = await get_page_text(
            page
        )

        # ESC 返回主页
        await page.keyboard.press("Escape")

        await page.wait_for_timeout(
            800
        )

        return text

    except Exception as e:

        print(
            "读取 About this account 失败:",
            e
        )

        return ""





# ===========================================
# Joined
# ===========================================

def get_join_year(text):

    if not text:
        return 0

    patterns = [

        r"Joined\s+[A-Za-z]+\s+(\d{4})",

        r"(\d{4})年\d{1,2}月加入"

    ]

    for p in patterns:

        m = re.search(
            p,
            text,
            re.I
        )

        if m:

            try:

                return int(
                    m.group(1)
                )

            except:

                pass

    return 0


def check_join_year(year):

    return (

        MIN_JOIN_YEAR

        <=

        year

        <=

        MAX_JOIN_YEAR

    )


# ===========================================
# About this account
# Account based in
# ===========================================

def get_account_based_in(text):

    if not text:

        return ""

    lines = [

        x.strip()

        for x in text.splitlines()

        if x.strip()

    ]

    for i, line in enumerate(lines):

        if (

            line == "Account based in"

            or

            line == "账户位于"

        ):

            if i + 1 < len(lines):

                return lines[i + 1].strip()

    return ""


def check_country(account_based):

    return (

        account_based

        ==

        KEEP_COUNTRY

    )


# ===========================================
# 职业过滤
# ===========================================

def check_profession_filter(text):

    if not text:

        return False

    text = text.lower()

    for word in BAD_PROFESSION:

        if word in text:

            return True

    return False







# ===========================================
# Posts / Replies 数量
# ===========================================

def get_posts_count(text):

    if not text:
        return 0

    patterns = [

        r"([\d,]+)\s+Posts",

        r"([\d,]+)\s+posts",

        r"([\d,]+)\s+帖子"

    ]

    for p in patterns:

        m = re.search(
            p,
            text,
            re.I
        )

        if m:

            return int(
                m.group(1).replace(",", "")
            )

    return 0


def get_replies_count(text):

    if not text:
        return 0

    patterns = [

        r"([\d,]+)\s+Replies",

        r"([\d,]+)\s+replies",

        r"([\d,]+)\s+回复"

    ]

    for p in patterns:

        m = re.search(
            p,
            text,
            re.I
        )

        if m:

            return int(
                m.group(1).replace(",", "")
            )

    return 0


# ===========================================
# 最近活动
# ===========================================

async def get_latest_activities(page):

    result = []

    try:

        articles = page.locator("article")

        total = await articles.count()

        for i in range(total):

            if len(result) >= 3:
                break

            try:

                article = articles.nth(i)

                text = await article.inner_text()

                if text:

                    result.append(text)

            except:

                continue

    except Exception as e:

        print("读取活动失败:", e)

    return result


# ===========================================
# Pinned
# ===========================================

def is_pinned(text):

    if not text:
        return False

    return (

        "Pinned" in text

        or

        "置顶" in text

    )


# ===========================================
# Tweet / Reply / Repost
# ===========================================

def get_activity_type(text):

    if not text:
        return "tweet"

    low = text.lower()

    if (

        "reposted" in low

        or

        "repost" in low

        or

        "转发" in text

    ):

        return "repost"

    if (

        "replying to" in low

        or

        "回复" in text

    ):

        return "reply"

    return "tweet"


def check_activity_time(text):

    activity_time = parse_x_time(text)

    if activity_time is None:

        return False

    return check_within_30_days(
        activity_time
    )


# ===========================================
# 最近3条活动
# ===========================================

def check_recent_activity(activities):

    if not activities:

        # 没有活动
        return True

    valid = 0

    for item in activities:

        # Pinned 超过30天跳过

        if is_pinned(item):

            t = parse_x_time(item)

            if t:

                if not check_within_30_days(t):

                    continue

        activity_type = get_activity_type(item)

        if activity_type == "tweet":

            if check_activity_time(item):

                valid += 1

        elif activity_type == "reply":

            if check_activity_time(item):

                valid += 1

        elif activity_type == "repost":

            # 按用户主页显示的 Repost 时间
            if check_activity_time(item):

                valid += 1

    return valid > 0





# ===========================================
# X 时间解析
# ===========================================

def parse_x_time(text):

    if not text:
        return None

    now = datetime.now()

    # ---------- 相对时间 ----------

    relative_patterns = [

        (r"(\d+)\s*s", "seconds"),
        (r"(\d+)\s*m", "minutes"),
        (r"(\d+)\s*h", "hours"),
        (r"(\d+)\s*d", "days"),

        (r"(\d+)\s*秒", "seconds"),
        (r"(\d+)\s*分钟", "minutes"),
        (r"(\d+)\s*小时", "hours"),
        (r"(\d+)\s*天", "days"),

    ]

    for pattern, unit in relative_patterns:

        m = re.search(
            pattern,
            text,
            re.I
        )

        if m:

            value = int(m.group(1))

            if unit == "seconds":
                return now - timedelta(seconds=value)

            if unit == "minutes":
                return now - timedelta(minutes=value)

            if unit == "hours":
                return now - timedelta(hours=value)

            if unit == "days":
                return now - timedelta(days=value)

    # ---------- 英文日期 ----------

    months = {

        "Jan":1,
        "Feb":2,
        "Mar":3,
        "Apr":4,
        "May":5,
        "Jun":6,
        "Jul":7,
        "Aug":8,
        "Sep":9,
        "Oct":10,
        "Nov":11,
        "Dec":12

    }

    m = re.search(

        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:,\s*(\d{4}))?",

        text

    )

    if m:

        month = months[m.group(1)]

        day = int(m.group(2))

        year = m.group(3)

        if year:

            year = int(year)

        else:

            year = now.year

        try:

            return datetime(
                year,
                month,
                day
            )

        except:

            pass

    return None


# ===========================================
# 30天判断
# ===========================================

def check_within_30_days(activity_time):

    if activity_time is None:
        return False

    delta = CHECK_START_TIME - activity_time

    return (

        delta.total_seconds() >= 0

        and

        delta.total_seconds()

        <=

        MAX_DAYS * 86400

    )



# ===========================================
# 主检测
# ===========================================

async def run_checker(browser, username):

    page = browser.get("page")

    if page is None:

        return None

    # ---------------------------------------
    # 打开主页
    # ---------------------------------------

    ok = await open_profile(
        page,
        username
    )

    if not ok:

        return None

    text = await get_page_text(page)

    if not text:

        return None

    # ---------------------------------------
    # Joined
    # ---------------------------------------

    join_year = get_join_year(text)

    if not check_join_year(join_year):

        return None

    # ---------------------------------------
    # About this account
    # ---------------------------------------

    about_text = await open_about_account(page)

    account_based = get_account_based_in(
        about_text
    )

    if not check_country(account_based):

        return None

    # ---------------------------------------
    # 职业过滤
    # ---------------------------------------

    if check_profession_filter(text):

        return None

    # ---------------------------------------
    # Posts / Replies 数量
    # ---------------------------------------

    posts_count = get_posts_count(text)

    replies_count = get_replies_count(text)

    # ---------------------------------------
    # 0 Posts
    # ---------------------------------------

    if posts_count == 0 and replies_count == 0:

        return {

            "username": username,

            "join_year": join_year,

            "country": account_based,

            "posts": 0,

            "replies": 0,

            "result": RESULT_OK

        }

    # ---------------------------------------
    # 最近活动
    # ---------------------------------------

    activities = await get_latest_activities(
        page
    )

    if not check_recent_activity(
        activities
    ):

        return None

    # ---------------------------------------
    # 返回
    # ---------------------------------------

    return {

        "username": username,

        "join_year": join_year,

        "country": account_based,

        "posts": posts_count,

        "replies": replies_count,

        "result": RESULT_OK,

        "checked_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    }