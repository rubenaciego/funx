from funx_interpreter import *
from flask import Flask, render_template, request
from collections import deque

app = Flask(__name__)
funx_intr = FunxInterpreter()
history = deque(maxlen=5)
submit_count = 0

@app.route('/', methods = ['POST', 'GET'])
def mainpage():
    global submit_count
    out = None
    error = None
    
    if request.method == 'POST':
        result = request.form
        code = result['input']

        try:
            out = funx_intr.execute(code)
            history.appendleft((code, out, submit_count))
            submit_count += 1
        except FunxException as e:
            error = str(e)

            # Clean frames if the error happened inside a function
            while len(funx_intr.stackframe) > 1:
                funx_intr.popframe()
    
    return render_template("base.html", out=out, error=error,
        hist=history, vars=funx_intr.currframe(), funcs=funx_intr.funcs)
