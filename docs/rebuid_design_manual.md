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

#### 对YAML文件的处理

#### 兼容性测试
待完成