#coding=utf-8
#执行字符串python命令，这些命令在同一个命名空间内
import uniout
import re

vars = {}
def _exec(s):
    '''
    执行python脚本s，历史变量在同一个命名空间
    :param s:
    :return:
    '''
    #定义并赋值变量
    global vars
    vardef = ''
    item = None
    for item in vars.items():
        vardef += "{}=vars[\'{}\']\n".format(item[0],item[0])
    vardef += s
    exec vardef
    del item
    del vardef
    vars = locals()

def _addvar(*varlst):
    '''
    添加变量列表
    :param varlst: [(name1,value1),(name2,value2),...]
    :return:
    '''
    for var in varlst:
        vars[var[0]] = var[1]

def _getvar(name):
    '''
    返回名称为name的变量值
    :param name:
    :return:
    '''
    return vars[name]

def _replacevar(string):
    '''
    替换str中的形如$<a>的字符串为程序变量的值
    :param string:
    :return:
    '''
    regex = re.compile(r'\$\<([^\>]+)\>')
    for var in set(regex.findall(string)):
        # 取得变量值
        string = string.replace('$<' + var + '>', str(_getvar(var)))
    return string
