import hashlib

def encode_to_md5(s,encode='utf8'):
    """
    字符串转md5
    :param s:
    :param encode:
    :return:
    """
    m = hashlib.md5()
    m.update(s.encode(encode))
    return m.hexdigest()


def decode_file_to_md5(file_path,encode='utf8'):
    """
    获取文件的md5
    :param file_path:
    :param encode:
    :return:
    """
    md5_hash = hashlib.md5()
    md5_result = ""
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        md5_result = md5_hash.hexdigest()
    return md5_result
