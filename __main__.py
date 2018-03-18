#coding=utf-8
import getopt
import sys
from difffile import difffile
import scriptrunner

opts ,args = getopt.gnu_getopt(sys.argv[1:],'r:o',['root=','objfile'])
ROOT_DIR = './'
OBJ_FILE = ''
if(args.__len__() == 0):
    print '使用方式：\npython diffexe difffile1.diff difffile2.diff ... [-r ROOT_DIR] [-o OBJ_FILE]'
else:
    for dfpath in args:
        for opt in opts:
            if (opt[0] == '-r' or opt[0] == '--root'):
                ROOT_DIR = opt[1]
            elif (opt[0] == '-o' or opt[0] == '--objfile'):
                OBJ_FILE = opt[1]
        f = difffile(dfpath)
        if (f.isValidDIffFile()):
            f.execute(ROOT_DIR, OBJ_FILE)
        else:
            f._error('无效文件！')