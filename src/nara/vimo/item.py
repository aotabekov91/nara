from .object import Object

class Item(Object):

    def __init__(
        self,
        view=None,
        index=None,
        element=None,
        identifier=None,
        **kwargs,
    ):
        self.m_id = index
        self.m_view = view
        self.m_element = element
        self.m_identifier = identifier
        super().__init__(**kwargs)

    def setup(self):
        super().setup()
        self.setView(self.m_view)
        self.setElement(self.m_element)

    def identifier(self):
        return self.m_identifier

    def setIdentifier(self, identifier):
        self.m_identifier = identifier

    def view(self):
        return self.m_view

    def setView(self, view):
        self.m_view = view

    def element(self):
        return self.m_element

    def update(self):
        pass

    def setElement(self, element):
        self.m_element = element

    def index(self):
        return self.m_id

    def setIndex(self, idx):
        self.m_id = idx
