import os

class FileCache:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_file(self, prefix, key, ext) -> str:
        """
        prefix 에 해당하는 파일에서 key 에 해당하는 값을 가져온다.
        :param prefix:
        :param key: key는 항상 yyyymmdd 를 가지고 있어야 한다
        :return:
        """

        yyyy = key[:4]
        mm = key[4:6]
        dd = key[6:]

        file_name = self.base_dir + '/' + prefix + '/' + yyyy + '/' + mm + '/' + dd + '/' + key + '.' + ext
        if not os.path.exists(file_name):
            return None
        with open(file_name, 'r') as f:
            return f.read()

    def save_file(self, prefix, key, ext, data):
        yyyy = key[:4]
        mm = key[4:6]
        dd = key[6:]

        file_dir = self.base_dir + '/' + prefix + '/' + yyyy + '/' + mm + '/' + dd
        os.makedirs(file_dir, exist_ok=True)

        file_name =self.base_dir + '/' + prefix + '/' + yyyy + '/' + mm + '/' + dd + '/' + key + '.' + ext
        with open(file_name, "w") as f:
            f.write(data)