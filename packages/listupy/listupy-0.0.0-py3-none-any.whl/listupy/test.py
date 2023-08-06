
# listupy [listupy]
# 【動作確認 / 使用例】

import sys
import fies
import ezpip
listupy = ezpip.load_develop("listupy", "../", develop_flag = True)

# pythonファイルのリストアップ [listupy]
res = listupy.listup("./")

fies["listup_result.md"] = res
