"""
execute python from string! thank you Jesus!
"""

import sys
import traceback
import code as _code
from io import StringIO
from importlib import util

# I'm not sure if we need this still. I know sha that we need a way
# to set the exec know what module is running...
def run2(source: str, file=False):
    lcls = {"sys": sys, "__name__": "__main__"}
    interpreter = _code.InteractiveInterpreter(locals=lcls)
    # here, we are saying this guy come's from the
    # actually, try to get the name of the file!
    interpreter.runsource(source, '<main>', 'exec')


def run(code: str, return_output: bool=False, cloud=False):
    """Execute Python code

    Keyword arguments:
    argument -- description
    Return: return_description
    """

    codeOut = StringIO()
    codeErr = StringIO()

    sys.stdout = codeOut
    sys.stderr = codeErr

    try:
        my_spec = util.spec_from_loader("main_cloud", loader=None)
        my_module = util.module_from_spec(my_spec)


        if cloud:
            exec(code, my_module.__dict__)
        else:
            exec(code)
    except Exception as e:
        err = e
        traceback.print_exc()

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    err = codeErr.getvalue()

    s = codeOut.getvalue()

    codeOut.close()
    codeErr.close()

    if not return_output:
        if err:
            print("error: \n%s\n" % err)
        print("output: \n%s" % s)
    else:
        return err, s




if __name__ == '__main__':
    code = """
                if (20 > 10) {
                    print('Greater!');
                } else {
                    print('Smaller!');
                };
            """
    run(code)
