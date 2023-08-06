# pythonファイルのリストアップ [listupy]

import os
import sys
import fies
import argparse
from sout import sout

# 再帰的にpythonファイルをすべて列挙
def r_listup(dir_name):
	dir_fies = fies[dir_name]
	ret_ls = []
	for file in dir_fies:
		fullpath = os.path.join(dir_name, file)
		if os.path.isdir(fullpath) is True:
			ret_ls += r_listup(fullpath)
		else:
			if file.endswith(".py") is False: continue
			ret_ls.append((file, dir_fies[file, "text"]))
	return ret_ls

# 行数合計の計算
def line_n(file_ls):
	ret_n = 0
	for _, content in file_ls:
		ret_n += len(content.split("\n"))
	return ret_n

# pythonファイルのリストアップ [listupy]
def listup(dir_name):
	# 再帰的にpythonファイルをすべて列挙
	file_ls = r_listup(dir_name)
	# 統計情報
	res = f"# listupy report\n\n## summary\n- {line_n(file_ls)} lines\n- {len(file_ls)} files\n\n"
	# 各ファイルの内容を足していく
	for filename, content in file_ls:
		res += f"## {filename}\n```python\n{content}\n```\n\n"
	return res

# コンソールから利用
def console_command():
	# コンソール引数
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", required = True, help = "Target directory name.")
	parser.add_argument("-o", "--output", required = False, help = "Output text filepath.")
	args_dic = vars(parser.parse_args())
	# pythonファイルのリストアップ [listupy]
	res = listup(args_dic["input"])
	# 出力
	if args_dic["output"] is None: args_dic["output"] = "./listup_result.md"
	fies[args_dic["output"], "text"] = res
