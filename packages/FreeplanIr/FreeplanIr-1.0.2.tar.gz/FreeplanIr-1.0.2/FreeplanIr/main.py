# coding=utf-8

from typing import List
import xml.etree.ElementTree as Et
from xml.etree.ElementTree import Element
import xlsxwriter


class FreeplanIr:

    def __init__(self, file_path: str) -> None:
        self._max_num: int = 0
        self._count: int = 1
        self.file_path = file_path
        self._open()

    def _open(self) -> None:
        mind_map = Et.parse(self.file_path)
        self.root = mind_map.getroot()

    def plan_test(self) -> List[List[str]]:
        data_list = []

        def traverse_nodes(node: Element, data: List[str]):
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

    def chage_list(self, data_list: List[List[str]], number: int) -> List[List[str]]:
        for i in range(len(data_list)):
            current_list = data_list[i]
            for j in range(i + 1, len(data_list)):
                next_list = data_list[j]
                for k in range(number):
                    if current_list[k] == next_list[k]:
                        next_list[k] = ''
        # for i in range(len(data_list)):
        #     current_list = data_list[i]
        #     if i == len(data_list) - 1:
        #         break
        #     next_list = data_list[i+1]
        #     for k in range(len(current_list)):
        #         if current_list[k] == next_list[k]:
        #             next_list[k] = ''

        return data_list

    def download(self) -> str:
        title = ["项目名称", "模块", "功能点", "用例名称", "前置条件", "测试步骤", "预期输出", "实际输出", "测试结果"]
        title1 = ["项目名称", "模块", "子模块", "功能点", "用例名称", "前置条件", "测试步骤", "预期输出", "实际输出",
                  "测试结果"]
        number = 4
        xlsx_path = self.file_path.replace(".mm", ".xlsx")
        write_worke = xlsxwriter.Workbook(xlsx_path)
        writesheet = write_worke.add_worksheet()
        data_list = self.plan_test()
        write_title: List = []
        if len(data_list[0]) == 7:
            number = 4
            write_title = title
        elif len(data_list[0]) == 8:
            write_title = title1
            number = 5
        data_list = self.chage_list(data_list, number)
        for ids, title_write in enumerate(write_title):
            writesheet.write(0, ids, title_write)
        row = 1
        for datas in data_list:
            for index in range(len(datas)):
                writesheet.write(row, index, datas[index])
            row += 1
        write_worke.close()
        return xlsx_path


if __name__ == '__main__':
    file_path = r"E:\项目文件\社区电商一起\RMS系统\v2.1轨迹\RMS轨迹测试用例.mm"
    test_plan = FreeplanIr(file_path)
    datas = test_plan.download()
    print(datas)