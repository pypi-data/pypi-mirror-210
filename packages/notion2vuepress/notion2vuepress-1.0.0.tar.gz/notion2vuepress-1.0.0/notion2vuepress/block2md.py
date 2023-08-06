import os
from abc import abstractmethod, ABCMeta

import requests

from notion2vuepress.file_io_context import FileContext
from notion2vuepress.notion import Notion
from notion2vuepress.utils import create_file_folder, random_name

IMG_FOLDER = 'assets'


class Block2Md(Notion):

    def __init__(self, blocks):
        super().__init__()
        for block in blocks:
            pass

    def conversion(self, money):
        pass

    class Header:
        pass

    def sub_header(self):
        pass

    def sub_sub_header(self):
        pass


# 抽象产品角色（Product）
class BlockConversion(metaclass=ABCMeta):

    @abstractmethod
    def conversion(self):
        pass

    def __repr__(self):
        pass

    @staticmethod
    def link(name, url):
        return "[" + name + "]" + "(" + url + ")"


class Header(BlockConversion):
    """header"""

    def __init__(self, block):
        self.block = block
        self.conversion()

    def conversion(self):
        # vuepress 从二级标题开始
        self.block = "## " + self.block

    def __repr__(self):
        return self.block


class SubHeader(BlockConversion):
    """sub_header"""

    def __init__(self, block):
        self.block = block
        self.conversion()

    def conversion(self):
        self.block = "### " + self.block

    def __repr__(self):
        return self.block


class SubSubHeader(BlockConversion):
    """sub_sub_header"""

    def __init__(self, block):
        self.block = block
        self.conversion()

    def conversion(self):
        self.block = "#### " + self.block

    def __repr__(self):
        return self.block


class Page(BlockConversion):
    """page"""

    def __init__(self, block, icon):
        self.block = block
        self.icon = icon
        self.conversion()

    def conversion(self):
        try:
            if "https:" in self.icon:
                self.icon = "!" + self.link("", self.icon)
            self.block = "# " + self.icon + self.block
        except:
            self.block = "# " + self.block

    def __repr__(self):
        return self.block


class Text(BlockConversion):
    """text"""

    def __init__(self, block):
        self.block = block
        self.conversion()

    def conversion(self):
        self.block = self.block + "  "

    def __repr__(self):
        return self.block


class Bookmark(BlockConversion):
    """bookmark"""

    def __init__(self, block, link):
        self.block = block
        self.link = link
        self.conversion()

    def conversion(self):
        self.block = self.link(self.block, self.link)

    def __repr__(self):
        return self.block


class Video(BlockConversion):
    """video"""

    def __init__(self, block, source):
        self.block = block
        self.source = source
        self.conversion()

    def conversion(self):
        self.block = self.link(self.block, self.source)

    def __repr__(self):
        return self.block


class File(BlockConversion):
    """file/audio/pdf/gist"""

    def __init__(self, block, source):
        self.block = block
        self.source = source
        self.conversion()

    def conversion(self):
        self.block = self.link(self.block, self.source)

    def __repr__(self):
        return self.block


class BulletedList(BlockConversion):
    """bulleted_list/toggle"""

    def __init__(self, block):
        self.block = block
        self.conversion()

    def conversion(self):
        self.block = '- ' + self.block

    def __repr__(self):
        return self.block


class NumberedList(BlockConversion):
    """numbered_list"""

    def __init__(self, block, number_idx):
        self.block = block
        self.number_idx = number_idx
        self.conversion()

    def conversion(self):
        self.block = str(self.number_idx) + '. ' + self.block

    def __repr__(self):
        return self.block


class Image(BlockConversion):
    """image"""

    def __init__(self, source, directory, img_token):
        self.block = ""
        self.source = source
        self.directory = directory
        self.img_token = img_token
        self.conversion()

    def conversion(self):
        directory = os.path.join(self.directory, IMG_FOLDER)
        create_file_folder(directory)
        file_name = f'{random_name()}.png'

        img_dir = os.path.join(directory, file_name)
        headers = {
            'Cookie': f'file_token={self.img_token}',
        }
        r = requests.get(self.source, allow_redirects=True, headers=headers)
        with FileContext(img_dir, "wb") as f:
            f.write(r.content)
        self.block = "!" + self.link("", f'./assets/{file_name}')

    def __repr__(self):
        return self.block

# elif btype == "code":
# md += "```" + block.language + "\n" + block.title + "\n```"
# elif btype == "equation":
# md += "$$" + block.latex + "$$"
# elif btype == "divider":
# md += "---"
# elif btype == "to_do":
# if block.checked:
#     md += "- [x] " + bt
# else:
#     md += "- [ ]" + bt
# elif btype == "quote":
# md += "> " + bt
# elif btype == "column" or btype == "column_list":
# continue
# else:
# pass
# md += "\n\n"

class Code(BlockConversion):
    """code"""

    def __init__(self, source, directory, img_token):
        self.block = ""
        self.source = source
        self.directory = directory
        self.img_token = img_token
        self.conversion()

    def conversion(self):
        directory = os.path.join(self.directory, IMG_FOLDER)
        create_file_folder(directory)
        file_name = f'{random_name()}.png'

        img_dir = os.path.join(directory, file_name)
        headers = {
            'Cookie': f'file_token={self.img_token}',
        }
        r = requests.get(self.source, allow_redirects=True, headers=headers)
        with FileContext(img_dir, "wb") as f:
            f.write(r.content)
        self.block = "!" + self.link("", f'./assets/{file_name}')

    def __repr__(self):
        return self.block
