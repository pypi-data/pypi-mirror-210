## notion2vuepress

notion2vuepress is a Python package that seamlessly converts Notion notes (including text, images, and formatting) into VuePress-compatible Markdown files. Effortlessly migrate concept-based documents or blogs to a VuePress powered website while preserving structure and style. Simplify your workflow and enhance publishing capabilities.

## 提示

目前只是初步的实现，尽情期待后面的封装以及自动化的过程

### 大致架构图

![](./img/4.png)

## 获取token_v2

1. F12进入开发者模式
2. ![](./img/1.png)

## 获取图片的token

如果图片保存在notion上用到

得到一直图片连接访问即可

![](./img/2.png)

## 获取文章的id(page_id)

![](./img/3.png)

https://www.notion.so/youyizhang/git-9cad24555c3648b1a902333128bf1a0d?pvs=4

id = 9cad24555c3648b1a902333128bf1a0d



## 运行的时候报错需要重新装包 notion-cobertos-fork

```
1. pip uninstall notion-cobertos-fork
2. pip install notion-cobertos-fork
```

