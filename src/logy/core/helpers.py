def demangled(cls, name: str):
    return name if not name.startswith('__') else '_' + cls.__name__ + name
