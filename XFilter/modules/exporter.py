import openpyxl
from datetime import datetime
import os


RESULT_FILE = "results.xlsx"


def export_excel(results):

    if not results:
        print("没有结果可导出")
        return


    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "检测结果"


    headers = [
        "用户名",
        "ADS_ID",
        "帖子数量",
        "注册时间",
        "注册年份",
        "账号年龄",
        "地区",
        "美国地区",
        "检测结果",
        "原因"
    ]


    ws.append(headers)


    for item in results:

        ws.append(
            [
                item.get("用户名",""),
                item.get("ADS_ID",""),
                item.get("帖子数量",""),
                item.get("注册时间",""),
                item.get("注册年份",""),
                item.get("账号年龄",""),
                item.get("地区",""),
                item.get("美国地区",""),
                item.get("检测结果",""),
                item.get("原因","")
            ]
        )


    for col in ws.columns:

        max_length = 0

        col_letter = col[0].column_letter


        for cell in col:

            if cell.value:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )


        ws.column_dimensions[col_letter].width = max_length + 3



    wb.save(RESULT_FILE)


    print()
    print("================")
    print("Excel导出完成:")
    print(
        os.path.abspath(RESULT_FILE)
    )
    print("================")