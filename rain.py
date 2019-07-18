# encoding: utf-8

import re
import os
import shutil
import argparse

# 将脚本放到要处理代码的目录的同级，注意只会处理与脚本同级的其他目录里面的文件
# 设置好脚本的几个全局参数，终端直接运行：python rain.py, 修改的记录保存在 classnamesave.txt
# 参数说明：
# 不传参数，默认先copy，再replace
# -copy 复制所有零散的文件到 newFileFolder 里面，等待处理
# -r 对newFileFolder 里的文件执行替换操作

newPrenames = 'DL' #指定新的前缀
newFileFolder = 'newFileFolder' #处理后的文件放到这里， 与脚本同级目录

prenames = ['YY','GG'] #只会处理这些前缀的文件
_filterexts = ['h', 'm', 'mm', 'xib','pbxproj'] #只处理这些类型的文件
_filterdirs = ['xcassets','xcodeproj','xcworkspace','.git','Pods'] #这些类型的文件夹不处理

# 对于包含关系的词，替换时前面的优先级更高
endnames = {
            'ViewController':'Presenter',
            'View':'Content',
            'Controller':'Controller',
            'CellModels':'ItemDatas',
            'CellModel':'ItemData',
            'Cell':'Item',
            'Item':'Cell',
            'Model':'Data',  
            'ViewManager':'Provider',  
            'Manager':'Director', 
            'Helper':'Some',  
            'Utils':'Tools',   
            'Util':'Tool',
            'Alert':'Warn',      
            'Api':'Req',
            'AppDelegate':'AppDelegate',
            'Delegate':'Protocol',
            'URLActionHandler':'ProtocolEvent',
            'VideoGroup':'MovieDetail',
            'Video':'Movie'
            }
 
keywords =  {
            'Practice':'Training', 
            'Examine':'Testing',  
            'Exam':'Test', 
            'Study':'Xuexi', 
            'Kaoshi':'Ks',
            'Question':'Timu',
            'Qu':'Timu', 
            'Vip':'Member',   
            'Kemu':'Subject',    
            'BaseDrive':'Jichujiashi',   
            'Courseware':'Kejian',
            'Coureware':'Kejian',
            'Knowledge':'Point',
            'Error':'Mistake',
            'Main':'Primary',
            'Mine':'Wode',
            'Rank':'HOT',
            'Tiku':'QLib',
            'TrainingTopic':'Summary',
            'Traffic':'Transport',
            'Setting':'Config',
            'TuBiaoSuji':'IconsLook',
            }

copyCommand = '-copy'
_replaceCommand = '-r'
_classlist = []
_allfilepath = []
copycount = 0
def appendnosame(name):
    global allnamesnew
    if name in allnamesnew:
        name = name + 'ab'
        return appendnosame(name)
    else:
        allnamesnew.append(name)
        return name

def getclassname(line):
    name = line
    name = name.replace('@interface','' )
    name = name.split(':')[0]
    name = name.strip()
    return name
 
def getnewclassname(t):
    name = t
    for k, v in enumerate(prenames):
        if name.startswith(v):
            name = name.replace(v,'')
            break
    allkeys = keywords.keys()
    allkeys.sort(key=lambda x:len(x))
    allkeys.reverse()
    # print(allkeys)
    for k in allkeys:
        name = name.replace(k,keywords[k])
            
    good = False
    allkeys = endnames.keys()
    allkeys.sort(key=lambda x:len(x))
    allkeys.reverse()
    # print(allkeys)
    for k in allkeys:
        if name.endswith(k):
            name = name.replace(k,endnames[k])
            good = True
            break
    if not good:
        name = name + 'Class'
    name = newPrenames + name
    name = appendnosame(name)
    return name

def getallclass(path):
    global _classlist
    if os.path.isfile(path):
        name = os.path.splitext(os.path.basename(path))[0]
        if not name in _classlist :
            _classlist.append(name)
        name = ''
        file = open(path, "r")
        for index, line in enumerate(file.readlines()):
            line = line.strip()
            if line.startswith('@interface'):
                if line.find(':') == -1:
                    pass
                else:
                    name = getclassname(line)
                    if not name in _classlist :
                        _classlist.append(name)
        file.close()


def getfile_ext(path):
    if os.path.isfile(path):
        file_path = os.path.split(path)
        file = file_path[1]
        lists = file.split('.')
        file_ext = lists[-1]
        return file_ext

