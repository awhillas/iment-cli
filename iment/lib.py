import imghdr
import pathlib  # Python 3.5+
import sys
from os.path import abspath, exists, expanduser


def path_check(p, create=False):
    """ Expand path to absolute and make sure it exists """
    path = expanduser(p) if p.startswith('~') else abspath(p)
    if create:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path if exists(path) else False

def query_yes_no(question:str, default:str="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    see: https://stackoverflow.com/a/3041990/196732
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def query_options(question:str, options:dict, default:str=None):
    """ Ask a question and give a list of options with a default.

        :param question: Free text
        :param options: keys are the input options, values are for display
        :param default: which option to return of user presses <enter>
        :return: One of the keys from the options dict. If not given first otion is assumed.
    """
    valid = list(options.keys())
    defaulty = default if default else valid[0]
    prompt = "[{}]".format("/".join([ i.upper() if i is defaulty else i for i in valid ]))
    menu = []
    for k, v in options.items():
        menu.append("{} - {}".format(k, v))

    while True:
        sys.stdout.write("{}\n{}\n{}?".format(question, "\n".join(menu), prompt))
        choice = input().lower()
        if choice == '':
            return defaulty
        elif choice in valid:
            return choice
        else:
            sys.stdout.write("wha...?\n")

def print_table(myDict:list, colList:list=None):
    """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
        from: https://stackoverflow.com/a/40389411/196732

        :param colList: If column names aren't specified, they will show in random order.
        :param sep: row separator. Ex: sep='\n' on Linux. Default: dummy to not split line.
    """
    if not colList: colList = list(myDict[0].keys() if myDict else [])
    myList = [colList] # 1st row = header
    for item in myDict:
        myList.append([str(item[col] or '') if col in item else '-' for col in colList])
    colSize = [max(map(len,col)) for col in zip(*myList)]
    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    myList.insert(1, ['-' * i for i in colSize]) # Seperating line
    for item in myList: print(formatStr.format(*item))

def print_h_table(data:list, columns:list):
    """ Print items horizontally in a table
        :param data: list of dicts
        :param columns: list of colums to show, should be keys in data's dicts
    """
    pass
