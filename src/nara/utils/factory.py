def Factory(*klasses):
    class Klass(*klasses):
        pass

    return Klass
