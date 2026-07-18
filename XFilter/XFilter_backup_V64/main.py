"""
XFilter V5
Main Pipeline

流程:

X.csv
 ↓
基础过滤
 ↓
营销/推广过滤
 ↓
美国账号检测
 ↓
30天活跃检测
 ↓
CSV输出
"""


from utils.helpers import load_csv


from modules.filters import (
    filter_accounts
)


from modules.account_age_filter import (
    account_age_filter
)


from modules.category_filter import (
    category_filter
)


from modules.usa_checker import (
    check_us_accounts
)


from modules.activity_checker import (
    activity_filter
)


from modules.exporter import (
    export_us_accounts
)



from config import (
    INPUT_FILE
)



def main():


    print()

    print("=" * 50)

    print(
        "XFilter V5 START"
    )

    print("=" * 50)



    # ======================
    # 读取CSV
    # ======================


    df = load_csv(
        INPUT_FILE
    )



    # ======================
    # 基础过滤
    # ======================


    df = filter_accounts(
        df
    )
    # 账号年份过滤

    df = account_age_filter(
        df
    )


    # ======================
    # 营销/分析类过滤
    # ======================


    df = category_filter(
        df
    )



    # ======================
    # 美国账号检测
    # ======================


    us_df = check_us_accounts(
        df
    )



    # ======================
    # 30天活跃检测
    # ======================


    us_df = activity_filter(
        us_df
    )



    # ======================
    # 输出CSV
    # ======================


    export_us_accounts(
        us_df
    )



    print()

    print("=" * 50)

    print(
        "XFilter V5 DONE"
    )

    print(
        f"最终账号:{len(us_df)}"
    )

    print("=" * 50)





if __name__ == "__main__":

    main()