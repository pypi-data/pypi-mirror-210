import os as _os
class FileData:
    @classmethod
    def check_ext(cls, /, file):
        if cls._ext is None:
            return
        if cls._ext == _os.path.splitext(file):
            return
        raise ValueError()

    @classmethod
    def load(cls, /, file):
        cls.check_ext(file)
        return cls._load(file)

    def save(self, /, file):
        type(self).check_ext(file)
        if self._save(file) is not None:
            raise ValueError()
        