# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['markdownparser']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'markdownparser',
    'version': '0.4.2',
    'description': '',
    'long_description': '# MarkdownParser\n\n[![codecov](https://codecov.io/gh/luzhixing12345/MarkdownParser/branch/main/graph/badge.svg?)](https://codecov.io/gh/luzhixing12345/MarkdownParser)\n\nMarkdownParser 是一个 Markdown 语法解析器,用于实现md到html标签的转换\n\n## 安装\n\n```bash\npip install markdownparser\n```\n\n## 快速使用\n\n```python\nimport MarkdownParser\n\nhtml = MarkdownParser.parse(\'# Hello World!\')\nprint(html)\n\n#<div class=\'markdown-body\'><h1>Hello World!</h1></div>\n```\n\n接口函数\n\n```python\n# 解析markdown text\ndef parse(text: str) -> str:\n\n# 解析markdown 文件\ndef parseFile(file_name: str) -> str:\n\n# 见下方补充说明\ndef parse_withtag(text: str) -> str:\n\ndef parseFile_withtag(file_name: str) -> str:\n```\n\n第二个参数为可选项, `has_tag` 表示是否将\n\n## 测试\n\n```bash\npython generate.py <FILE_NAME>\n\n# python generate.py ./testfiles/test1.md\n# python generate.py README.md\n```\n\n运行会生成index.html, 使用浏览器打开生成的index.html即可与您的Markdown编辑器的预期渲染结果对比\n\n![20230218202400](https://raw.githubusercontent.com/learner-lu/picbed/master/20230218202400.png)\n\n代码覆盖率\n\n```bash\npip install coverage\n\ncoverage run -m unittest\ncoverage html\n```\n\n## 实现思路\n\n[Markdown解析器的代码实现](https://www.bilibili.com/video/BV1LA411X7X3)\n\n您可通过取消 [core.py](./MarkdownParser/core.py) 注释来获取树的结构\n\n```python\ndef parse(self, text: str) -> str:\n\n    # 去除空行/注释/html标签\n    lines = self.preprocess_parser(text)\n    # print(lines)\n    # 逐行解析,得到一颗未优化的树\n    root = self.block_parser(lines)\n    # root.info()\n    # 优化,得到正确的markdown解析树\n    tree = self.tree_parser(root)\n    # tree.info()\n    # 输出到屏幕 / 导出html文件\n    return tree.toHTML()\n```\n\n## 不支持\n\n- 四个空格变为代码段\n- [^1]的引用方式\n- Setext 形式的标题\n- 上标 / 下标 / 下划线\n\n## 补充说明\n\n- 生成的结果如下 `<div class=\'markdown-body\'>markdown内容</div>`\n- 代码段会根据语言加入一个类名便于后期高亮,例如 `class="language-cpp"`, 未定义语言则为 `language-UNKNOWN`\n- 默认导出的HTML中层级任务列表会有显示问题,这是因为使用了ul+li+checkbox的方式,您需要添加以下css样式修正\n\n  ```css\n  .markdown-body > ul>li:has(input) {\n    padding-left: 0;\n    margin-bottom: 0;\n  }\n\n  .markdown-body  ul>li:has(input)>ul {\n    list-style-type: none;\n    padding-left: 8px;\n  }\n  ```\n\n- 您可以使用 `parse_withtag` 将 HashHeadBlock 提取出来组成目录树, 得到一个 `<div class="header-navigator">...</div>` 并添加到返回的 HTML 元素中, 您可能还需要一些 js 相关的代码实现跳转, 具体可以参考 [template.html](./template.html)\n\n  ```js\n  let links = document.querySelectorAll(\'div a[href^="#"]\');\n    links.forEach(link => {\n      link.addEventListener(\'click\', function(event) {\n        event.preventDefault();\n        let target = document.querySelector(this.getAttribute(\'href\'));\n        target.scrollIntoView({ behavior: \'smooth\' });\n      });\n    });\n  ```\n\n  以及一些样式美化\n\n  ```css\n  .header-navigator {\n    position: fixed;\n  }\n  ```\n\n- 如果您想添加对[Mermaid](https://mermaid.js.org/)的支持, 您可参考[mermaid plugin](https://mermaid.js.org/intro/n00b-gettingStarted.html#_2-using-mermaid-plugins)在您的html页面 `<body>` 末尾添加如下 `<script>`\n\n  ```html\n  <script type="module">\n    const codeBlocks = document.querySelectorAll(\'.language-mermaid\');\n    codeBlocks.forEach(codeBlock => {\n        codeBlock.classList.remove(\'language-mermaid\');\n        codeBlock.classList.add(\'mermaid\');\n    });\n    import mermaid from \'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs\';\n    mermaid.initialize({ startOnLoad: true });\n  </script>\n  ```\n\n  > **请注意**, 由于本Markdown解析器的CodeBlock解析得到的类名为 `language-mermaid`, 而mermaid插件支持的类名格式为`mermaid`, 所以代码中手动修改了 `language-mermaid` 的类名\n\n- 如果您想添加对Latex数学公式的支持, 可以在html页面 `<body>` 末尾添加如下 `<script>`\n\n  ```html\n  <script>\n      MathJax = {\n        tex: {\n          inlineMath: [[\'$\', \'$\'], [\'\\\\(\', \'\\\\)\']]\n        }\n      };\n      </script>\n  <script id="MathJax-script" async\n  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">\n  </script>\n  ```\n\n  注意,这里仅支持很少一部分数学公式\n\n\n## 相关参考\n\n- [Github Markdown CSS](https://cdn.jsdelivr.net/npm/github-markdown-css@4.0.0/github-markdown.css)\n- [Mermaid API](https://mermaid.js.org/intro/#mermaid-api)\n- [MathJax](https://docs.mathjax.org/en/latest/web/start.html)',
    'author': 'luzhixing12345',
    'author_email': 'luzhixing12345@163.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/luzhixing12345/MarkdownParser',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
