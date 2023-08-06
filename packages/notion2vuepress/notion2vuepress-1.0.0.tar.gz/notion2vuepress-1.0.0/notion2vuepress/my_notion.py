from notion.client import NotionClient


class Notion():
    def __init__(self, _token):
        self.__token = _token
        self.__client = NotionClient(token_v2=self.__token)

    def get_page_obj(self, page_id):
        return self.__client.get_block(page_id)

    def get_block(self, block_id):
        """获取单个块"""
        return self.__client.get_block(block_id)

    def recursive_get_blocks(self, block, blocks):
        new_id = self.get_block(block.id)
        if not (new_id in blocks):
            blocks.append(new_id)
            try:
                for children_id in block.get("content"):
                    children = self.get_block(children_id)
                    if children.type != "page":
                        self.recursive_get_blocks(children, blocks)
            except:
                return

    def children_exists(self, page_id):
        page = self.get_page_obj(page_id)
        """校验是否存在子页面"""
        for child in page.children:
            if child.type == "page":
                return True

        return False
