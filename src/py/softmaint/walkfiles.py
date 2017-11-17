from path import Path
import os

def main(dirpath):
    if not isinstance(dirpath, Path):
        dirpath = Path(dirpath)
    if (dirpath/'.gitignore').exists():
        return git(dirpath)
    return fs(dirpath)

def fs(dirpath):
    if not isinstance(dirpath, Path):
        dirpath = Path(dirpath)
    filepaths = list(dirpath.walkfiles())
    return [filepath for filepath in filepaths if not any(parent.startswith('.') for parent in filepath.relpath(dirpath).splitall()[1:])]

def git(dirpath, vcs=None):
    return [filepath for filepath in fs(dirpath) if os.system('git check-ignore ' + filepath)]