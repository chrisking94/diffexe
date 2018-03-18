#coding=utf-8
import os
import re
import shutil
from prettytable import PrettyTable
import scriptrunner


LINE_CMD_MASK=r'//\$' #用于正则表达式中，必须转义特殊字符
class difffile():
    excuteddict = {}#已经执行过的文件绝对路径
    def __init__(self,path):
        self.path = path
        if(os.path.exists(self.path)):
            self.abspath = os.path.abspath(self.path)
            # 添加到文件列表
            difffile.excuteddict[self.abspath] = self
            self.dir = os.path.dirname(self.abspath) + '/'
            self.filename = os.path.basename(self.path)
            f = file(self.path, mode='r')
            self.lines = f.read().split('\n')
            f.close()
            self.fpath = ''
            self.ftmppath = ''
            self.fidx = 0
            self.idx = 0
            self.succexed = False #成功执行
            self.type = 'diff'
        else:
            #无效文件
            self.lines = []


    def isValidDIffFile(self):
        if(self.lines.__len__() > 0):
            line0 = self.lines[0]
            if( line0[0:4] == 'diff'):
                return 1
        return 0

    def _include(self,path,root):
        path = os.path.abspath(path)
        if (difffile.excuteddict.has_key(path)):
            file = difffile.excuteddict[path]
        else:
            file = difffile(path)
            if (file.isValidDIffFile()):
                file.execute(root)
        if (file.succexed):
            # 已经执行成功
            return 1
        else:
            self._error('错误：所需#include<%s>未执行成功，程序中止！' % (path))
            return 2


    @staticmethod
    def _isSameStr(str1,str2):
        '''
        删除str1,str2中所有空白字符后进行比较
        :param str1:
        :param str2:
        :return: 相同返回True,否则False
        '''
        regexp = re.compile(r'\s+')
        s1 = regexp.sub(r'', str1)
        s2 = regexp.sub(r'', str2)
        if (s1 == s2):
            return True
        else:
            return False

    def _checkLine(self, line, fline):#删除str中所有空白符后进行比较
        if(self._isSameStr(line,fline)):
            return True
        else:
            self._error('错误：无法在{}中第【{}】行匹配行\"{}\",请查看diff文件第【{}】行，或检查u-boot版本！' \
                        .format(self.fpath, self.fidx + 1, line, self.idx + 1), 2, self)

    def _writeFLine(self,line):
        self.fout.write(line+'\n')

    def _print(self,msg,mode='default',forecolor='white',backcolor='black'):
        modedict = {'default':0,'highlight':1,'bold':2,'nobold':22,'underline':4,'nounderline':24
                    ,'blink':5,'noblink':25,'inverse':7,'noinverse':27}
        colordict = {'black':0,'red':1,'green':2,'yellow':3,'blue':4,'pink':5,'cyan':6,'white':7}
        msg = '\033[{};{};{}m{}\033[0m'.format(modedict[mode],
                                                colordict[forecolor] + 30,
                                                colordict[backcolor] + 40,
                                               msg)
        print   msg

    def _msg(self, msg, mode='default', forecolor='white', backcolor='black'):
        '''
        与_print()相似
        不同处在于_msg会在【消息】前面增加【self.path：]字样
        :param msg:
        :param mode:
        :param forecolor:
        :param backcolor:
        :return:
        '''
        msg = self.path + "：" + msg
        self._print(msg,mode,forecolor,backcolor)

    def _printAround(self,index,lines):
        '''
        输出index和其前后5行
        :param index:
        :return:
        '''
        count = 5
        start = index - count
        end = index + count + 1
        if(start < 0):
            end -= start
            start = 0
        else:
            print '.\n.\n.'
        if(end>lines.__len__()):
            end = lines.__len__()
        for i in range(start,end):
            line = lines[i]
            if(i == index):
                self._print("%d.%s" % (i+1,line),'highlight','black','yellow')
            else:
                print ("%d.%s" % (i+1,line))
        if(end < lines.__len__()):
            print '.\n.\n.'

    def _printCompare(self):
        '''
        打印lines的idx，和flines的fidx附近前后五行，作为对比
        :return:
        '''
        table = PrettyTable([self.path,self.fpath])
        table.align[self.path] = 'l' #左对齐
        table.align[self.fpath] = 'l'
        count = 5
        start = self.idx - count
        fstart = self.fidx - count
        end = self.idx + count + 1
        fend = self.fidx + count + 1
        for j in range(2):#两次调整start
            maxstart = max([start, fstart])
            if (maxstart < 0):
                start -= maxstart
                fstart -= maxstart
                end -= start
                fend -= start
            if(j==1):
                break
            minoverflow = min([end - self.lines.__len__(), fend - self.flines.__len__()])
            if (minoverflow > 0):
                end -= minoverflow
                fend -= minoverflow
                start -= minoverflow
                fstart -= minoverflow
            else:
                break
        i = start
        fi = fstart
        while(i < end):
            if(i >= 0 and i <self.lines.__len__()):
                line = self.lines[i]
            else:
                line = '\033[1;35;40m【超出文件边界】\033[0m'
            if (fi >= 0 and fi < self.flines.__len__()):
                fline = self.flines[fi]
            else:
                fline = '\033[1;35;40m【超出文件边界】\033[0m'
            line = "%d.%s" % (i + 1, line)
            fline = "%d.%s" % (fi + 1, fline)
            if (i == self.idx):
                line = '\033[1;30;43m' + line
                fline = fline + '\033[0m'
                #self._print("%d.%s" % (i + 1, line), 'highlight', 'black', 'yellow')
            else:
                pass
                #print ("%d.%s" % (i + 1, line))
            table.add_row([line, fline])
            i += 1
            fi += 1
        print table

    def _error(self,msg,code=0,*kwargs):
        self._msg(msg, 'highlight', 'red', 'white')
        class difffileException(Exception):
            def __init__(self,args):
                Exception.__init__(self,'difffile.' + args)
        if(code == 0):
            raise difffileException(msg)
        if(code == 1):#输出附近行
            self._printAround(kwargs[0],kwargs[1])
            raise difffileException(msg)
        elif(code==2):
            kwargs[0]._printCompare()
            raise difffileException(msg)
        elif(code==3):
            kwargs[0]._printCompare()
        else:
            pass

    def execute(self,root,objfile=''):
        '''
        开始修改原文件
        :param root: 原文件所在根目录
        :param objfile: 目标文件路径，设置则不使用diff文件中的目标路径
        :return:0成功 非0失败
        '''
        self.fpath = ''
        self.fidx = 0
        self.idx = 0
        blockheadidx = 0
        info_nrows_before_modifying = 0 #@@后面的行数(修改前)
        info_nrows_after_modifying = 0 #修改后的行数
        step = 1
        self.flines = []
        cmd = ''
        isMultiLineCmd = False
        while(self.idx < self.lines.__len__()):
            line = self.lines[self.idx]
            if (step == 1):
                if(line == ''):
                    pass
                elif(line[0] == '#'):
                    #处理宏定义
                    if(line[0:8] == '#include'):
                        line = re.search(r'<([^>]+)>',line).group(1)
                        self._include(self.dir + line,root)

                if(line[0:3] == '+++'):
                    # 获取原文件路径
                    # 路径
                    if(objfile == ''):
                        self.fpath = re.search(r'/(.*)$', line).group(1)
                        self.fpath = self.fpath.replace(r'\\', '/')
                    else:
                        self.fpath = objfile
                    if(self.fpath == 'script'):#脚本文件
                        self.type = 'script'
                        self.fpath = '/tmp/diffexe.script'
                        self._msg("正在执行...", 'highlight', 'pink', 'blue')
                        pass
                    else:
                        self.fpath = root + '/' + self.fpath
                        self.fpath = scriptrunner._replacevar(self.fpath)
                        self._msg("正在修改 %s ..." % (self.fpath), 'highlight', 'green', 'blue')
                    fbkuppath = self.fpath + '.bkup'
                    self.ftmppath = self.fpath + '.tmp'
                    # 备份原文件
                    if (not os.path.exists(fbkuppath)):
                        if (os.path.exists(self.fpath)):
                            shutil.move(self.fpath, fbkuppath)
                        else:
                            # 不存在则创建
                            file(fbkuppath, 'w').close()
                    # 读取原始文件
                    self.flines = file(fbkuppath, 'r').read().split('\n')
                    # 打开输出文件
                    self.fout = file(self.ftmppath, 'w')
                    step = 2
                self.idx += 1
            elif(step == 2):
                #查找块
                if (line[0] == '+' or line[0] == '#'):
                    # 没有块头，原文件无内容 或 完全覆盖原文件时允许这种情况
                    info_nrows_before_modifying = 0
                    info_nrows_after_modifying = self.lines.__len__() - self.idx
                    step = 3
                    nrows_origin = 0
                    nrows_added = 0
                    #清空原文件
                    self.flines = []
                elif (line[0:2] == '@@'):
                    #记录block头索引
                    blockheadidx = self.idx
                    # 获取@@内的修改信息
                    info = re.search(r'@@([^@]+)(@@)', line).group(1)
                    info = re.findall(r'([0-9]+)', info)
                    if (info.__len__() != 4):
                        self._error('错误：@@...@@格式不正确')
                    info_fidx_start = int(info[0]) - 1  # @@中的行号从1开始计算
                    if(info_fidx_start==-1):#空文件fpath
                        info_fidx_start = 0
                    info_nrows_before_modifying = int(info[1])
                    info_nrows_after_modifying = int(info[3])
                    if (self.fidx < info_fidx_start):
                        # 把源文件中@@...@@之前的行都写出到文件
                        for self.fidx in range(self.fidx, info_fidx_start):
                            line = self.flines[self.fidx]
                            self._writeFLine(line)
                        self.fidx = info_fidx_start  # 原文件跳到@@...@@后面的那行
                    else:
                        # 跳过diff文件中，原文件已写出的部分
                        nrows_written = self.fidx - info_fidx_start
                        self.idx += nrows_written
                        info_nrows_before_modifying -= nrows_written  # 去掉重叠行
                        info_nrows_after_modifying -= nrows_written  # 去掉重叠行
                    step = 3
                    nrows_origin = 0
                    nrows_added = 0
                    self.idx += 1
                elif (line[0] == ' '):
                    # 格式错误，不允许在@@之前出现行首空格
                    self._error('错误：diff文件格式不正确，不允许在@@之前出现行首空格！')
                if(self.idx == self.lines.__len__()-1):
                    self._error('错误：diff文件{}格式不正确，没有找到@@或+标记！'.format(self.path))
            elif(step == 3):
                if(line.__len__() == 0):
                    if(self.idx+1 == self.lines.__len__()):
                        # diff文件尾部，检验修改
                        mask = '@'
                    else:
                        #空行
                        mask = ' '
                        fline = self.flines[self.fidx]
                else:
                    # 取出可能存在的行尾命令
                    regex = re.compile(r'(.*?(?=' + LINE_CMD_MASK + '))' + LINE_CMD_MASK + '(.*)')
                    rslt = regex.search(line)
                    cmdline = ' '
                    if (rslt != None):
                        line = rslt.group(1)
                        cmdline = rslt.group(2)

                    if(isMultiLineCmd):
                        if(cmdline[0] == '>'):#多行命令结束
                            isMultiLineCmd = False
                            scriptrunner._exec(cmd)
                        else:
                            cmd += line + '\n'
                        mask = '#'
                    else:
                        if(cmdline[0] == '<'):
                            isMultiLineCmd = True
                            cmd = ''
                            mask = '#'
                        else:
                            # 开始修改
                            mask = line[0]
                            line = line[1:]
                            if (self.fidx < self.flines.__len__()):
                                fline = self.flines[self.fidx]
                            else:
                                fline = '\n'  # 原文件已到结尾，不允许 ' '匹配 和 '-'删除操作。
                            #执行命令
                            cmd = cmdline
                            if (cmd.strip() != ''):
                                # 执行命令
                                scriptrunner._exec(cmd)
                            # 替换line中的变量
                            line = scriptrunner._replacevar(line)

                if (mask == ' '):
                    # 检验
                    self._checkLine(line, fline)
                    nrows_origin += 1
                    # 写出行
                    self._writeFLine(fline)
                    self.fidx += 1
                elif (mask == '-'):
                    # 检验
                    self._checkLine(line, fline)
                    # 删除行
                    nrows_added -= 1
                    nrows_origin += 1
                    self.fidx += 1 #后移指针
                    pass
                elif (mask == '+'):
                    # 添加行
                    if (0 and not self._isSameStr(line,'') and line.__len__()>10):#可以在空行附近增加空行
                        if (self._isSameStr(line, fline)):
                            self._error('警告：要添加的行【%s】在原文件%s中已存在，这可能由重复修改导致！' % (line,self.fpath), 3, self)
                            choice = raw_input('继续修改可能出错，是否继续？s跳过此行。【y/N/s】：')
                            choice = choice.lower().strip()
                            if (choice != 'y'):
                                if (choice == 's'):
                                    self.idx += 1
                                    continue
                                else:
                                    return 0
                    self._writeFLine(line)
                    nrows_added += 1
                elif (mask == '#'):
                    # 注释
                    pass
                elif(mask != '@'):
                    self._error('错误：第{}行行首，非法字符【{}】！'.format(self.idx + 1, mask),1,self.idx,self.lines)

                if(mask == '@' or self.idx == self.lines.__len__() - 1):
                    #块修改完毕，进入第二步检测是否有下一块
                    #或最后一行
                    if(self.type == 'script'):
                        self.succexed = True
                        self._msg('执行完成！', 'default', 'pink', 'white')
                        return 0
                    else:
                        step = 2
                        # 检验修改
                        if not (info_nrows_before_modifying == nrows_origin
                                or info_nrows_after_modifying == (nrows_origin + nrows_added)):
                            info = '错误：修改行数不匹配。\n' + \
                                   '--diff携带信息：修改前行数【{}】；修改后行数【{}】\n' + \
                                   '--实际修改结果：修改前行数【{}】；修改后行数【{}】'
                            info = info.format(info_nrows_before_modifying, info_nrows_after_modifying, nrows_origin,
                                               nrows_origin + nrows_added)
                            self._error(info, 1, blockheadidx, self.lines)
                        if (self.idx + 1 == self.lines.__len__()):
                            # 修改完成
                            # 写出flines剩余行
                            while (self.fidx < self.flines.__len__() - 1):  # 不写出EOF
                                self._writeFLine(self.flines[self.fidx])
                                self.fidx += 1
                            self.fout.close()
                            self._msg('修改完成 %s' % (self.fpath), 'default', 'blue', 'white')
                            shutil.move(self.ftmppath, self.fpath)
                            self.succexed = True
                            return 0
                else:
                    self.idx += 1
        if(self.fpath == ''):
            self._error('错误：%s中没有包含目标修改文件的路径信息！'%(self.path))