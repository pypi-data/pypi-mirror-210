class File:
    file_in_use = None
    __lines = []

    def __init__(self, path):
        self.path = path

    def open(self, mode):
        self.file_in_use = open(self.path, mode)
        return self.file_in_use

    def close(self):
        self.file_in_use.close()

    def write(self, line):
        self.file_in_use.write(line)

    def write_lines(self, lines):
        self.file_in_use.writelines(lines)
        self.close()

    def get_lines(self):
        self.__lines = open(self.path).readlines()
        return self.__lines

    def is_empty(self):
        return len(self.get_lines()) == 0
