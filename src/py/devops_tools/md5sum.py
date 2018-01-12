import md5
from .walkfiles import main as walkfiles

def compute_md5sum(directory):
    md5sum = md5.new()
    for filepath in walkfiles(directory):
        with open(filepath, 'r') as filehandler:
            md5sum.update(filehandler.read())
    return md5sum.hexdigest()