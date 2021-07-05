import os
from bs4 import BeautifulSoup
import lxml


class AuroraReader:
    def __init__(self):
        os.chdir('..')
        os.chdir('custom')
        self.full_data = []
        for folder, subs, files in os.walk(os.path.abspath(os.curdir)):
            files = [fi for fi in files if fi.endswith(".xml")]
            for filename in files:
                with open(os.path.join(folder, filename), 'r', encoding='utf8') as f:
                    data = f.read()
                    bs_data = BeautifulSoup(data, 'xml')
                    self.full_data.append(bs_data)
        os.chdir('..')
        os.chdir('Character sheet converter')

    def full_data_find(self, to_find):
        list = []
        for data in self.full_data:
            list.extend(data.find_all("elements"))
        for data in list:
            result = data.find("element", to_find)
            if result is not None:
                return result
        return None

    def full_data_find_all(self, to_find):
        result_list = []
        list = []
        for data in self.full_data:
            list.extend(data.find_all("elements"))
        for data in list:
            result = data.find("element", to_find)
            if result is not None:
                result_list.append(result)
        return result_list
