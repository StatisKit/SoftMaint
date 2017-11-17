from path import Path
import argparse

from .walkfiles import main as walkfiles
from .notice import insert_notice

def main_notice():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help  = 'The directory in which files need to include NOTICE as a license header',
                        nargs ='?',
                        default = '.')
    parser.add_argument('notice',
                        help  = 'The file containing the content of include as files\' license header',
                        nargs ='?',
                        default = 'NOTICE')
    parser.add_argument('--back-up',
                        dest='back_up',
                        action='store_true',
                        help="")
    parser.add_argument('--no-back-up',
                        dest='back_up',
                        action='store_false')
    parser.set_defaults(back_up=False)
    parser.add_argument('--do',
                        dest='do',
                        action='store_true',
                        help="")
    parser.add_argument('--undo',
                        dest='do',
                        action='store_false',
                        help="")
    parser.set_defaults(do=True)
    args = parser.parse_args()

    notice = Path(args.directory)/args.notice
    if not notice.exists():
        raise ValueError("'notice' argument is invalid")
    with open(notice, 'r') as filehandler:
        notice = filehandler.read()

    for filepath in walkfiles(args.directory):
        if args.do:
            insert_notice(filepath, notice, args.back_up)
        elif (filepath + ".back").exists():
            with open(filepath + ".back", "r") as filehandler:
                content = filehandler.read()
            with open(filepath, "w") as filehandler:
                filehandler.write(content)