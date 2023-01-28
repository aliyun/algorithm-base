import inspect


def arguments():
    """Returns tuple containing dictionary of calling function's
       named arguments and a list of calling function's unnamed
       positional arguments.

       linked from here. http://kbyanc.blogspot.com/2007/07/python-aggregating-function-arguments.html
    """
    from inspect import getargvalues, stack
    posname, kwname, args = getargvalues(stack()[1][0])[-3:]
    posargs = args.pop(posname, [])
    args.update(args.pop(kwname, []))
    return args, posargs
