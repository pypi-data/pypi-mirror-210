# listupy

下の方に日本語の説明があります

## Listupy Documentation

### Introduction

Listupy is a command-line Python tool that allows you to recursively enumerate Python files within a directory, compute the total number of lines in those files, and consolidate the results into a single markdown file. The name "Listupy" is a portmanteau of "listup" and "python," and is pronounced as "list-a-pie."

### Installation

To install Listupy, use the following pip command:

```bash
pip install listupy
```

### Usage

You can use Listupy from the command line using the `listupy` command. Below is an example:

```bash
listupy -i /path/to/directory -o /path/to/output.md
```

The `-i` argument requires the directory path to be scanned. The `-o` argument, which is optional, is used to specify the output markdown file path. If the `-o` argument is not provided, the output will be saved as `./listup_result.md` by default.

### Code Explanation
Listupy is primarily composed of four functions: `r_listup`, `line_n`, `listup`, and `console_command`.

- `r_listup(dir_name)` is a recursive function that lists all python files in a directory.
- `line_n(file_ls)` calculates the total number of lines from a list of files.
- `listup(dir_name)` lists all python files in a directory, computes the total line count, and generates a markdown-formatted string.
- `console_command()` handles command-line arguments and orchestrates the listup process.

### Notes

- Ensure that the directory you're scanning doesn't contain large numbers of Python files, as this could significantly slow down the performance of Listupy.



## Listupyドキュメンテーション

### はじめに

Listupyはコマンドラインから利用できるPythonツールで、ディレクトリ内のPythonファイルを再帰的に列挙し、それらのファイルの行数の合計を計算し、結果を1つのmarkdownファイルにまとめます。"Listupy"という名前は"listup"と"python"の合成語で、「リストアッパイ」と読みます。

### インストール

Listupyのインストールは以下のpipコマンドで行うことができます：

```bash
pip install listupy
```

### 使用方法

コマンドラインから`listupy`コマンドを使ってListupyを使用できます。以下に使用例を示します：

```bash
listupy -i /path/to/directory -o /path/to/output.md
```

`-i`引数にはスキャンするディレクトリのパスを指定します。`-o`引数はオプションで、出力markdownファイルのパスを指定します。`-o`引数が指定されていない場合、出力はデフォルトで`./listup_result.md`として保存されます。

### コードの説明
Listupyは主に4つの関数で構成されています：`r_listup`、`line_n`、`listup`、そして`console_command`。

- `r_listup(dir_name)`はディレクトリ内の全てのPythonファイルを列挙する再帰関数です。
- `line_n(file_ls)`はファイルのリストから行数の合計を計算します。
- `listup(dir_name)`はディレクトリ内の全てのPythonファイルを列挙し、行数の合計を計算し、markdown形式の文字列を生成します。
- `console_command()`はコマンドライン引数を処理し、リストアッププロセスを調整します。

### 注意点
- スキャンするディレクトリが大量のPythonファイルを含んでいないことを確認してください。大量のファイルがあるとListupyのパフォーマンスが大幅に低下する可能性があります。
