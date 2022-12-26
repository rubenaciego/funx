from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from funx_grammar.funxLexer import funxLexer
from funx_grammar.funxParser import funxParser
from funx_grammar.funxVisitor import funxVisitor

class FunxException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class FunxUndefinedFunction(FunxException):
    def __init__(self, fname, line):
        super().__init__('funx undefined function \'' + fname + '\' in \'' + line + '\'')
        self.function_name = fname

class FunxRedefinedFunction(FunxException):
    def __init__(self, fname, line):
        super().__init__('funx redefined function \'' + fname + '\' in \'' + line + '\'')
        self.function_name = fname

class FunxInvalidOperand(FunxException):
    def __init__(self, expr, line):
        super().__init__('funx invalid operand (not an expression) \'' + expr + '\' in \'' + line + '\'')
        self.expr = expr

class FunxInvalidParams(FunxException):
    def __init__(self, fname, fparams, params, line):
        super().__init__('funx invalid parameter amount in \'' + line + '\', calling function \''
            + fname + ' ' + str(fparams) + '\' with ' + str(params))

        self.function_name = fname
        self.function_params = fparams
        self.given_params = params

class FunxRepeatedParams(FunxException):
    def __init__(self, fname, fparams, line):
        super().__init__('funx repeated parameter names in function definition \'' + line + '\'')
        self.function_name = fname
        self.function_params = fparams

class FunxZeroDivision(FunxException):
    def __init__(self, expr):
        super().__init__('funx division by zero in \'' + expr + '\'')
        self.line = expr

class FunxSyntaxError(FunxException):
    def __init__(self, line):
        super().__init__('funx syntax error, ' + line)
        self.line = line


class TreeVisitor(funxVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter

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

        if function_name not in self.interpreter.funcs:
            raise FunxUndefinedFunction(function_name, ctx.getText())

        for p in ctx.params:
            params.append(self.visit(p))

        func = self.interpreter.funcs[function_name]

        if len(params) != len(func[1]):
            raise FunxInvalidParams(function_name, func[1], params, ctx.getText())

        self.interpreter.pushframe()

        for (p, name) in zip(params, func[1]):
            self.interpreter.currframe()[name] = p

        res = self.visit(func[0])
        self.interpreter.popframe()
        return res

    # Visit a parse tree produced by funxParser#unaryOpExpr.
    def visitUnaryOpExpr(self, ctx:funxParser.OpExprContext):
        expr = self.visit(ctx.e)

        if expr is None:
            raise FunxInvalidOperand(ctx.e.getText(), ctx.getText())
        
        return expr if ctx.op.text == '+' else -expr;

    # Visit a parse tree produced by funxParser#not.
    def visitNot(self, ctx:funxParser.NotContext):
        expr = self.visit(ctx.e)

        if expr is None:
            raise FunxInvalidOperand(ctx.e.getText(), ctx.getText())
        
        return int(not expr)

    # Visit a parse tree produced by funxParser#and.
    def visitAnd(self, ctx:funxParser.AndContext):
        left = self.visit(ctx.left)
        if not left: return 0

        right = self.visit(ctx.right)
        if not right: return 0
        return 1

    # Visit a parse tree produced by funxParser#or.
    def visitOr(self, ctx:funxParser.OrContext):
        left = self.visit(ctx.left)
        if left: return 1

        right = self.visit(ctx.right)
        if right: return 1
        return 0

    # Visit a parse tree produced by funxParser#opExpr.
    def visitOpExpr(self, ctx:funxParser.OpExprContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        res = 0

        if left is None:
            raise FunxInvalidOperand(ctx.left.getText(), ctx.getText())
        elif right is None:
            raise FunxInvalidOperand(ctx.right.getText(), ctx.getText())

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
                case _: raise FunxSyntaxError('unknown binary operator \'' + ctx.op.text + '\'')
        except ZeroDivisionError:
            raise FunxZeroDivision(ctx.getText()) from None
        
        return res

    # Visit a parse tree produced by funxParser#var.
    def visitVar(self, ctx:funxParser.VarContext):
        var_name = ctx.var.text
        if var_name not in self.interpreter.currframe():
            self.interpreter.currframe()[var_name] = 0
        return self.interpreter.currframe()[var_name]

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
        self.interpreter.currframe()[dst_name] = val

    # Visit a parse tree produced by funxParser#ifelse.
    def visitIfelse(self, ctx:funxParser.IfelseContext):
        cond = self.visit(ctx.cond)
        if cond is None:
            raise FunxInvalidOperand(ctx.cond.getText(), ctx.getText())
        
        if cond: return self.visit(ctx.trueb)
        elif ctx.falseb: return self.visit(ctx.falseb)

    # Visit a parse tree produced by funxParser#while.
    def visitWhile(self, ctx:funxParser.WhileContext):
        cond = self.visit(ctx.cond)

        if cond is None:
            raise FunxInvalidOperand(ctx.cond.getText(), ctx.getText())

        while cond:
            res = self.visit(ctx.b)
            if res: return res
            cond = self.visit(ctx.cond)
            if cond is None:
                raise FunxInvalidOperand(ctx.cond.getText(), ctx.getText())


    # Visit a parse tree produced by funxParser#fundef.
    def visitFundef(self, ctx:funxParser.FundefContext):
        function_name = ctx.fun.text

        if function_name in self.interpreter.funcs:
            raise FunxRedefinedFunction(function_name, ctx.getText())

        param_names = []
        for p in ctx.params:
            param_names.append(p.text)

        if len(param_names) != len(set(param_names)):
            raise FunxRepeatedParams(function_name, param_names, ctx.getText())
        
        self.interpreter.funcs[function_name] = (ctx.b, param_names)


class FunxErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise FunxSyntaxError('line ' + str(line) + ':' + str(column) + ' ' + msg) from None


class FunxInterpreter:
    def __init__(self):
        self.error_listener = FunxErrorListener()
        self.funcs = {}
        self.stackframe = []
        self.visitor = TreeVisitor(self)

        self.pushframe()

    def pushframe(self):
        self.stackframe.append({})
    
    def popframe(self):
        self.stackframe.pop()

    def currframe(self):
        return self.stackframe[-1]

    def execute(self, code):
        input_stream = InputStream(code)
        lexer = funxLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(self.error_listener)
        token_stream = CommonTokenStream(lexer)
        parser = funxParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(self.error_listener)
        tree = parser.root()
        return self.visitor.visit(tree)
