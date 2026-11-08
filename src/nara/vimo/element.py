from .object import Object

class Element(Object):

    def __init__(
        self,
        id=None,
        data={},
        index=None,
        model=None,
        identifier=None,
        **kwargs,
    ):
        self.m_id = id
        self.m_data = data
        self.m_index = index
        self.m_model = model
        self.m_kwargs = kwargs
        self.m_identifier = identifier
        super().__init__(**kwargs)
        if data:
            self.setData(data)

    def id(self):
        return self.m_id

    def setId(self, idx):
        self.m_id = idx

    def identifier(self):
        return self.m_identifier

    def setIdentifier(self, idx):
        self.m_identifier = idx

    def data(self, idx=None):
        if not idx:
            return self.m_data
        return self.m_data.get(idx, None)

    def setData(self, data):
        self.m_data = data
        # self.dataReset.emit()

    def updateData(self, data):
        self.m_data.update(data)
        # self.dataUpdated.emit()

    def model(self):
        return self.m_model

    def setModel(self, model):
        self.m_model = model

    def index(self):
        return self.m_index

    def setIndex(self, idx):
        self.m_index = idx

    def get(self, key, default=None):
        return self.m_data.get(key, default)

    def set(self, key, value):
        self.m_data[key]=value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __bool__(self):
        if self.m_data:
            return True
        return False
