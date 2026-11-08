class Cache(dict):

    def setCache(self, key, value, name="default"):
        self[name][key] = value

    def clearCache(self, name="default"):
        self[name] = {}

    def addCache(self, name="default", holder={}):
        if not name in self:
            self[name] = holder

    def dropCache(self, key, name="default"):
        if name in self:
            self[name].pop(key, None)

    def getCache(self, key=None, name="default"):
        cache = self.get(name, {})
        if key:
            return cache.get(key, None)
        return cache
