# coding: utf-8
from collections import OrderedDict
import itertools
import os
from os import path

#
#   脚本工具：用代码生成类文件
#   代码设计思想：
#       级别大小：Package>Module>Class>Method ...均继承自CodeObject
#       都有children属性以保存子级别的类对象
#       每个类有自己特定的gen产生代码方法，同时可以定义其他特有的方法
#

class TabLevel():
    """ 缩进等级
    """
    NIL = 0 # 无缩进
    ONE = 1
    TWO = 2
    THREE = 3

class CodeBuilder(object):

    def __init__(self):
        self.code = []
        self.tab = "    "
        self.level = TabLevel.NIL

    def finished(self):
        """ 完成构建，返回完整的代码字符串
        """
        return "".join(self.code)

    def save(self, string):
        for line in string.split('\n'):
            self.code.append(self.tab*self.level + line + "\n")

    def newline(self, count=TabLevel.ONE):
        self.code.append("\n" * count)

    def indent(self, count=TabLevel.ONE):
        self.level += count

    def dedent(self, count=TabLevel.ONE):
        if (self.level - count) < 0:
            raise SyntaxError, "internal error in code generator"
        self.level -= count

#__________________________________________________#

class CodeObject(object):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, child, indent=TabLevel.ONE):
        self.children.append((child, indent))
        return self

    def add_newline(self):
        return self.add("\n")

    def gen(self):
        cb = CodeBuilder()
        for c, indent_count in self.children:
            cb.indent(indent_count)
            if isinstance(c, basestring):
                cb.save(c)
            else:
                cb.save(c.gen())
            cb.dedent(indent_count) # 缩进复原

        return cb.finished()


class Method(CodeObject):
    def __init__(self, name, *args, **kwargs):
        super(Method, self).__init__(name)
        self.args = list(args)
        self.named_args = OrderedDict(kwargs)

    def add_argument(self, *args):
        self.args.extend(args)

    def add_named_argument(self, **kwargs):
        self.named_args.update(kwargs)

    def gen(self):
        cb = CodeBuilder()

        header_pattern = "def %s(self, %s):"
        cb.save(header_pattern % (self.name, ", ".join(itertools.chain(self.args, self.named_args.iterkeys()))))
        body = super(Method, self).gen()
        if not body:
            body = "pass"
        cb.save(body)

        return cb.finished()

class InitMethod(Method):
    def __init__(self, *args, **kwargs):
        super(InitMethod, self).__init__("__init__", *args, **kwargs)
        for arg in itertools.chain(self.args, self.named_args.iterkeys()):
            self.add("self.%s = %s" % (arg, arg))

    def add_argument(self, *args):
        super(InitMethod, self).add_argument(*args)
        for arg in args:
            self.add("self.%s = %s" % (arg, arg))

class Class(CodeObject):
    def __init__(self, name, super_name="object"):
        super(Class, self).__init__(name)
        self.super_name = super_name
        self.depends = []
        self.add("class %s(%s):" % (self.name, self.super_name), TabLevel.NIL)

    def add_depend(self, model_name):
        self.depends.append(model_name)

class Module(CodeObject):
    def __init__(self, name):
        super(Module, self).__init__(name)
        self.add("# coding: utf-8")
        self.add_newline()

    def add(self, child, indent=TabLevel.NIL):
        return super(Module, self).add(child, indent)

class Package(CodeObject):
    def __init__(self, name):
        super(Package, self).__init__(name)
        self.name = name
        self.add(Module("__init__"))

    def add(self, child, indent=TabLevel.NIL):
        if isinstance(child, CodeObject):
            if child.name == '__init__':
                for old_child in self.children:
                    if isinstance(old_child, CodeObject) and old_child.name == '__init__':
                        self.children.remove(old_child)

        return super(Package, self).add(child, indent)

    def gen(self, base_dir=None):
        if os.path.exists(self.name):
            print u'存在 package:[%s]' % self.name

        if not base_dir:
            base_dir = path.abspath(os.getcwd())
        else:
            base_dir = path.abspath(base_dir)
        base_path = path.join(base_dir, self.name)

        if not path.exists(base_path):
            os.makedirs(base_path)

        print u'model配置文件输出路径为: %s' % base_path
        for module, _ in self.children:
            fn = path.join(base_path, module.name + ".py")
            if module.name == '__init__' and path.exists(fn):
                print u'文件已存在，将覆盖旧文件(不覆盖__init__.py文件)'
                continue

            with open(fn, "w") as f:
                f.write(module.gen())

def test():
    # define_________________________
    package = Package("test_models")
    md = Module("news")
    c = Class("News")
    m_hello = Method("hello", word="world")
    m_get = Method("get_field", "name")

    # build body_____________________
    # class
    c.add("var s = None")

    # method
    m_hello.add("print a")
    m_get.add("return self.fields[name]")

    # combine________________________
    c.add(InitMethod("title", "content", author="admin"))
    c.add(m_hello)
    c.add(m_get)
    md.add(c)
    package.add(md)

    # product________________________
    package.gen()


if __name__ == '__main__':
    test()
