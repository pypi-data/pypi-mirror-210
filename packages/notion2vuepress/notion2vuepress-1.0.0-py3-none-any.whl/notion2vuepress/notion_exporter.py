import os

import requests

from notion2vuepress import Notion, FileContext, random_name


class NotionExporter(Notion):
    def __init__(self, _token, img_token):
        super().__init__(_token)
        self.img_token = img_token

    def link(self, name, url):
        return "[" + name + "]" + "(" + url + ")"

    def image_export(self, url, directory):
        directory = os.path.join(directory, 'assets')
        self.create_file_folder(directory)

        img_name = f'{random_name()}.png'
        img_dir = os.path.join(directory, img_name)
        headers = {
            'Cookie': f'file_token={self.img_token}',
        }
        r = requests.get(url, allow_redirects=True, headers=headers)

        with FileContext(img_dir, "wb", ) as f:
            f.write(r.content)

        return f'./assets/{img_name}'

    def block2md(self, blocks, file_path):
        md = ""
        numbered_list_index = 0
        for block in blocks:

            try:
                btype = block.type
            except:
                continue

            if btype != "numbered_list":
                numbered_list_index = 0

            try:
                bt = str(block.title).replace("*", "")
            except:
                bt = ""

            # vuepress 从二级标题开始，所以每个标题加一个#
            if btype == 'header':
                md += "## " + bt
            elif btype == "sub_header":
                md += "### " + bt
            elif btype == "sub_sub_header":
                md += "#### " + bt
            elif btype == 'page':
                try:
                    if "https:" in block.icon:
                        icon = "!" + self.link("", block.icon)
                    else:
                        icon = block.icon
                    md += "# " + icon + bt
                except:
                    md += "# " + bt
            elif btype == 'text':
                md += bt + "  "
            elif btype == 'bookmark':
                md += self.link(bt, block.link)
            elif btype == "video" or btype == "file" or btype == "audio" or btype == "pdf" or btype == "gist":
                md += self.link(block.source, block.source)
            elif btype == "bulleted_list" or btype == "toggle":
                md += '- ' + bt
            elif btype == "numbered_list":
                numbered_list_index += 1
                md += str(numbered_list_index) + '. ' + bt
            elif btype == "image":

                try:
                    img_url = self.image_export(block.source, file_path)
                    md += "!" + self.link("", img_url)
                except:
                    pass

            elif btype == "code":
                md += "```" + block.language + "\n" + block.title + "\n```"
            elif btype == "equation":
                md += "$$" + block.latex + "$$"
            elif btype == "divider":
                md += "---"
            elif btype == "to_do":
                if block.checked:
                    md += "- [x] " + bt
                else:
                    md += "- [ ]" + bt
            elif btype == "quote":
                md += "> " + bt
            elif btype == "column" or btype == "column_list":
                continue
            else:
                pass
            md += "\n\n"
        return md

    def export_cli(self, file_name, page_obj):
        print(f"{file_name}-正则导出文件{page_obj.title}")

        with FileContext(file_name, "w", encoding="utf-8") as f:
            blocks = list()
            self.recursive_get_blocks(page_obj, blocks)
            parent_dir = os.path.dirname(file_name)
            f.write(self.block2md(blocks, parent_dir))

    @staticmethod
    def modify_title(title):
        return title.replace("*", "").replace("_", "").replace("/", "-")

    def export_to_markdown(self, page_id, file_path):
        # 获取页面对象
        page_obj = self.get_page_obj(page_id)
        file_path = os.path.join(file_path, f"{self.modify_title(page_obj.title)}")

        self.export_cli(f"{file_path}.md", page_obj)
        if not self.children_exists(page_id):
            return

        # 创建文件夹，同时创建文件
        self.create_file_folder(file_path)
        for idx, page_child_obj in enumerate(page_obj.children):
            if page_child_obj.type == "page":
                self.export_to_markdown(page_child_obj.id, file_path)

    def create_file_folder(self, directory):
        """判断文件夹是否存在，如果不存在则创建"""
        if not os.path.exists(directory):
            os.makedirs(directory)
