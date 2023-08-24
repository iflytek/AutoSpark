import xmltodict
import xml.etree.ElementTree as ET
from utils import read_hierarchy
from config import run_config
class Hierarchy(object):
    """
    Hierarchy类，用于对hierarchy树进行处理和输出
    """

    def __init__(self, hierarchy_tree: str, specified_package_name=run_config['packge_name']):
        """
        初始化方法
        :param hierarchy_tree: 需要处理的hierarchy树
        :param specified_package_name: 指定包名，不属于该包名的节点将被删除
        """
        self.hierarchy_tree = hierarchy_tree
        self.specified_package_name = specified_package_name

    def declutter_hierarchy(self) -> str:
        """
        清理hierarchy树，删除无用节点
        :return: 清理后的hierarchy树
        """
        # 将xml格式的hierarchy树转换为dict格式
        hierarchy_dict = self.hierarchy_to_dict(self.hierarchy_tree)
        # 清理hierarchy树,将属性值为空的节点删除，将非指定包名的节点删除
        cleaned_tree = self.clean_hierarchy_tree(hierarchy_dict, self.specified_package_name)
        xml_tree_string = xmltodict.unparse(cleaned_tree, pretty=True)
        # 读取xml文件
        xml_tree_element = ET.fromstring(xml_tree_string)
        xml_tree_element_tree = ET.ElementTree(xml_tree_element)
        root = xml_tree_element_tree.getroot()
        # 删除不可点击的节点
        self._remove_attributes_with_can_not_click_values(root)
        modified_tree = ET.ElementTree(root)
        # 最终的hierarchy树
        xml_content = ET.tostring(modified_tree.getroot(), encoding="utf-8").decode("utf-8")
        print(xml_content)
        return xml_content


    def _clean_hierarchy(self, hierarchy_tree: dict,specified_package_name: str):
        """
        内部方法，清理hierarchy树，将属性值为空的节点删除，将非指定包名的节点删除
        :param hierarchy_tree: 转换为dict的hierarchy树
        :param specified_package_name: 指定的包名，不属于该包名的节点将被删除
        :return:
        """
        if isinstance(hierarchy_tree, dict):
            if '@package' in hierarchy_tree and hierarchy_tree['@package'] != specified_package_name:
                hierarchy_tree.clear()
                return
            for key in list(hierarchy_tree.keys()):
                # if key == '@package' and hierarchy[key] != 'com.huawei.appmarket':
                #     hierarchy.clear()
                #     return
                if hierarchy_tree[key] == '':
                    del hierarchy_tree[key]
                else:
                    self._clean_hierarchy(hierarchy_tree[key], specified_package_name)
        elif isinstance(hierarchy_tree, list):
            for item in hierarchy_tree:
                self._clean_hierarchy(item, specified_package_name)

    def clean_hierarchy_tree(self, hierarchy_tree: dict, specified_package_name:str) -> dict:
        """
        清理hierarchy树，将属性值为空的节点删除，将非指定包名的节点删除
        :param hierarchy_tree: 转换为dict的hierarchy树
        :param specified_package_name: 指定的包名，不属于该包名的节点将被删除
        :return: 处理后的hierarchy树
        """
        self._clean_hierarchy(hierarchy_tree,specified_package_name)
        return hierarchy_tree

    def hierarchy_to_dict(self, hierarchy_tree: str) -> dict:
        """
        将xml格式的hierarchy树转换为dict格式
        :param hierarchy_tree: xml格式的hierarchy
        :return: dict格式的hierarchy
        """
        tree_dict = xmltodict.parse(hierarchy_tree)
        print(tree_dict)
        return tree_dict

    def _remove_attributes_with_can_not_click_values(self, element_tree):
        """
        删除不可点击的节点
        :param element_tree: xml节点对象
        :return:
        """
        if "checkable" in element_tree.attrib and "clickable" in element_tree.attrib:
            if element_tree.attrib["checkable"] == "false" and element_tree.attrib["clickable"] == "false":
                element_tree.attrib.clear()

        for child in element_tree:
            self._remove_attributes_with_can_not_click_values(child)




if __name__ == '__main__':
    # from actions import Actions
    # act = Actions()
    tree = read_hierarchy("test")
    h = Hierarchy(tree, "com.huawei.appmarket")
    h.declutter_hierarchy()
    # res = h.hierarchy_to_dict(tree)
    # remove_res = h.process_hierarchy_tree(res)
    # print(remove_res)
    # xml = xmltodict.unparse(remove_res, pretty=True)
    # # print(xml)
    # # with open("test.xml", "w", encoding="utf-8") as f:
    # #     f.write(xml)
    # import xml.etree.ElementTree as ET
    #
    # # 读取xml文件
    # tree = ET.fromstring(xml)
    # tree = ET.ElementTree(tree)
    # root = tree.getroot()
    # for c in list(root):
    #     print(c.tag)
    # h.remove_attributes_with_false_values(root)
    #
    # modified_tree = ET.ElementTree(root)
    # xml_content = ET.tostring(modified_tree.getroot(), encoding="utf-8").decode("utf-8")
    # print(xml_content)
    # modified_tree.write("output.xml", encoding="utf-8", xml_declaration=True)
