# AutoReplaceClassName
自动替换类名，适用于OC代码，可以同时修改类/文件名，xib的名字
## Usage
#### 将脚本放到要处理代码的目录的同级，注意只会处理与脚本同级的其他目录里面的文件

#### 设置好脚本的几个全局参数，终端直接运行：python rain.py, 修改的记录保存在 classnamesave.txt

## 参数说明：

#### -copy 复制所有零散的文件到 newFileFolder 里面，等待处理

#### -r 对newFileFolder 里的文件执行替换操作
> 不传参数，默认先copy，再replace
> newFileFolder 的设置在脚本里
