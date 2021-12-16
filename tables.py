import copy

# 一个符号的所有属性
# 构成：
# type, ... 
class NameProperty: 
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def get_type(self):
        return self.type
    def set_type(self, type):
        self.type = type
    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = value


# 所有符号的属性
# 要考虑作用域！
# 及时把退出作用域的符号 pop 出去；
# 还有符号重命名和覆盖的问题
class NameTable:
    # Name(str) : NameProperty , ...
    # 每一层一个 dict， 记录所有的符号
    # 查询的时候倒退回去查询
    # 退出的时候直接 pop
    def __init__(self):
        self.table = [{}]
        self.current_scope_level = 0

    def enterScope(self):
        self.current_scope_level += 1
    
    def exitScope(self):
        if self.current_scope_level == 0:
            raise BaseException("exitScope error")
        self.table.pop()
        self.current_scope_level -= 1
    
    def addGlobal(self, name : str, property: NameProperty):
        if(self.table[0].get(name) != None):
            raise BaseException("global name already exist")
        self.table[0].update({name : property})
    
    def addLocal(self, name : str, property: NameProperty):
        if(self.table[self.current_scope_level].get(name) != None):
            raise BaseException("local name already exist")
        self.table[self.current_scope_level].update({name : property})
    
    def getProperty(self, name : str):
        for i in range(self.current_scope_level, -1, -1):
            if(self.table[i].get(name) != None):
                return self.table[i].get(name)
        raise BaseException("name not exist")

# 类表
# 用来类的函数调用
class ClassTable:
    pass