"""
generate the python code from AST tree
AST -> Abstract Syntax Tree... thank you Jesus!

THIS FILE IS FULL OF GOD'S GRACE AND MAGIC CODE :)))
"""

import json
from .importer import get
from .translations import keywords, operator_words, builtin_functions, builtin_funcs
""" NOTE: Let all blocks be like this:
    if [COND] {\n
        [EXPRESSION]
    \n}
    Asin, the curly braces should be at the end of everyline
"""


def is_in_parents_props(prop_name: str, parent_props) -> bool:
    """For every prop in parent check if that prop is same as the passed prop
        if so, stop searching and return found
    """
    found = False
    i = 0

    if len(parent_props) <= 0:
        return found

    while not found and i < len(parent_props):
        p = parent_props[i]
        if p.get("value", None) == prop_name or p.get("left", None) == prop_name:
            found = True
        i += 1

    return found



def make_py(token, local: bool = False):
    """local is if this file is a local file"""

    settings = token.get("settings", {"lang": "hausa"})

    # TODO: NOTE: lease how do we ensure this dictionary is always
    # accurate!
    word_ops = {
        operator_words[settings["lang"]]["and"]: "and",
        operator_words[settings["lang"]]["or"]: "or",
        operator_words[settings["lang"]]["is"]: "=",
        operator_words[settings["lang"]]["not"]: "!=",
        operator_words[settings["lang"]]["in"]: "in",
        operator_words[settings["lang"]]["plus"]: "+",
        operator_words[settings["lang"]]["minus"]: "-",
        operator_words[settings["lang"]]["times"]: "*",
        operator_words[settings["lang"]]["dividedby"]: "/"
    }


    def handle_operators(op: str) -> str:
        """ convert custom operators to python operators... """
        # check if string operator, else just return op

        if op.isalpha():
            return word_ops.get(op)
        else:
            return op

    def pythonise(token):
        switch = {
            "num": py_atom,
            "str": py_atom,
            "bool": py_atom,
            "var": py_var,
            "module": py_var,
            "binary": py_binary,
            "membership": py_binary,
            "assign": py_assign,
            "access": py_access,
            "function": py_function,
            "import": py_import,
            "return": py_return,
            "if": py_if,
            "list": py_list,
            "dict": py_dict,
            "while": py_while,
            "for": py_forloop,
            "call": py_call,
            "prog": py_prog,
            # class stuff
            "class": py_class,
            "class_property": py_class_prop
        }

        doer = switch.get(token["type"], None)

        if not doer:
            raise Exception("Invalid Hapy code: %s" % json.dumps(token))

        return doer(token)

    # helper functions
    def py_atom(tok):
        """return the value of a token"""

        # if its a boolean, don't stringify the value, return it
        # raw
        if tok["type"] == "bool":
            return "%s" % tok["value"]
        return json.dumps(tok["value"])

    def py_var(tok):
        """return a plain variable value"""

        # hmm, let's check if this var is a hausa builtin
        if settings["lang"] == "hausa" and tok["value"] in builtin_functions["hausa"].values():
            return builtin_funcs[tok["value"]]

        return tok["value"]

    def py_class_prop(tok):
        """return a plain variable value"""
        if "default_value" in tok:
            return "{left}{op}{right}".format(
                **{
                    "left": pythonise(tok["value"]),
                    "op": "=",
                    "right": pythonise(tok["default_value"])
                })

        return tok["value"]

    def py_binary(tok):
        """return a binary statement"""
        """ this is because we make '.' a binary operator :)
                        and we are using this different notation cuz I don't want space
                        between the operands... 'foo.bar' over 'foo . bar'
        """

        # give space between operands by default
        s1 = s2 = " "

        brackets = ("(", ")")

        # to access the keys for the operands on each side
        left_key, right_key = "left", "right"

        if tok["operator"] == ".":
            s1 = s2 = ""

        if tok["operator"] == ":":
            left_key, right_key = "key", "value"
            # no space after the 'key' => {"key": value}
            s1 = ""

        if tok["type"] != "binary":
            brackets = ("", "")

        # if tok["operator"] == ".":

        #     return "{left}{op}{right}".format(
        #         **{
        #             "left": pythonise(tok["left"]),
        #             "op": handle_operators(tok["operator"]),
        #             "right": pythonise(tok["right"])
        #         })
        # else:
        """if this is a regular binary operator, then give space!"""
        return brackets[0] + "{left}{s1}{op}{s2}{right}".format(
            **{
                "left": pythonise(tok[left_key]),
                "op": handle_operators(tok["operator"]),
                "right": pythonise(tok[right_key]),
                "s1": s1,
                "s2": s2
            }) + brackets[1]

    def py_assign(tok):
        """return an assign function"""

        return py_binary(tok)

    def py_access(tok):
        """return dot access statement: foo.bar """
        return py_binary(tok)

    def py_function(tok, class_method=False, custom_name=None):
        """return a Python function definition"""

        function_name = pythonise(
            tok["name"]) if not custom_name else custom_name

        args = ""

        if class_method:
            sep = "," if len(tok["vars"]) > 0 else ""
            args = " (self" + sep + "{args})".format(**{
                "args":
                ", ".join(list(map(lambda x: pythonise(x), tok["vars"])))
            })
        else:
            args = " ({args})".format(**{
                "args":
                ", ".join(list(map(lambda x: pythonise(x), tok["vars"])))
            })

        o = "def " + function_name + args + "{\n"\
        + pythonise(tok["body"]) + "\n}"

        return o

    def py_list(tok):
        """return a Python list definition"""

        o = " [{args}]".format(**{
            "args":
            ",".join(list(map(lambda x: pythonise(x), tok["elements"])))
        })

        return o

    def py_dict(tok):
        """This turns a dictionary AST into a dictionary with boundary definition like this `<<<| |>>>` """
        o = "<<<|{args}|>>>".format(
            **{"args": ", ".join(list(map(lambda x: py_binary(x), tok["content"])))})
        return o

    """ NOTE: Let all blocks be like this:
        if [COND] {\n
            [EXPRESSION]
        \n}
        Asin, the curly braces should be at the end of everyline
    """

    def py_if(tok):
        """creates a Python if statement"""
        # TODO: support elif...

        if_blck = "if (" + pythonise(tok["cond"]) + ") {\n" + pythonise(tok["then"]) + "\n}"


        elif_blcks = ""

        else_blck = (("else {\n" + pythonise(tok["else"]) + "\n}") if tok.get("else", None) else "")

        for el in tok["elifs"]:
            elif_blcks = elif_blcks + "elif (" + pythonise(el["cond"]) + ") {\n" + pythonise(el["then"]) + "\n}"

        return if_blck + elif_blcks + else_blck

    def py_while(tok):
        """while loop, returns python while loop!"""

        o = "while (" + pythonise(tok["cond"]) + ") {\n"
        + pythonise(tok["then"]) + "\n}"

        return o

    def py_forloop(tok):
        """forloop, returns python for loop!"""

        o = "for " + pythonise(tok["header"]) + " {\n" \
        + pythonise(tok["body"]) + "\n}"

        return o

    def py_call(tok):
        # just return the token
        return pythonise(tok["func"]) + "({args})".format(**{
            "args":
            ", ".join(list(map(lambda x: pythonise(x), tok["args"])))
        })

    def py_class(tok):
        """generate python class"""

        # Make the 'class header' i.e class ClassName(ParentClass):
        class_header = "class " + pythonise(tok["name"]) + ("(%s) {\n" % tok["inherits"]["value"] if \
        "inherits" in tok else " {\n")

        # Add __init__ method and other special methods, if available
        init = ""

        for t in tok["class_special_methods"]:
            # for each special method
            if t["name"]["value"] == builtin_functions[settings["lang"]]["__startwith__"]:
                init += py_class_init(tok, t)
                # the __str__ method
            elif t["name"]["value"] == builtin_functions[settings["lang"]]["__toshow__"]:
                init += py_function(
                    t, class_method=True, custom_name='__repr__') + ";\n"
            else:
                # if we don't recognize the special method...
                init += "#invalid special method\n"

        # Add Class Methods, if any.
        methods = ""
        if "class_methods" in tok:
            methods = ";\n".join(
                list(
                    map(lambda x: py_function(x, class_method=True),
                        tok["class_methods"])))

        # Add body expressions, if any. Usually this is None
        class_body = ""
        if "body" in tok:
            class_body = "pass"

        # Add everything together, plus close with } :p
        o = class_header + init + methods + class_body + "\n}"

        return o

    def py_class_init(tok, init_token):
        """return __init__ definition"""

        # Make the __init__ function header with arguments, if any
        # i.e def __init__(self, {args}){\n

        # find similar stuff...

        init_header = "def __init__(self, {args})".format(
            **{
                "args":
                ", ".join(
                    list(map(lambda x: pythonise(x), tok["class_properties"])))
            }) + " {\n"

        init_body = ""

        # if this class inherits another, add the super() statement...
        if "inherits" in tok:
            args = ""

            # TODO (!!!!): prevent duplicating attributes that were sent to Parent in
            # the _init_ also!

            if "init_parent" in tok and tok["init_parent"].get("args", None):
                args = ", ".join(
                    list(
                        map(lambda x: pythonise(x),
                            tok["init_parent"]["args"])))

            init_body += "super().__init__({});\n".format(args)

        # if there are class properties, add the initializations here...
        if len(tok["class_properties"]) > 0:

            # add 'self.abc = abc' to init
            for p in tok["class_properties"]:
                # if it has a default value, make that property
                # equal to the default value...
                if p["type"] == "var" and not is_in_parents_props(p["value"], tok.get("init_parent", {}).get("args", [])):
                    # only do this if the prop_name is not in init_class props

                    init_body += "self.{prop_name} = {prop_name}".format(
                        **{"prop_name": p["value"]}) + ";\n"
                elif p["type"] == "assign" and not is_in_parents_props(p["left"]["value"], tok.get("init_parent", {}).get("args", [])):
                    # it means, the var is in assign!
                    init_body += "self.{prop_name} = {prop_name}".format(
                        **{"prop_name": p["left"]["value"]}) + ";\n"

        # the expressions inside the __init__ body
        if init_token.get("body", None):
            init_body += "\n" + pythonise(init_token["body"]) + ";\n"

        # add everything together
        o = "\n" + init_header + init_body + "}\n"

        return o

    def py_return(tok):
        # return a return statement...
        o = "return " + pythonise(tok["expression"])

        return o

    def py_import(tok):
        """paste import statement in code
        Importing in Hapy. You can import:
        - Another .hapy "module"
        - A "custom" builtin module, see popo and test lol
        - Actual Python builtin modules, no restrictions for now!

        It was challenging at first, but thank God we achieved it.
        :)
        """

        status, imp_type, result = get(tok["module"]["value"], is_local=local)

        if status and imp_type in (1, 2):
            # this means it's a hapy builtin or
            # another local module
            # this adds a statement that makes that module available in the code
            # I haven't tested it for multiple embedded imports. I'm afraid :]

            o = result + "\n"
        elif status and imp_type == 3:
            # this means it's neither a Hapy module nor a local module...
            # and it starts with 'py_*' this is how we differentiate Python
            # modules in Hapy. For now...
            o = "import {module}\n".format(**{"module": result})
        elif not status:
            # this module is neither a hapy builtin, custom local module
            # or even a python module that starts with 'py_'
            # return an error!
            o = "# !!! Hapy cannot import {module}. Sorry :/ !!!\n".\
                format(**{"module": tok["module"]["value"]})

        return o

    def py_prog(tok):
        # just return the token
        # TODO: maybe add closing ; at the end of the program? DISCUSS IT
        return ";\n".join(list(map(lambda x: pythonise(x), tok["prog"])))

    return pythonise(token)


if __name__ == "__main__":
    print("In generate_py")
