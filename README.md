# Preface of easymake-yaml

#### Above All
This will be a auto-make tool for c/c++, and I would accomplish it when I am not busy.

The Project will be written by Python 3.6, meaning it would not support to run with Python 2.7 and older python version.

I do not make the decision what the compiling method is, but the project will use the `.yaml` as configuration file, like the cmake dependents on `CMakeLists.txt`.

#### Reason of Using YAML

As well known, `yaml` is a friendly markable language to read and write, and python has a mature library to prase it. 

I was enlighten by netplan when I configured the Static IP on Ubuntu Server 18.04 --- the netplan used `.yaml` as configuration file for the highlysimplified and free syntax.

#### Why to Intend to Develop This Tool?

Well, I am using another easymake tool named [emake](https://github.com/skywind3000/emake). It is a good tool for c/c++, but too old is its fetal problem --- It even cannot run with python 3 runtime! So I need a totally new tool to take it place.

#### Compiling Method
There are two methods to implement, I name one of them as cmake-style, and the other as manual-style.

Obviously, the cmake-style will generate the `makefile` and call `gnu make`, `nmake` or other building tool to generate executable binary file. And manual-style is simulation of inputing `gcc` command to CLI.

If I choose the cmake-style, I would have no time to patch all compilers except the GCC and Clang(this tool will be mainly used for c/c++ with GCC and Clang). If the other will be chosen, there is a fetal shortcoming that it hardly to work on parallel cores.

But I will try them all and conclude a best resolution if I have enough time on it.

#### Time Record

+ 2019-07-31 Build this Project on Github
