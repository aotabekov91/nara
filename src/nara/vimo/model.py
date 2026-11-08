import re
from collections import OrderedDict

from .object import Object
from .element import Element

class Model(Object):

    wantView = []
    pattern = None
    isLoaded = False
    wantUniqView = False
    element_class = Element

    def __init__(
        self,
        index=None,
        source=None,
        render=None,
        elements=OrderedDict(),
        **kwargs,
    ):
        self.m_id = index
        self.m_data = None
        self.m_loaded = False
        self.m_source = source
        self.m_render = render
        self.m_base_model = None
        self.m_elements = elements.copy()
        super().__init__(**kwargs)

    def count(self):
        return len(self.m_elements)

    def readSuccess(self):
        return self.m_data is not None

    def modelData(self):
        return self.m_data

    def id(self):
        return self.m_id

    def setId(self, idx):
        self.m_id = idx

    def element(self, idx):
        return self.m_elements.get(idx, None)

    def elements(self):
        return self.m_elements

    def setElements(self, elements):
        self.m_elements = elements

    def __eq__(self, o):
        return o and id(self) == id(o)

    def __hash__(self):
        return id(self) 

    def source(self):
        return self.m_source

    def load(self):
        self.isLoaded = True

    @classmethod
    def isCompatible(cls, s, **kwargs):
        if type(s) != str:
            return
        if not cls.pattern:
            return
        return re.match(cls.pattern, s, re.I)

    @classmethod
    def getSourceName(cls, source, **kwargs):
        return source

    def createElement(self, data={}, idx=None):
        if not idx:
            idx = id(data)
        element = self.element_class(
            data=data, index=idx, model=self
        )
        self.addElement(element)
        return element

    def findElement(self, value=None, by=None):
        for idx, e in self.m_elements.items():
            d = e.data()
            if d.get(by) == value:
                return idx, e

    def addElement(self, element):
        idx = element.index()
        self.m_elements[idx] = element
        return element

    def delElement(self, element):
        self.m_elements.pop(element.index(), None)
        return element

    def updateElement(self, element, data):
        element.updateData(data)
        return element

    def getElement(
            self, value, by="id", only_one=True):
        found=[]
        elements=self.m_elements.values()
        for element in elements: 
            data = element.data()
            if value == data.get(by, None):
                if only_one: 
                    return element
                else:
                    found+=[element]
        return found

    def clearAll(self):
        elems = self.m_elements
        self.m_elements = OrderedDict()
        for e in elems.values():
            self.delElement(e)
