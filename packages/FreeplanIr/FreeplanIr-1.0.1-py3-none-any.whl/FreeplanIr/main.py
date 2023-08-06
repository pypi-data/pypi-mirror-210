# coding=utf-8

from typing import List
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


class FreeplanIr:
    def __init__(self, file_path: str) -> None:
        self._max_num: int = 0
        self._count: int = 1
        self.file_path = file_path
        self._open()

    def _open(self) -> None:
        mind_map = ET.parse(self.file_path)
        self.root = mind_map.getroot()

    def plan_test(self) -> List[List[str]]:
        data_list = []

        def traverse_nodes(node: Element, data:List[str]):
            data.append(node.get('TEXT'))
            for child_node in node.findall('node'):
                self._count += 1
                if self._count > self._max_num:
                    self._max_num = self._count
                traverse_nodes(child_node, data.copy())
                

            if len(data) == self._max_num:
                data_list.append(data)
                self._count = 0
        
        for node in self.root.findall('node'):
            traverse_nodes(node, [])

        return data_list



if __name__ == '__main__':
    file_path = r"XXXX.mm"
    test_plan = FreeplanIr(file_path)
    datas = test_plan.plan_test()
    print(datas)