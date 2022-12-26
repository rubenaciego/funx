from antlr4 import *
from funxLexer import funxLexer
from funxParser import funxParser
from funxVisitor import funxVisitor

class TreeVisitor(funxVisitor):

    def __init__(self):
        self.stackframe = []
        self.funcs = {}

        self.stackframe.append({})

    # Visit a parse tree produced by funxParser#block.
    def visitBlock(self, ctx:funxParser.BlockContext):
        for ins in ctx.ins:
            res = self.visit(ins)
            if res != None: return res

    # Visit a parse tree produced by funxParser#funcall.
    def visitFuncall(self, ctx:funxParser.FuncallContext):
        function_name = ctx.fun.text
        params = []

        for p in ctx.params:
            params.append(self.visit(p))

        func = self.funcs[function_name]

        if len(params) != len(func[1]):
            print("Error with parameter amount")
            return None

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

        # TODO check division by 0 and Nones

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
            case _: print("Unkwown operand")
        
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
        if cond: return self.visit(ctx.trueb)
        elif ctx.falseb: return self.visit(ctx.falseb)

    # Visit a parse tree produced by funxParser#while.
    def visitWhile(self, ctx:funxParser.WhileContext):
        cond = self.visit(ctx.cond)

        while cond:
            res = self.visit(ctx.b)
            if res: return res
            cond = self.visit(ctx.cond)


    # Visit a parse tree produced by funxParser#fundef.
    def visitFundef(self, ctx:funxParser.FundefContext):
        function_name = ctx.fun.text
        param_names = []
        for p in ctx.params:
            param_names.append(p.text)
        
        self.funcs[function_name] = (ctx.b, param_names)


def execute_funx(code):
    input_stream = InputStream(code)
    lexer = funxLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = funxParser(token_stream)
    tree = parser.block()
    visitor = TreeVisitor()
    print("Out: " + str(visitor.visit(tree)))
    print(tree.toStringTree(recog=parser))


def main():
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    s = """{}""".format("\n".join(contents))
    execute_funx(s)

if __name__ == '__main__':
    main()
