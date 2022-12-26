from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from funxLexer import funxLexer
from funxParser import funxParser
from funxVisitor import funxVisitor

class FunxUndefinedFunction(Exception):
    
    def __init__(self, fname):
        self.function_name = fname

class FunxRedefinedFunction(Exception):

    def __init__(self, fname):
        self.function_name = fname

class FunxInvalidOperand(Exception):

    def __init__(self, expr):
        self.expr = expr

class FunxInvalidParams(Exception):

    def __init__(self, fname, fparams, params):
        self.function_name = fname
        self.function_params = fparams
        self.given_params = params

class FunxRepeatedParams(Exception):

    def __init__(self, fname, fparams):
        self.function_name = fname
        self.function_params = fparams

class FunxZeroDivision(Exception):
    
    def __init__(self, expr):
        self.line = expr

class FunxSyntaxError(Exception):
    
    def __init__(self, line):
        self.line = line


class TreeVisitor(funxVisitor):

    def __init__(self):
        self.stackframe = []
        self.funcs = {}

        self.stackframe.append({})

    # Visit a parse tree produced by funxParser#root.
    def visitRoot(self, ctx: funxParser.RootContext):
        return self.visit(ctx.b)

    # Visit a parse tree produced by funxParser#block.
    def visitBlock(self, ctx:funxParser.BlockContext):
        for ins in ctx.ins:
            res = self.visit(ins)
            if res != None: return res

    # Visit a parse tree produced by funxParser#funcall.
    def visitFuncall(self, ctx:funxParser.FuncallContext):
        function_name = ctx.fun.text
        params = []

        if function_name not in self.funcs:
            raise FunxUndefinedFunction(function_name)

        for p in ctx.params:
            params.append(self.visit(p))

        func = self.funcs[function_name]

        if len(params) != len(func[1]):
            raise FunxInvalidParams(function_name, func[1], params)

        self.stackframe.append({})

        for (p, name) in zip(params, func[1]):
            self.stackframe[-1][name] = p

        res = self.visit(func[0])
        self.stackframe.pop()
        return res


    # Visit a parse tree produced by funxParser#opExpr.
    def visitOpExpr(self, ctx:funxParser.OpExprContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        res = 0

        if left is None:
            raise FunxInvalidOperand(ctx.left.text)
        elif right is None:
            raise FunxInvalidOperand(ctx.right.text)

        try:
            match ctx.op.text:
                case '*': res = left * right
                case '/': res = left // right
                case '%': res = left % right
                case '+': res = left + right
                case '-': res = left - right
                case '<': res = int(left < right)
                case '>': res = int(left > right)
                case '<=': res = int(left <= right)
                case '>=': res = int(left >= right)
                case '=': res = int(left == right)
                case '!=': res = int(left != right)
                case _: raise FunxSyntaxError("unknown binary operator " + ctx.op.text)
        except ZeroDivisionError:
            raise FunxZeroDivision(ctx.getText()) from None
        
        return res


    # Visit a parse tree produced by funxParser#var.
    def visitVar(self, ctx:funxParser.VarContext):
        var_name = ctx.var.text
        vars = self.stackframe[-1]
        if var_name not in vars:
            vars[var_name] = 0
        return vars[var_name]


    # Visit a parse tree produced by funxParser#atom.
    def visitAtom(self, ctx:funxParser.AtomContext):
        num = int(ctx.atom.text)
        return num


    # Visit a parse tree produced by funxParser#parentExpr.
    def visitParentExpr(self, ctx:funxParser.ParentExprContext):
        return self.visit(ctx.inner)


    # Visit a parse tree produced by funxParser#assignment.
    def visitAssignment(self, ctx:funxParser.AssignmentContext):
        dst_name = ctx.dst.text
        val = self.visit(ctx.src)
        vars = self.stackframe[-1]
        vars[dst_name] = val


    # Visit a parse tree produced by funxParser#ifelse.
    def visitIfelse(self, ctx:funxParser.IfelseContext):
        cond = self.visit(ctx.cond)
        if cond is None:
            raise FunxInvalidOperand(ctx.cond.text)
        
        if cond: return self.visit(ctx.trueb)
        elif ctx.falseb: return self.visit(ctx.falseb)

    # Visit a parse tree produced by funxParser#while.
    def visitWhile(self, ctx:funxParser.WhileContext):
        cond = self.visit(ctx.cond)

        if cond is None:
            raise FunxInvalidOperand(ctx.cond.text)

        while cond:
            res = self.visit(ctx.b)
            if res: return res
            cond = self.visit(ctx.cond)
            if cond is None:
                raise FunxInvalidOperand(ctx.cond.text)


    # Visit a parse tree produced by funxParser#fundef.
    def visitFundef(self, ctx:funxParser.FundefContext):
        function_name = ctx.fun.text

        if function_name in self.funcs:
            raise FunxRedefinedFunction(function_name)

        param_names = []
        for p in ctx.params:
            param_names.append(p.text)

        if len(param_names) != len(set(param_names)):
            raise FunxRepeatedParams(function_name, param_names)
        
        self.funcs[function_name] = (ctx.b, param_names)


class FunxErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise FunxSyntaxError("line " + str(line) + ":" + str(column) + " " + msg) from None

def execute_funx(code):
    error_listener = FunxErrorListener()
    input_stream = InputStream(code)
    lexer = funxLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    token_stream = CommonTokenStream(lexer)
    parser = funxParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.root()
    visitor = TreeVisitor()
    return visitor.visit(tree)


def main():
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    s = """{}""".format("\n".join(contents))
    print("Out: " + str(execute_funx(s)))

if __name__ == '__main__':
    main()
