# Deign Manual of EasyMake-YAML Rebuilding

#### preface
该文档是对easymake-yaml重构时编写的设计手册，这里将会包含该项目的设计思想、实现细节等等一些列深层次的内容，因为在原有基础上进行迭代，这里的技术路线大致可以表示为：
```mermaid
graph LR;
p1("读取YAML文件") ==> |pyyaml| p2(YAML数据字典) ==> p3(Makefile)
```

在两年前的最初版本中，我曾经使用过KMP暴力搜索算法和正则表达式来处理yaml文件，都没有收到较好的结果，唯独使用`pyyaml`的版本获得了较大提升，因此这一版继续沿用这种方法

另外，easymake-yaml依赖的python版本为`3.8.3`，在重构完成后，我将会测试在低版本解释器上的运行状况，后续详见本文[兼容性测试](#兼容性测试)

#### Makefile
本项目对Makefile的设计，主要面向GNU make，即本项目主要面向GCC/Clang/Msys2(Mingw)设计，在项目设计中也采用了一些GNU Compiler Collection的一些私有特性以便编译器自行推导依赖

##### GCC中的依赖推导
##### Makefile的设计原则
该项目中的Makefile的设计中，主要使用隐式规则，以减少Makefile的大小，降低其复杂度

关于Makefile中的隐式规则，详见[跟我一起写Makefile - 陈皓](https://seisman.github.io/how-to-write-makefile/overview.html)，此处不再进行过多的讨论

除此之外，Makefile的设计还应遵循以下规则：
+ 在关键处进行格式化的注释
+ 避免和环境变量中适用于Make的变量冲突
+ 按照Makefile标准对C/C++相关变量进行命名，其他混编语言按照另外一种统一的格式
+ 至于其它方面，待想起来再补充

#### 对YAML文件的处理

此处记录对YAML文件中一些字段进行的特殊处理

##### `int`字段
对于`int`字段的处理，要较为谨慎：
1. 若未声明该字段，则不做任何处理
2. 若声明该字段，则由Python负责建立该文件夹，以及复制项目结构至`int`声明的目录下

但是无论如何，在Makefile中都将生成`$(OUTPUT_DIR)`变量，用于声明编译输出的目录

##### `sources`字段（global）
考虑到C/C++文件拥有很多不同的后缀名，例如`.c/.C/.cc/.cxx/.cpp/.CPP`等

在Makefile中生成隐式规则时，将会形成以下的形式（以`.cc`后缀为例）：
```makefile
%.o: %.cc
	$(CC) -c $(CFLAGS) $< -o $@ -MMD -MP -MF $*.d 
```

显然针对所有后缀，这样一条隐式规则是不够用的，因此在生成Makefile之前，将对该字段的所有值进行遍历，取得其后缀列表并根据该列表生成相应的隐式规则

##### `compiler::command::cc`字段
该字段用于指示C语言编译器

**是否应该允许自行指定c++编译器？开放该功能是否有意义？**


#### 兼容性测试
待完成