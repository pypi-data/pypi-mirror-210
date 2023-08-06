from os.path import expanduser

home = expanduser("~")

class Store:
    def __init__(self, win_letter:str, win_path: str, unix_path: str):
        self._win_letter = win_letter
        self._win_path = win_path
        self._unix_path = unix_path

    def replace_letter(self, dir:str):
        return dir.replace(self._win_letter, self._win_path)

    def to_unix(self, dir: str):
        res = self.replace_letter(dir)
        res = res.replace(self._win_path, self._unix_path)
        res = res.replace("\\", "/")
        return res

    def to_win(self, dir: str):
        res = dir.replace(self._unix_path, self._win_path)
        # res = res.replace("/", "\\")
        return res