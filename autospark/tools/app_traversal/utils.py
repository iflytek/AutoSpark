import os

import mistune


def read_prompt(prompt_name: str, prompt_path="./prompts") -> str:
    """
    读取prompt文件的内容
    :param prompt_name: 模板名称
    :param prompt_path: 模板路径
    :return: 读取内容
    """
    with open(f"{prompt_path}/{prompt_name}.pmp", "r", encoding="utf-8") as f:
        return f.read()


def read_hierarchy(hierarchy_name: str, hierarchy_path="./hierarchys") -> str:
    """
    读取hierarchy文件的内容
    :param hierarchy_name: 文件名称
    :param hierarchy_path: 路径
    :return:读取的内容
    """
    with open(f"{hierarchy_path}/{hierarchy_name}.txt", "r", encoding="utf-8") as f:
        return f.read()


def get_md_code(md_string) -> list:
    """
    从markdown格式的字符串中提取出代码节点的内容，返回代码字符串
    :param md_string: str, markdown格式的字符串
    :return: list, 每个代码节点的字符串内容列表
    """

    class CodeExtractorRenderer(mistune.Renderer):
        def __init__(self):
            super().__init__()
            self.code_blocks = []

        def block_code(self, code, lang):
            self.code_blocks.append(code)
            return ""

    renderer = CodeExtractorRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    markdown(md_string)

    # for idx, code_block in enumerate(renderer.code_blocks, start=1):
    #     print(f"Code block {idx}:")
    #     print(code_block)
    #     print()
    print("代码块列表如下：")
    print(renderer.code_blocks)
    return renderer.code_blocks


def get_newest_file_info(directory) -> tuple:
    """
    获取指定目录下最新的文件信息
    :param directory:
    :return:
    """
    files = os.listdir(directory)
    operation_files = [f for f in files if f.startswith("operation_") and f.endswith(".txt")]

    if not operation_files:
        return None, None

    def get_file_mtime(filename):
        filepath = os.path.join(directory, filename)
        return os.path.getmtime(filepath)

    sorted_files = sorted(operation_files, key=get_file_mtime, reverse=True)
    newest_file_name = sorted_files[0]
    newest_file_path = os.path.abspath(os.path.join(directory, newest_file_name))
    return newest_file_name, newest_file_path
