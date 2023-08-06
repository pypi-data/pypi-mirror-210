def rewrite_file(source, target, chunk_size=None):
    """Copies contents of one file-like object into another"""
    megabyte = 1024**2
    chunk_size = chunk_size or (10 * megabyte)
    while True:
        bytes_read = source.read(chunk_size)
        if not bytes_read:
            break
        target.write(bytes_read)
