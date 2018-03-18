#coding=utf-8
import os
import re

import scriptrunner
from difffile import difffile

print '%'
print '%########################################################################'
print '%#----------------u-boot configuration v1.0------------------------------'
print '%# File Name: config_uboot.sh'
print '%# Author: chris'
print '%# mail: 1050243371@qq.com'
print '%# Created Time: Fri 09 Mar 2018 10:54:44 AM CST'
print '%#########################################################################'
#!/bin/bash
print '%'

DEFAULT_GIT="git://git.denx.de/u-boot.git"
#	下面的参数一般用在本脚本调试过程中
#	如果为空则在之后会提示用户进行输入
EDIT_UBOOT_NO=1				#默认编辑当前文件夹第${}个U-Boot
PROJECT_NAME="itop4412"		#默认项目名
ROOT_DIR = './'

#扫描当前文件夹下的u-boot
ubarr=()

uboots=[]

for home in os.listdir('./'):
    if(os.path.isdir(home)):
        path = home + '/include/u-boot'
        if (os.path.exists(path)):
            uboots.append(home)

if(uboots.__len__() > 0):
    print("-在%s中共扫描到%d个u-boot：" % (ROOT_DIR , uboots.__len__()))
    for i in range(uboots.__len__()):
        print("--%d、%s" % (i+1 , uboots[i]))
    if(EDIT_UBOOT_NO==0):
        uboot = input('-请选择一个u-boot来进行配置：')
    else:
        uboot = EDIT_UBOOT_NO
    if(uboot > uboots.__len__()):
        print "错误：输入不正确，程序中止！"
        exit(1)
    uboot -= 1
    uboot = uboots[uboot]
else:
    print "-请指定一个下载u-boot源码的远程git仓库："
    print "--（输入空将使用默认%s，输入q退出）" % DEFAULT_GIT
    giturl = input('--')
    if(giturl == 'q'):
        exit(0)
    elif(giturl.strip() == ''):
        giturl = DEFAULT_GIT
    os.system('git clone '+ giturl)
    uboot = re.search(r'[^/\s]+$',giturl).group(0)
    #开始配置u-boot

if(uboot.strip() == ''):
    raise Exception("错误：没有可以操作的u-boot，程序中止。")
else:
    uboot += '/'

os.system('clear')
print "----------正在编辑：%s----------" % uboot
if( PROJECT_NAME == ''):
    proj = input("-请输入项目名称：")
else:
    proj = PROJECT_NAME

#参照：http://blog.csdn.net/techping/article/details/69911634
#(一) 创建$proj板级目录
proju = proj.upper()
projl = proj.lower()
scriptrunner._addvar(('proju', proju), ('projl', projl))
cmd = 'cd ' + uboot + '\n'
cmd += \
'''
projl=%s
proju=%s
cp -raf board/samsung/origen board/samsung/${projl}
mv board/samsung/${projl}/origen.c board/samsung/${projl}/${projl}.c
mv board/samsung/${projl}/tools/mkorigenspl.c board/samsung/${projl}/tools/mk${projl}spl.c
#(二) 增加文件
cp include/configs/origen.h include/configs/${projl}.h
cp configs/origen_defconfig configs/${projl}_defconfig
cp arch/arm/dts/exynos4412-odroid.dts arch/arm/dts/exynos4412-${projl}.dts
touch arch/arm/mach-exynos/${projl}_setup.h
touch arch/arm/mach-exynos/board.c
'''%(projl,proju)

try:
    os.system(cmd)
except:
    pass

#(三) 修改文件
diffdir = ROOT_DIR + 'cfgubmodify/'

for path in os.listdir(diffdir):
    path = diffdir + path
    if(os.path.isfile(path)):
        file = difffile(path)
        if (file.isValidDIffFile()):
            file.execute(uboot)
        else:
            file._error('无效文件！',4)


