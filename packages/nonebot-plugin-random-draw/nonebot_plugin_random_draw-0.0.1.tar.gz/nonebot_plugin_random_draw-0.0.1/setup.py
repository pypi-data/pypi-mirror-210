# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_random_draw']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.1.3,<3.0.0', 'nonebot2>=2.0.0b5,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-random-draw',
    'version': '0.0.1',
    'description': '通过添加各种想要抽取的内容，最后进行随机抽取。',
    'long_description': '<div align="center">\n  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>\n  <br>\n  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>\n</div>\n\n<div align="center">\n\n# nonebot_plugin_random_draw\n\n_✨ NoneBot 随机抽取设定内容 插件 ✨_\n\n\n<a href="https://github.com/Ikaros-521/nonebot_plugin_random_draw/stargazers">\n    <img alt="GitHub stars" src="https://img.shields.io/github/stars/Ikaros-521/nonebot_plugin_random_draw?color=%09%2300BFFF&style=flat-square">\n</a>\n<a href="https://github.com/Ikaros-521/nonebot_plugin_random_draw/issues">\n    <img alt="GitHub issues" src="https://img.shields.io/github/issues/Ikaros-521/nonebot_plugin_random_draw?color=Emerald%20green&style=flat-square">\n</a>\n<a href="https://github.com/Ikaros-521/nonebot_plugin_random_draw/network">\n    <img alt="GitHub forks" src="https://img.shields.io/github/forks/Ikaros-521/nonebot_plugin_random_draw?color=%2300BFFF&style=flat-square">\n</a>\n<a href="./LICENSE">\n    <img src="https://img.shields.io/github/license/Ikaros-521/nonebot_plugin_random_draw.svg" alt="license">\n</a>\n<a href="https://pypi.python.org/pypi/nonebot_plugin_random_draw">\n    <img src="https://img.shields.io/pypi/v/nonebot_plugin_random_draw.svg" alt="pypi">\n</a>\n<a href="https://www.python.org">\n    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">\n</a>\n\n</div>\n\n## 📖 介绍\n\n通过添加各种想要抽取的内容，最后进行随机抽取。  \n\n## 🔧 开发环境\nNonebot2：2.0.0rc3  \npython：3.8.13  \n操作系统：Windows10（Linux兼容性问题不大）  \n编辑器：VS Code  \n\n## 💿 安装  \n\n### 1. nb-cli安装\n\n在你bot工程的文件夹下，运行cmd（运行路径要对啊），执行nb命令安装插件，插件配置会自动添加至配置文件  \n```\nnb plugin install nonebot_plugin_random_draw\n```\n\n### 2. 本地安装\n\n将项目clone到你的机器人插件下的对应插件目录内（一般为机器人文件夹下的`src/plugins`），然后把`nonebot_plugin_random_draw`文件夹里的内容拷贝至上一级目录即可。  \nclone命令参考（得先装`git`，懂的都懂）：\n```\ngit clone https://github.com/Ikaros-521/nonebot_plugin_random_draw.git\n``` \n也可以直接下载压缩包到插件目录解压，然后同样提取`nonebot_plugin_random_draw`至上一级目录。  \n目录结构： ```你的bot/src/plugins/nonebot_plugin_random_draw/__init__.py```  \n\n\n### 3. pip安装\n```\npip install nonebot_plugin_random_draw\n```  \n打开 nonebot2 项目的 ```bot.py``` 文件, 在其中写入  \n```nonebot.load_plugin(\'nonebot_plugin_random_draw\')```  \n当然，如果是默认nb-cli创建的nonebot2的话，在bot路径```pyproject.toml```的```[tool.nonebot]```的```plugins```中添加```nonebot_plugin_random_draw```即可  \npyproject.toml配置例如：  \n``` \n[tool.nonebot]\nplugin_dirs = ["src/plugins"]\nplugins = ["nonebot_plugin_random_draw"]\n``` \n\n\n## 🔧 配置\n\n\n## 🎉 功能\n  \n\n## 👉 命令\n\n### /随机抽取帮助\n命令结构：```/随机抽取帮助```  \n例如：```/随机抽取帮助```  \n功能：返回所有命令的使用方式。  \nbot返回内容：  \n```\n功能说明：命令列表（命令前缀自行匹配）\n获取帮助：随机抽取帮助\n创建随抽组，一个群可以有多个组：随抽组创建 <组名>\n往指定的随抽组中添加待抽内容：随抽添加 <组号> <内容>\n删除指定随抽组中的待抽内容：随抽删除 <组号> <内容>\n删除指定组号的随抽组：随抽组删除 <组号>\n查看本群所有的随抽组内容（含组号和组名）：随抽组列表\n查看指定组号的所有待抽内容：随抽列表 <组号>\n在指定随抽组中随机抽取一个待抽内容：随抽 <组号>\n清空本群中所有的随抽组（慎用）：随抽组清空\n清空指定随抽组中所有的待抽内容（慎用）：随抽清空 <组号>\n```\n\n### 其他命令懒得写了，直接看图吧\n![](docs/result.png)\n\n## ⚙ 拓展\n \n\n## 📝 更新日志\n\n<details>\n<summary>展开/收起</summary>\n\n### 0.0.1\n\n- 插件初次发布  \n\n</details>\n\n## 致谢\n- [nonebot-plugin-template](https://github.com/A-kirami/nonebot-plugin-template)\n\n## 项目打包上传至pypi\n\n官网：https://pypi.org，注册账号，在系统用户根目录下创建`.pypirc`，配置  \n``` \n[distutils] \nindex-servers=pypi \n \n[pypi] repository = https://upload.pypi.org/legacy/ \nusername = 用户名 \npassword = 密码\n```\n\n### poetry\n\n```\n# 参考 https://www.freesion.com/article/58051228882/\n# poetry config pypi-token.pypi\n\n# 1、安装poetry\npip install poetry\n\n# 2、初始化配置文件（根据提示填写）\npoetry init\n\n# 3、微调配置文件pyproject.toml\n\n# 4、运行 poetry install, 可生成 “poetry.lock” 文件（可跳过）\npoetry install\n\n# 5、编译，生成dist\npoetry build\n\n# 6、发布(poetry config pypi-token.pypi 配置token)\npoetry publish\n\n```\n\n### twine\n\n```\n# 参考 https://www.cnblogs.com/danhuai/p/14915042.html\n#创建setup.py文件 填写相关信息\n\n# 1、可以先升级打包工具\npip install --upgrade setuptools wheel twine\n\n# 2、打包\npython setup.py sdist bdist_wheel\n\n# 3、可以先检查一下包\ntwine check dist/*\n\n# 4、上传包到pypi（需输入用户名、密码）\ntwine upload dist/*\n```\n',
    'author': 'Ikaros',
    'author_email': '327209194@qq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Ikaros-521/nonebot_plugin_random_draw',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
