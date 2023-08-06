
from setuptools import setup
# 公開用パッケージの作成 [ezpip]
import ezpip

# 公開用パッケージの作成 [ezpip]
with ezpip.packager(develop_dir = "./_develop_listupy/") as p:
	setup(
		name = "listupy",
		version = "0.1.0",
		description = "A tool that recursively enumerates Python files within a folder, calculates the total number of lines, and compiles them into a single Markdown text.",
		author = "bib_inf",
		author_email = "contact.bibinf@gmail.com",
		url = "https://github.co.jp/",
		packages = p.packages,
		install_requires = ["relpath", "ezpip", "sout", "fies"],
		long_description = p.long_description,
		long_description_content_type = "text/markdown",
		license = "CC0 v1.0",
		classifiers = [
			"Programming Language :: Python :: 3",
			"Topic :: Software Development :: Libraries",
			"License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication"
		],
		entry_points = """
			[console_scripts]
			listupy = listupy:console_command
		"""
	)
