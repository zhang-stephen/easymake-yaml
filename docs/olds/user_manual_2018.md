# User Manual of easymake-yaml[^1]

[^1]: 2018-04-11，于长江大学电子信息综合创新实验室，张璞

#### Preface 
easymake-yaml是一个简单的、跨平台的、面向C/C++开发的Makefile生成工具，正如它的名字一样，该工具使用YAML作为配置文件，通过对YAML中各字段的解析，生成一份简明的Makefile（for gmake）

该工具会在项目根目录下搜寻名为`easymake.yml/emake.yml`的配置文件，生成的Makefile也会放置在同一目录下

#### 简单示例
如下是一个简单的配置文件示例，展示了配置文件中必须的字段：
```yaml
# the simple example of easymake.yml

# specify the output filename
output: proj-xxxx-debug

# specify the target type(executable|static lib|dynamic lib)
mode: exec

# files dependent on compiling(.h/.hpp|.c/.cpp|.a/.lib)
sources: main.cc, src1.cc, src2.cc, module1/, module/**
```

如上，可以看到，共有三个核心字段，这些字段缺少任意一个都无法正常生成Makefile

其中，`output`字段指示了编译目标的名字（不含后缀名）

`mode`字段指示了编译目标的类型，它是一个Enumerate类型的值，可选的目标类型分别为可执行文件`exec`、静态链接库`lib`和动态链接库`dll`；设置为None时可以用于编译arm Cortex-M系列单片机的裸机程序（需要声明`compiler`字段）

`sources`字段指示了编译目标的依赖，这是一个列表属性，可以以YAML的形式指定多个值，其中以`/`结尾的值代表这是一个目录，其中所有的源文件（不包括子目录）都要参与编译，而以`**`结尾则表示要递归搜索该目录下所有的子目录，将其中的源文件添加至Makefile中

#### 非核心的字段
以上核心字段只能实现简单的项目编译，若要实现更复杂的功能，则需要这些非核心的字段

##### 编译依赖
关于编译依赖的字段还有`header`和`link`，前者指示编译时依赖的头文件路径（具体到头文件而非其所在的目录），后者指示编译时依赖的静态链接库，二者都是列表类型的字段

其中，`link`的配置可以使用遵循GNU约定的库名，也可以使用绝对路径或相对路径指明要连接的库的具体位置，例如：
```yaml
link: m, pthread, /path/to/libssl.a
```
前两个是遵循GNU约定的静态库，即`libm.a`和`libpthread.a`，后者则是库文件的完全路径，这两种配置都是允许的

##### 编译器配置
编译器配置有两种，分别是默认编译器配置`compiler`和额外的编译器配置`extraCompiler`，二者均拥有子字段，下面针对它们进行说明

###### `compiler`字段
该字段用于配置默认的C/C++编译器，下面的实例中展示了它拥有的子字段和配置方法
```yaml
compiler:
	# the command used to call compiler
	command: 
		cc:	/path/to/clang++		# for C Compiler
		ar:			# for archive file generator

	# flags will be passed to compiler
	flags: --standard=c++17, -g, -O3, -Wall

	# the extra path to search C/C++ header files
	inc: ~

	# the extra path to search C/C++ static libraries
	lib: ~
```
如上，`compiler`拥有数个子字段，所有的子字段一起更次级的子字段都是可选的

`command`字段拥有两个子字段，其中`cc`用于声明本次编译要使用的编译器，`ar`用于声明生成静态链接库的打包工具，如果不需要生成静态链接库，则可以忽略；如果要使用的工具不在系统变量内，则需要声明完整路径

在一种特殊情况下，如果声明了`subpath`字段，且`subpath`字段声明的编译模式为`lib`时，如果不使用系统默认的打包工具，则必须声明`ar`字段

`inc`和`lib`字段用于声明搜索额外头文件和库文件的目录，可以使用相对路径或者绝对路径

###### `extraCompiler`字段
该字段用于配置和C/C++混编的语言及其编译器，例如yacc/bison和Assembly，一个简单示例如下：
```yaml
extraCompiler:
	- YASM:			# extra language id
		command: /path/to/yasm
		flags: ~
		sources: ~

	- BISON:
		command:
		flags:
		sources:
```

不论要配置多少种与C/C++混编的语言，在`extraCompiler`字段下都要写作如上数组的形式，否则在文件解析中会抛出错误

如上所示，字段`YASM`和`BISON`是区分不同编程语言的ID，它们在最后生成的Makefile中会被声明为变量`EXTRA_COMPILER_YASM`和`EXTRA_COMPILER_BISON`，用于保存该字段下配置的`command`字段

在每个ID下的三种字段中，只有`flags`是可选字段，其他两种字段缺失将会引发报错，对文件的解析和生成将会立即停止

##### 临时文件夹
`int`字段用于声明编译时输出中间文件例如`*.o`文件的目录，若不声明则默认将中间文件存放在项目根目录中

##### 子文件夹
在项目根目录下的easymake的配置文件中允许存在`subpath`字段，用于声明根目录下的子目录，这些子目录可以拥有自己的编译模式和输出，最后生成`.o`或者`.a`文件用于连接到主文件的输出上

`subpath`字段支持相对路径和绝对路径，但是要求子文件下存在名为`subemake.yml`的配置文件，在生成Makefile时将检查此文件是否存在，若不存在则抛出错误

`subemake.yml`文件可以拥有以上除`subpath`外介绍的所有字段，但是在`mode`字段中只允许配置为`lib`（生成`.a`文件），或者`none`（生成`.o`文件），使用其他配置将会抛出错误；如果配置为生成静态链接库，则遵循GNU命名约定，生成的库文件为`libxxx.a`；如果配置为`none`，则会忽略`output`字段的内容

#### 命令行选项
easymake-yaml支持部分命令行选项，罗列如下


short | long | value type | note
:--|:--|:--|:--
-f | --file | str | 指定要使用的配置文件，忽略默认文件名
-o | --output | str | 指定输出文件名
-c | --check-compiler| boolean | 设置为`true`时检查依赖的编译器是否存在
-b | --build | int | 此选项存在时在生成Makfile后尝试执行编译，其后的数字为编译时使用的核心数量
-e | --exec | str | 指定要使用的`make`工具，若不在环境变量内则要求完整路径


#### 结语
该工具是一个非常简单的小工具，由于追求开发效率，因此选择使用Python进行开发

在进行迭代的过程中，一共经历了三次文件解析技术的变更：第一次使用字符串的**暴力搜索算法KMP**，用于匹配字段关键字；第二次使用**REGEX**进行关键字的解析，实现了一个无记忆的State machine，可惜同第一次尝试一样，效率虽有提升但是提升幅度有限；第三次使用了`pyyaml`库进行开发，将所有的字段及其数据转换为字符串放入字典中进行处理，由于大部分操作都是对字符串进行处理，因此效率提升不少，在生成Makefile时的逻辑也更清晰

这个工具是受到[emake](github.com/skywind3000/emake)项目的启发，在它的基础上重新开发，增加了一部分我认为更优秀的特性，同时选用YAML这种可读性更好的语言作为配置语言，也算是博采众家之长吧，该项目将在不久后开源到Github；在此勉励自己，**作为程序员，虽然不需要时时刻刻重新发明轮子，但是要有随时造轮子的能力！**