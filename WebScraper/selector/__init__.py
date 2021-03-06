#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/4/17 9:07 AM
# @Author  : mirko
# @FileName: __init__.py.py
# @Software: PyCharm


from lxml.cssselect import CSSSelector
from pyquery import PyQuery as pq

class RegisterSelectorType(object):

    selector_type = {}

    def __init__(self, type):
        self._type = type

    def __call__(self, cls, *args, **kwargs):

        if not self.selector_type.__contains__(self._type):
            self.selector_type[self._type] = cls

        return cls


class SelectorFactory(object):

    __selector_type = RegisterSelectorType.selector_type

    @classmethod
    def create_selector(cls, type):

        if cls.__selector_type.__contains__(type):
            return cls.__selector_type[type]
        else:
            raise NotImplementedError()

    @classmethod
    def bulid_selector_tree(cls, _json_selectors):
        """
        构筑一棵json字符串表示的selector tree
        :param _json_selectors:
        :return: 各种selector实例组成的selector tree,根节点为root
        """
        #root_selector = Selector('_root', 'SelectorElement', None, None)

        root_selector = SelectorFactory.create_selector("SelectorElement").from_settings({"multiple": False, "id": "_root", "css_paths": "html"})

        def build(p_selector, selectors, created_selector):
            parent_selector_id = p_selector.id   #拿到父节点的id

            for selector in selectors:
                if parent_selector_id in selector.get("parent_selectors"):
                    current_selector_id = selector.get("id")  # 拿到当前节点的id

                    if current_selector_id in created_selector.keys():
                        child_selector = created_selector[current_selector_id]
                        p_selector.add_child(child_selector)
                    else:
                        child_selector_class = SelectorFactory.create_selector(selector.get("type"))
                        if child_selector_class:
                            new_selector = child_selector_class.from_settings(selector)
                            child_selector = build(new_selector, selectors, created_selector)
                            p_selector.add_child(child_selector)
                            created_selector[current_selector_id] = child_selector
                        else:
                            #TODO Selecotr工厂中找不到该类型selector时的分支判断
                            pass
            return p_selector

        return build(root_selector, _json_selectors, {})

class Selector(object):
    can_return_multiple_records = False     #能否返回多条记录
    can_have_child_selectors = False        #能有拥有孩子节点
    can_have_local_child_selectors = False  #能否在当前页面拥有孩子节点
    can_create_new_jobs = False             #能否产生新的任务
    can_return_elements = False             #返回元素

    features = {
        'id': '',
        'type': None,
        'css_paths': '',
        'parent_selectors': []
    }

    @classmethod
    def get_features(cls):
        return cls.features.copy()

    @classmethod
    def from_settings(cls, settings):
        #取得每个selecotr的特征值列表
        features = cls.get_features()

        #对于features不存在，settings中存在的值，删去
        for key in list(settings.keys()):
            if key not in features.keys():
                del settings[key]

        #对于features存在，但settings不存在的值，赋予默认值
        for key, value in features.items():
            if key not in settings.keys():
                settings[key] = value

        #生成实例
        selector = cls(**settings)

        return selector

    def __init__(self, id, type, css_paths, parent_selectors, **kwargs):
        """
        :param id:
        :param type:
        :param css_paths:
        :param parent_selectors:
        :param kwargs:
        """
        self.id = id
        self.type = type
        self.css_paths = css_paths
        self.parent_selectors = parent_selectors
        self.children = []

    def add_child(self, selector):
        if self.children:
            self.children.append(selector)
        else:
            self.children = [selector, ]

    def will_return_multiple_records(self):
        raise NotImplementedError()


    def get_data(self, parentElement):

        #TODO 考虑在未来加入延时，控制selector的抽取速度
        return self.get_specific_data(parentElement)



    def get_data_elements(self, parentElement):
        elements = ElementQuery(self.css_paths, parentElement).execute()

        if self.will_return_multiple_records():
            return elements
        else:
            return elements[:1] if elements else []

    def get_specific_data(self, element):
        raise NotImplementedError()



class ElementQuery(object):

    def __init__(self, cssselector, parentElement):
        self.cssselector = cssselector if cssselector else ""
        self.parentElement = parentElement
        self.selectedElements = list()

    def getSelectorParts(self):
        resultSelectors = []
        currentSelector = ""

        regEx = r"(,|\".*?\"|\'.*?\'|\(.*?\))"
        cssPaths = self.cssselector.split(regEx)
        for css in cssPaths:
            if css == ",":
                if currentSelector.strip().__len__() > 0:
                    resultSelectors.append(currentSelector)
                else:
                    currentSelector = ""
            else:
                currentSelector += css
        if currentSelector.strip().__len__() > 0:
            resultSelectors.append(currentSelector)

        return resultSelectors

    def execute(self):
        selectorParts = self.getSelectorParts()
        #html = pq(self.parentElement)

        for selector in selectorParts:
            elements = pq(self.parentElement)(selector)
            for item in elements:
                if item not in self.selectedElements:
                    self.selectedElements.append(item)

        return self.selectedElements