def prepareClass(path):
    if os.path.isfile(path):
        file_path = os.path.split(path)
        file = file_path[1]
        isgood = -1
        for k, v in enumerate(prenames):
            if file.startswith(v):
                isgood = 1
                break
        if isgood == 1:
            lists = file.split('.')
            file_ext = lists[-1]
            if file_ext=='h':
                getallclass(path)
            elif file_ext == 'm' and file_ext == 'mm':
                getallclass(path)

    elif os.path.isdir(path):
        for x in os.listdir(path):
            prepareClass(os.path.join(path,x))

def copyfilestoonefolder():
    global copycount
    for path in _allfilepath:
        if os.path.isfile(path):
            file_path = os.path.split(path)
            file = file_path[1]
            isgood = 1
            # for k, v in enumerate(prenames):
            #     if file.startswith(v):
            #         isgood = 1
            #         break
            if isgood == 1:
                target = os.path.join(targetfolder,file)
                if os.path.exists(target):
                    os.remove(target)
                copycount += 1
                # print('copyed>>>>' + file)
                shutil.copyfile(path, target)
 
def replacetext(text1,text2):
    print('<replace> ' + text1 + ' <use> ' + text2)                      
    for path in _allfilepath:
        f = open(path,'r+')
        all_the_lines=f.readlines()
        f.seek(0)
        f.truncate()
        for line in all_the_lines:
            if  line.find(text1) != -1 and line.find('#import <') == -1:
                line = line.replace(text1,text2)
                # xib2 = 'loadNibNamed:@"' + text2 + '"'
                # xib1 = 'loadNibNamed:@"' + text1 + '"'
                # line = line.replace(xib2, xib1)
            f.write(line)
        f.close()

def getAllFilePath(apath):
    if os.path.isfile(apath):
        ext = getfile_ext(apath)
        if ext in _filterexts:
            _allfilepath.append(apath)
    elif os.path.isdir(apath) and os.path.basename(apath) not in _filterdirs:
        for x in os.listdir(apath):
            getAllFilePath(os.path.join(apath,x))

def replace():
    classnewnamelist = []
    classfilelist = []
    classfilelistnew = []

    for x in _classlist:
        newname = getnewclassname(x)
        classnewnamelist.append(newname)

        for path in _allfilepath:
            filename = os.path.basename(path)
            if filename.find(x) != -1:  
                classfilelist.append(path)
                classfilelistnew.append(path.replace(x,newname))
    # print(_allfilepath)
    # print(classfilelistnew)
    for k,v in enumerate(_classlist):
        log = v + ' ->>>> ' + classnewnamelist[k] + '\r\n'
        savefile.write(log)
      #  print(log)
        replacetext(v , classnewnamelist[k])
    for k,path in enumerate(classfilelist):
        newpath = classfilelistnew[k]
        # print(path)
        # print(newpath)
        if os.path.exists(path):
            os.rename(path, newpath)

def parse_args():
    parser = argparse.ArgumentParser('批量修改类及文件')
    parser.add_argument(_replaceCommand, dest='replace', required=False, help='生成新的类名并替换掉', action="store_true")
    parser.add_argument(copyCommand, dest='copyto', required=False, help='将一些分散的文件统一拷贝到一个文件夹下', action="store_true")
    args = parser.parse_args()
    return args


def main():  
    app_args = parse_args()
    global command
    command = _replaceCommand
    global files 
    files = ''
    if app_args.copyto:
        command = copyCommand
    else:
        pass

    path = os.path.dirname(os.path.realpath(__file__)) 

    global targetfolder 
    targetfolder = os.path.join(path,newFileFolder)

    global podfolder 
    podfolder = os.path.join(path,'Pods')

    savepath = os.path.join(path,'classnamesave.txt') 
    if os.path.exists(savepath):
        os.remove(savepath)
    global savefile
    savefile = open(savepath,'w')

    if not os.path.isdir(path) and not os.path.isfile(path):
        print('your path is invalid')  
        return False
    print('your path is:' + path) 
    global allnamesnew
    allnamesnew = [] 
    global copycount
    copycount = 0
    global _classlist
    _classlist = []

    global _allfilepath
    _allfilepath = []

    if command == copyCommand :
        if os.path.exists(targetfolder):
            shutil.rmtree(targetfolder) 
        os.mkdir(targetfolder)
        getAllFilePath(path)
        copyfilestoonefolder()
        print ('total copy file>>>>' , copycount)
    elif command == _replaceCommand and not files == '':
        getAllFilePath(targetfolder)
        _classlist =  files.strip().split(',')
        replace()
    else:
        if os.path.exists(targetfolder):
            shutil.rmtree(targetfolder) 
        os.mkdir(targetfolder)
        getAllFilePath(path)
        copyfilestoonefolder()
        _allfilepath = []
        getAllFilePath(targetfolder)
        prepareClass(targetfolder)
        replace()

main()  
