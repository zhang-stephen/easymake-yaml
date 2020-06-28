# EasyMake-YAML: a Flexible Makefile Generator for C/C++/ASM and other Languages[^1]

[^1]: created by vscode with plugin MPE, Stephen Zhang &copy; All right reserved 

# Preface
2018年四月份，我在使用[emake](https://github.com/skywind3000/emake)的过程中萌生了要对这个工具进行改进的念头，于是用了三个月的时间写了一个使用YAML文件作为配置文件的小工具，就是该项目的前身

由于当时只是把它作为一个玩具，所以没有引起我太多的重视以致于代码丢失到只留下一份[用户手册](./docs/olds/user_manual_2018.md)，这件事情令我追悔莫及，一直计划重写该工具，直到今天，即2020年6月份，才终于动手重写该工具

好了言归正传，easymake-yaml是一个简单而灵活的Makefile生成器，作为一众Make工具的后来之辈，它的优点是很明显的；当然一个工具过于简单，也意味着它无法胜任复杂的工作——我对easymake-yaml的期许大约是可以完成中等规模的C/C++项目构建，并支持部分语言混编就可以了

使用GNU Make时头昏脑涨、呼吸困难？认为Makefile写法过于反人类？头文件依赖太烦人？多核并行编译搞不定？也许easymake-yaml可以帮你解决这些问题：
+ 使用简单：只需声明源文件、编译依赖和输出目标就可以编译，easymake-yaml为你屏蔽一切细节
+ 依赖分析：自动分析源文件依赖，从此告别依赖黑洞
+ 输出模式：支持可执行文件、静态/动态链接库和用于嵌入式平台的裸机二进制文件输出
+ 多核编译：任何一个Make工具都支持
+ 结构精简：只需一个emake.py文件
+ 交叉编译：只需简单配置一下编译器，任何平台都不在话下
+ 语言支持：C/C++/ASM以及其他可以和C/C++混编的语言（需要提前安装其编译器）
+ 工具支持：GCC/LLVM/msys2（MinGW）
+ 系统支持： Windows/Linux/OS X/BSD等，只需支持python3即可使用该工具

easymake-yaml，为快速开发而生

#### Install
- [ ] 待完成，`emake.py`功能重写的差不多时我会更新安装方法
理论上可以做到只需执行`emake`命令即可完成编译

#### Tutorial
假设项目中存在三个源文件，分别是`main.cc`、`foo1.cc`、`foo2.cc`，需要将其编译为可执行文件，那么只需按照示例书写配置文件即可：
```yaml
# 输出模式：exec(可执行文件)/lib(静态链接库)/dll(动态链接库)/bin(裸机二进制文件)四选一
mode: exec

# 要编译的源代码(只需写成YAML接受的数组格式即可)
sources: main.cc, foo1.cc, foo2.cc

# 目标平台：win/unix/none
platform: win

# 输出文件名(目标平台为win时自动添加.exe后缀，为none时请自行添加后缀)
output: debug
```
然后在项目根目录下将该文件保存为`easymake.yml`或者`emake.yml`，在命令行中(以Powershell为例)输入：
```powershell
PS X:/path/to/project/ > emake 
```
等待执行完毕，即可在该路径下看到`debug.exe`已被生成

#### Documents
easymake-yaml会在项目根目录下自动搜索名为`easymake.yml`或者`emake.yml`的文件，当然也可以通过命令行选项使用其他名字的配置文件

在配置文件中，还可以通过其他字段进行更为详细的设置，下面将对它们进行介绍

##### sources
`source`字段用于指定编译目标依赖的源文件，可以如同[Tutorial](#Tutorial)中一样罗列源文件，也可以指定源文件所在的目录，例如：
```yaml
sources: 
    - module1/
    - main.cc
```
这是YAML语法中另一种数组的写法，可以看到该配置中我们直接把模块`module1`目录写入配置中；源码目录必须以`/`或者`**`结尾，否则会被忽略，建议使用相对路径形式，相对路径的起点即为项目根目录；在该目录中，以`.c/.C/.cc/.cxx/.cpp/.CPP`结尾的文件将被视为C/C++源文件

如果`sources`中某个值被指定为`path/to/**`这样的形式，那么将对该目录下所有的子目录进行递归搜索，如果无法搜索到C/C++源文件则会生成一个空值，但是不会引发错误

如果声明的目录不含`**`且以`/`结尾，那么只在该目录中进行源文件的查找；如果`**`出现在目录的开始或者中间，例如`path/to/**/moduleXX/`，那么会递归查找`moduleXX`目录并在该目录下查找源文件，而不会递归搜索`ModuleXX`目录；而且如果存在多个`moduleXX`目录，那么easymake-yaml将在第一次查找成功后停止查找

##### headers
该字段用于指示要使用的头文件，在生成Makefile时只会被转换为`-i`选项，这意味着**不能**在该字段下添加额外的头文件搜索目录，同`sources`字段，可以在该字段下添加多个头文件：
```yaml
headers: cstdio, ../include/linux.h, /path/to/include/ffmpeg.h
```
添加头文件时，并不分辨后缀，可以使用相对路径或者绝对路径

##### link
`link`字段用于指示要链接的静态链接库，可以在该字段下添加多个静态链接库；如果要链接的库位于编译器的搜索目录下或者环境变量内，则可以省去父目录；如果要链接的库符合GNU命名约定，例如`libm.a`，则可以简写为`m`:
```yaml
link: m, stdc++, filesystem, /path/to/lib/mylib.a
```
**注意：** 如果不指定`compiler`字段，则默认使用gcc进行编译，编译C++项目时必须增加`link`字段以链接`libstdc++.a`

##### compiler
`compiler`拥有几个子字段，用于配置编译器及其选项，这些子字段可以根据需要全部省去或保留部分：
```yaml
compiler:
    command:
        cc: gcc
        cxx: g++
        ar: ar
    flags: -std=c++17, -Wall, -O3, -g
    inc: /path/to/XX/include
    lib: /path/to/XX/libs
```

可以看到，该字段拥有四个子字段：
+ `command`字段用于指示默认的编译器(`cc/cxx`)和打包工具(`ar`)，前者用于编译源文件和链接二进制文件，后者用于将`.o`文件打包为静态链接库；二者均可省去，如全部略去则`command`字段可不写
在指示`cc/cxx`和`ar`的时候，可以使用相对路径或者绝对路径；如果要指定的工具位于环境变量内，可以只写命令名

+ `flags`字段为传递给`cc/cxx`字段的选项，如果需要更详细的设置，请单独声明`cflags/ccflags/arflags/ldflags`；这些字段中，`flags`的优先级最低——如果声明了`cflags`，那么`$(CC)`得到的参数将不会再来自于`flags`字段而是来自于`cflags`字段

+ `inc`字段为要搜索的额外头文件目录，同理`lib`是要进行搜索的额外的库文件目录，二者均可指定多个有效值，且不必以`/`结尾；同时，如果这两个字段的值以`**`结尾，则对该值声明的目录下所有子目录进行递归搜索
**在日常使用中，如无必要，尽量使用`inc`代替`headers`**

另外，可以只声明`cc/cxx`的其中一个字段，其他字段，例如`ar/cxx`（假设声明了`cc`），则可以由`cc`推导生成；但是该推导不会在只声明`ar`字段时发生

`command`字段中没有设置`ld`字段，因为最后目标文件(`exec`)的链接由`$(CC)`或者`$(CXX)`完成

##### extraCompiler
`extraCompiler`字段用于指示和C/C++的混编的代码的编译器，例如Assembly/Bison/Yacc等；该字段共拥有三个子字段：
```yaml
extraCompiler:
    "language ID":
        command: /path/to/yasm
        flags: ~
        sources: ~
```
值得注意的是`"language ID"`字段，该子字段可以配置为任意值，例如`YASM`，那么受其影响，其下的三个子字段在Makefile生成的变量值分别为`EXTRA_COMPILER_YASM`、`EXTRA_COMPILER_YASM_FLAGS`和`EXTRA_COMPILER_YASM_SRCS`

##### int
`int`字段用于指示编译时临时文件的存放目录，该目录由easymake-yaml而不是Make负责创建，在创建该目录时，该工具将会把项目根目录下的目录结构也复制到临时文件目录；如果不指定该值或者指定为项目根目录，则不会进行前述操作

另外，如果该字段的值被指定为`.git`、`.svn`、`.vscode`等等以`.`开头的目录，则会引发错误，使Makefile的生成中止，此限制是为了避免和某些IDE/Editor的配置文件夹冲突

**同时要注意，复制项目根目录下的目录结构时，所有以`.`开头的目录将被忽略**

##### subpath
`subpath`是类似于CMake中`add_subdirectory()`的语法，目前具体实现还在研究中，随后将会更新

至此所有主要的配置项都已介绍完毕了，如果需要更详尽的例子，请参考[测试用例](./test/README.md)

#### CLI Options
该工具提供了较为丰富的CLI Options，便于配合yaml文件对生成Makefile的过程以及其他方面进行配置，详细的选项及取值见下表

short | long | value | notes | status
:---| :--- | :--- | :--- | :---:
-f | --file | string | 使用指定的配置文件覆盖默认配置文件 | ongoing
-o | --output | string | 指定输出文件名 | ongoing
-c | --check-compiler| none | 该选项存在时检查**所有的`compiler`字段**指示的编译器是否存在 | ongoing
-b | --build | int | 此选项存在时在生成Makfile后尝试执行编译，其后的数字为编译时使用的核心数量，默认值为1 | ongoing
-e | --exec | string | 指定要使用的`make`工具，若不在环境变量内则要求完整路径 | ongoing
-n | --just-print | none | 该选项存在时，只打印要生成的Makefile而不进行生成 | ongoing
-l | --log | none | 该选项存在时，打印生成过程中的log | ongoing
-h/-? | --help | none | 该选项存在时，打印帮助内容并退出 | available
-v | --version | none | 该选项存在时，打印版本号并退出 | available

#### Road Map
这是一份计划中的开发路线：
TODO: 使用其他工具完成Road Map的绘制并添加至文档内

#### Change Logs

见[Change Logs](./docs/ChangeLog.md)
