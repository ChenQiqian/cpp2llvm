from antlr4 import *
from llvmlite.ir.values import ReturnValue

from src.cpp20Lexer import cpp20Lexer
from src.cpp20Parser import cpp20Parser
from src.cpp20ParserListener import cpp20ParserListener as cpp20Listener
from src.cpp20ParserVisitor import cpp20ParserVisitor as cpp20Visitor
from tables import *
from llvmlite import ir

double = ir.DoubleType()
int1 = ir.IntType(1)
int8 = ir.IntType(8)
int16 = ir.IntType(16)
int32 = ir.IntType(32)
int64 = ir.IntType(64)
void = ir.VoidType()

class myCpp20Visitor(cpp20Visitor):
    def __init__(self):
        super(cpp20Visitor,self).__init__()
        
        # llvm生成模块
        self.Module=ir.Module()

        # 待生成的llvm语句块
        # 每生成一块语句时，将当前语句块加到末尾，以self.Builder[-1]调用
        self.Builders=[]
        # 符号表
        self.symbolTable = NameTable()

    def getTypeFromText(name : str) :
        if(name == "int"):
            return int32
        elif(name == "int16"):
            return int16

    def visitVarDeclWithInit(self, ctx: cpp20Parser.VarDeclWithInitContext):
        '''
        对应语法：Identifier ASSIGN expression
        '''
        # print("varDeclWithInit")
        self.symbolTable.addLocal(ctx.Identifier().getText(),
            NameProperty(
                type= self.type,
                value=self.visit(ctx.expression())['value'])) # 只需要记录虚拟寄存器即可        
        

        return

    def visitVarDeclWithoutInit(self, ctx: cpp20Parser.VarDeclWithoutInitContext):
        '''
        对应语法：Identifier
        '''
        # print(f"varDeclWithOutInit: {ctx.Identifier().getText()}")
        
        self.symbolTable.addLocal(ctx.Identifier().getText(),
            NameProperty(
                type=self.type,
                value=None)) # 这里可能还是得给一个初始的值，但是也未必
        return

    def visitVariableDeclarator(self, ctx: cpp20Parser.VariableDeclaratorContext):
        '''
        对应语法 ：typeSpecifier variableDeclaration (COMMA variableDeclaration)* SEMI;
        '''
        # print("Variable Declaration")
        # print(f"{len(ctx.variableDeclaration())} variables: ",end='')

        # for declaration in ctx.variableDeclaration():
        #     print(declaration.getChildCount())
        
        self.type = self.visit(ctx.typeSpecifier())
        
        print("type:", self.type)

        for declaration in ctx.variableDeclaration():
            self.visit(declaration)

        del self.type
        return
    
    def visitArrayDeclarator(self, ctx: cpp20Parser.ArrayDeclaratorContext):
        '''
        对应语法：typeSpecifier Identifier LSQUARE DecimalLiteral RSQUARE (ASSIGN LBRACE expression (COMMA expression)* RBRACE)?;
        '''
        #数组长度
        ArrayLength = int(ctx.getChild(3).getText())
        print("arraylength: ",ArrayLength)
        #数据类型
        ArrayType = self.visit(ctx.getChild(0))
        LLVMArrayType = ir.ArrayType(ArrayType,ArrayLength)
        #数据标识符
        ArrayName = ctx.getChild(1).getText()
        #变量的声明
        if(self.symbolTable.current_scope_level == 0):
            NewVar=ir.GlobalVariable(self.Module,LLVMArrayType,name = ArrayName)
        else:
            Builder=self.Builders[-1]
            NewVar=Builder.alloca(LLVMArrayType,name = ArrayName)

        symbolProperty = NameProperty(LLVMArrayType,NewVar)
        self.symbolTable.addLocal(ArrayName,symbolProperty)
        ChildCount=ctx.getChildCount()
        if ChildCount > 5:
            #赋初值给数组中的元素
            ''''''
        return 

    def visitReturnStatement(self, ctx: cpp20Parser.ReturnStatementContext):
        '''
            对应语法： RETURN expression? SEMI;
        '''
        if(ctx.expression() is None):
            self.Builders[-1].ret_void()
        else:
            self.Builders[-1].ret(self.visit(ctx.expression())['value'])

    def visitFunctionParameter(self, ctx: cpp20Parser.FunctionParameterContext):
        '''
        
            对应语法：typeSpecifier Identifier;
        '''
        return {
            "name": ctx.Identifier().getText(),
            "type": self.visit(ctx.typeSpecifier())
        }

    def visitFunctionCall(self, ctx: cpp20Parser.FunctionCallContext):
        '''
        对应语法：functionCall : Identifier LPAREN (expression (COMMA expression)*)? RPAREN;
        '''
        Builder = self.Builders[-1]
        functionName = ctx.Identifier().getText()
        property = self.symbolTable.getProperty(functionName)
        # print(property.get_type())
        if(property.get_type().__class__.__name__ == ir.FunctionType.__name__):
            # 参数列表
            paramList = []
            for expression in ctx.expression():
                paramList.append(self.visit(expression)['value'])
            # 检查合法性
            print("paramList & argsList: ", paramList,property.get_type().args)
            if(len(paramList) != len(property.get_type().args)):
                raise BaseException("wrong args number")
            for real_param, param in zip(paramList,property.get_type().args):
                if(param != real_param.type):
                    raise BaseException("wrong args type")
            # 函数调用
            return Builder.call(property.get_value(), paramList, name='', cconv=None, tail=False, fastmath=())
        else:
            raise BaseException("not a function name")

    def visitFunctionDeclaration(self, ctx: cpp20Parser.FunctionDeclarationContext):
        #print(f"visitFunctionDeclaration: {ctx.Identifier().getText()}",) #test for debug
        '''
        对应语法：typeSpecifier Identifier '(' (functionParameter (COMMA functionParameter)*)? ')' block
        '''
        #函数名
        FunctionName = ctx.getChild(1).getText()
        #获取参数列表，填充到ParameterList里
        ReturnType = self.visit(ctx.getChild(0))
        ParameterList = []
        for param in ctx.functionParameter():
            ParameterList.append(self.visit(param))
        ParameterList = tuple(ParameterList)
        print(ParameterList)
        ParameterTypeTuple = (param['type'] for param in ParameterList)
        # if(ParameterList == []):
        #     ParameterList.append(None)
        #生成llvm函数
        LLVMFuncType = ir.FunctionType(ReturnType,ParameterTypeTuple)
        LLVMFunc = ir.Function(self.Module, LLVMFuncType, name=FunctionName)
        # 将函数原型存入符号表
        self.symbolTable.addGlobal(FunctionName,NameProperty(type = LLVMFuncType,value = LLVMFunc))
        #储存函数为block
        Block = LLVMFunc.append_basic_block(name="__"+FunctionName)
        Builder= ir.IRBuilder(Block)
        self.Builders.append(Builder)
        #进入作用域
        self.symbolTable.enterScope()
        #将函数形参存入符号表
        for param, argsValue in zip(ParameterList,LLVMFunc.args):
            self.symbolTable.addLocal(param['name'], NameProperty(param['type'], argsValue))
        #访问函数块，返回值到ValueToReturn
        ValueToReturn=self.visit(ctx.block())
        #可能还要强制加上一个ret void，不然不知道会不会有bug。。。
        # if(self.Builders[-1].)
        # self.Builders[-1].ret_void()
        #退出作用域
        self.symbolTable.exitScope()

        return {
            'type': ReturnType,
            'signed':True,
            'value':ValueToReturn
        }
    pass

    def visitTypeSpecifier(self, ctx: cpp20Parser.TypeSpecifierContext):
        '''
        对应语法：typeSpecifier : integerTypeSpecifier | realTypeSpecifier | booleanTypeSpecifier | charTypeSpecifier | voidTypeSpecifier;
        '''
        #TODO: 定义visitRealTypeSpecifier即后面类型的函数
        Type = self.visit(ctx.getChild(0))
        return Type
    
    def visitIntegerTypeSpecifier(self, ctx: cpp20Parser.IntegerTypeSpecifierContext):
        if(ctx.getText()== 'int' or ctx.getText() == 'long'):
            return int32
        elif(ctx.getText()=='short'):
            return int16
        elif(ctx.getText()=='longlong'):
            return int64

    def isExprJudge(self,realText):
        #没有处理 NOT_EQ中"not_equ"的情况
        if (realText == ">"):
            return True
        elif(realText == "<"):
            return True
        elif(realText == ">="):
            return True
        elif(realText == "<="):
            return True
        elif(realText == "=="):
            return True
        elif(realText == "!="):
            return True
        else:
            return False
    pass
    
    def isExprCal(self,realText):
        if (realText == "+"):
            return True
        elif(realText == "-"):
            return True
        elif(realText == "*"):
            return True
        elif(realText == "/"):
            return True
        elif(realText == "%"):
            return True
        else:
            return False
    pass   

    def isInt(self,llvmNum):
        if llvmNum['type']==int32 or llvmNum['type']== int64 or llvmNum['type'] == int16 or llvmNum['type'] == int8 or llvmNum['type'] == int1:
            return True
        return False

    def intConvert(self,src,target):
        Builder = self.Builders[-1] 
        if(target['type'].width >= src['type'].width): # 往大扩展   
            if(src['type'].width == 1):
                ValueToReturn= Builder.zext(src['value'],target['type'])
                return{
                    'type':target['type'],
                    'signed':src['signed'],
                    'value':ValueToReturn
                }
            else:
                if(src['signed']):
                    ValueToReturn = Builder.sext(src['value'],target['type'])
                else:
                    ValueToReturn = Builder.zext(src['value'],target['type'])
                return {
                    'type':target['type'],
                    'signed':src['signed'],
                    'value':ValueToReturn
                }
        else: # 往小了转换，其实是 undefined 行为
            ValueToReturn = Builder.trunc(src['value'],target['type'])
            return {
                    'type':target['type'],
                    'signed':src['signed'],
                    'value':ValueToReturn
            }
            
    def intToDouble(self,llvmNum):
        Builder = self.Builders[-1]
        if(llvmNum['signed']):
            ValueToReturn = Builder.sitofp(llvmNum['value'],double)
        else:
            ValueToReturn = Builder.uitofp(llvmNum['value'],double)
        return{
            'type':double,
            'value':ValueToReturn
        }

    
    def doubleToInt(self,llvmNum,target):
        Builder = self.Builders[-1]
        if(llvmNum['signed']):
            ValueToReturn = Builder.fptosi(llvmNum['value'],target['type'])
        else:
            ValueToReturn = Builder.fptoui(llvmNum['value'],target['type'])
        return {
            'type':target['type'],
            'value':ValueToReturn
        }
    

    def toBool(self,llvmNum):
        Builder = self.Builders[-1]
        if llvmNum['type'] == double:
            ValueToReturn = Builder.fcmp_ordered('==', llvmNum['value'], ir.Constant(int1,0))
        else:
            ValueToReturn = Builder.icmp_signed('==', llvmNum['value'], ir.Constant(int1,0))
        return{
            'type':int1,
            'signed':True,
            'value':ValueToReturn
        }

    def assignTypeConvert(self,left,right):
        # 赋值语句中用的类型转换
        # 强制把右侧的类型转换为左侧的类型
        if(left['type'] != right['type']):
            if(self.isInt(left) and self.isInt(right)):
                right = self.intConvert(right,left)
            elif(self.isInt(left) and self.isInt(right)==False):
                right = self.doubleToInt(right,left)
            elif(self.isInt(left)==False and self.isInt(right)):
                right = self.intToDouble(right)
            else:
                pass
        return left,right
    
    def exprTypeConvert(self,left,right):
        #left和right的符号类型不一致时，类型转换为一致，向大的类型转换
        #left,right可能的类型：int1,int8,int16,int32,int64,double...（暂时支持这几种）
        if(left['type']==right['type']):
            return left,right
        elif self.isInt(left) and self.isInt(right):
            if left['type'].width < right['type'].width:
                left = self.intConvert(left,right)
            else:
                right = self.intConvert(right,left)
        elif self.isInt(left) and right['type']==double: 
            left = self.intToDouble(left)
        elif left['type']==double and self.isInt(right):
            right = self.intToDouble(right)
        return left,right

    def visitExpression(self, ctx: cpp20Parser.ExpressionContext):
        # print(f"visitExpression:{ctx.getText()}, {ctx.getChildCount()}")
        ChildCount=ctx.getChildCount()
        Builder = self.Builders[-1]
        if(ChildCount == 1):
            grandChildren = ctx.getChild(0).getChildCount()
            if(grandChildren):
                '''
                对应语法：expression: Literals|functionCall;
                '''
                result = self.visit(ctx.getChild(0))
                return result
            else:
                '''
                对应语法：expression: Identifier
                '''
                symbol = self.symbolTable.getProperty(ctx.getText())
                return {
                    'name':ctx.getText(),
                    'type':symbol.get_type(),
                    'signed':symbol.get_signed(),
                    'value':symbol.get_value()
                }

        elif(ChildCount == 2):
            '''
            对应语法：expression: NOT expression
            '''  
            Builder = self.Builders[-1]
            result = self.visit(ctx.getChild(1))
            if result['type'] == double:
                ValueToReturn = Builder.fcmp_ordered('!=', result['value'], ir.Constant(int1,0))
            else:
                ValueToReturn = Builder.icmp_signed('!=', result['value'], ir.Constant(int1,0))
            return {
                'type':int1,
                'signed':True,
                'value':ValueToReturn
            }
          
        elif(ChildCount > 3):
            '''
            对应语法：expression: Identifier '[' DecimalLiteral ']'
            '''
            index = self.symbolTable.getProperty(ctx.getChild(0).getText())
            subscribe = int(ctx.getChild(2).getText())
            if(isinstance(index.get_type(),ir.types.ArrayType)):
                Builder = self.Builders[-1]
                Address = Builder.gep(index.get_value(),[ir.Constant(int32,0),ir.Constant(int32,subscribe)],inbounds=True)
                ValueToReturn = Builder.load(Address)
                print("call arrayItem",ValueToReturn)
                return{
                    'type':index.get_type().element,
                    'signed':True,
                    'value':ValueToReturn,
                    'address':Address
                }
            else:
                raise BaseException("the array isn't defined")

        elif(ChildCount == 3 and ctx.getChild(0).getText()=='('):
            '''
            对应语法：expression: '(' expression ')'
            '''
            result = self.visit(ctx.getChild(1))
            return result

        else:
            Operation = ctx.getChild(1).getText()
            # print(f"Operation:{Operation},child0:{ctx.getChild(0).getText()},child2:{ctx.getChild(2).getText()}")

            left = self.visit(ctx.getChild(0))
            right = self.visit(ctx.getChild(2))
            if(self.isExprJudge(Operation)):
                '''
                对应语法： expression: expression '==' | '!=' | '<' | '<=' | '>' | '>=' expr
                '''
                left,right = self.exprTypeConvert(left,right)
                if(left['type']==double):
                    valueToReturn = Builder.fcmp_ordered(Operation,left['value'],right['value'])
                elif(left['type']==int32 or left['type'] == int64 or left['type'] == int8 or left['type']==int1):
                    if(left['signed']):
                        valueToReturn = Builder.icmp_signed(Operation,left['value'],right['value'])
                    else:
                        valueToReturn = Builder.icmp_unsigned(Operation,left['value'],right['value'])                
                return{
                    'type':int1,
                    'signed':True,
                    'value':valueToReturn
                }

            elif(Operation == '+' or Operation == '-' or Operation == '*' or Operation == '/' or Operation == '%' or Operation == '<<' or Operation == '>>'):
                '''
                对应语法：expression: expression '+'|'-'|'*'|'/'|'%' expression
                '''
                left,right = self.exprTypeConvert(left,right)
                if(Operation == '+'):
                    valueToReturn = Builder.add(left['value'],right['value'])
                elif(Operation == '-'):
                    valueToReturn = Builder.sub(left['value'],right['value'])
                elif(Operation == '*'):
                    valueToReturn = Builder.mul(left['value'],right['value'])
                elif(Operation == '/'):
                    valueToReturn = Builder.sdiv(left['value'],right['value'])
                elif(Operation == '%'):
                    valueToReturn = Builder.srem(left['value'],right['value'])
                elif(Operation == '<<'):
                    valueToReturn = Builder.shl(left['value'],right['value'])
                elif(Operation == '>>'):
                    valueToReturn = Builder.lshr(left['value'],right['value'])
                return{
                    'type':right['type'],
                    'signed':True,
                        'value':valueToReturn
                }

            elif(Operation == '='):
                '''
                对应语法： expression: leftExpression '=' expression
                '''
                # result = self.visit(ctx.expression())
                ChildCount=ctx.getChild(0).getChildCount()
                if(ChildCount==1):
                    #leftExpression为变量
                    print(left," is an varible")
                    left,right = self.assignTypeConvert(left,right) # 强制类型转换
                    self.symbolTable.setProperty(left['name'], value = right['value'])
                else:
                    #leftExpression为数组
                    print(left," is an arrayItem")
                    Builder.store(right['value'],left['address'])
                return 

            elif(Operation == '|' or Operation == 'bitor' or Operation == '&' or Operation == 'bitand' or Operation == '^' or Operation == 'xor'):
                '''
                对应语法： expression: expression BITOR|BITAND|XOR expression
                '''
                left,right = self.exprTypeConvert(left,right)
                Signed = False
                if left['signed'] or right['signed']:
                    Signed = True
                if(Operation == '|' or Operation == 'bitor'):
                    ValueToReturn = Builder.or_(left['value'],right['value'])
                elif(Operation == '&' or Operation == 'bitand' ):
                    ValueToReturn = Builder.and_(left['value'],right['value'])
                elif(Operation == '^' or Operation == 'xor'):
                    ValueToReturn = Builder.xor(left['value'],right['value'])
                return{
                    'type':left['type'],
                    'signed':Signed,
                    'value':ValueToReturn
                }
            
            elif(Operation == '&&' or Operation == 'and' or Operation == '||' or Operation == 'or'):
                '''
                对应语法：expression AND|OR expression
                '''
                left = self.toBool(left)
                right = self.toBool(right)
                if(Operation == '&&' or Operation == 'and'):
                    ValueToReturn = Builder.and_(left['value'],right['value'])
                elif(Operation == '||' or Operation == 'or'):
                    ValueToReturn = Builder.or_(left['value'],right['value'])
                return{
                    'type':int1,
                    'signed':True,
                    'value':ValueToReturn
                }

    def visitBlock(self, ctx: cpp20Parser.BlockContext):
        self.symbolTable.enterScope()
        super().visitBlock(ctx)
        self.symbolTable.exitScope()
        return

    def visitLiterals(self, ctx: cpp20Parser.LiteralsContext):
        result = self.visit(ctx.getChild(0))
        return result


    def visitIntegerLiteral(self, ctx: cpp20Parser.IntegerLiteralContext):
        Signed = True
        if(ctx.getText()[-2:] == 'll' or ctx.getText()[-2:] == 'LL'):
            ReturnType = int64
            if ctx.getText()[-3] == 'u' or ctx.getText()[-3] == 'U':
                Signed = False
                textOutOfSuffix = ctx.getText()[:-3]
            else:
                textOutOfSuffix = ctx.getText()[:-2]
        elif(ctx.getText()[-1]=='l' or ctx.getText()[-2:-1] == 'L'):
            ReturnType = int32
            if ctx.getText()[-2] == 'u' or ctx.getText()[-2] == 'U':
                Signed = False
                textOutOfSuffix = ctx.getText()[:-2]
            else:
                textOutOfSuffix = ctx.getText()[:-1]
        else:
            ReturnType = int32
            if ctx.getText()[-1] == 'u' or ctx.getText()[-1] == 'U':
                Signed = False
                textOutOfSuffix = ctx.getText()[:-1]
            else:
                textOutOfSuffix = ctx.getText()
        return {
            'type':ReturnType,
            'signed':Signed,
            'value':ir.Constant(ReturnType,int(textOutOfSuffix))
        }
    
    def visitFloatingLiteral(self, ctx: cpp20Parser.FloatingLiteralContext):
        return{
            'type':double,
            'value':ir.Constant(double,float(ctx.getText()))
        }
    
    def visitLeftExpression(self, ctx: cpp20Parser.LeftExpressionContext):
        if(ctx.getText()[-1]==']'):
            '''
            对应语法：leftExpression:Identifier (LSQUARE DecimalLiteral RSQUARE)
            '''
            index = self.symbolTable.getProperty(ctx.getChild(0).getText())
            subscribe = int(ctx.getChild(2).getText())
            if(isinstance(index.get_type(),ir.types.ArrayType)):
                Builder = self.Builders[-1]
                Address = Builder.gep(index.get_value(),[ir.Constant(int32,0),ir.Constant(int32,subscribe)],inbounds=True)
                ValueToReturn = Builder.load(Address)
                print("call arrayItem",ValueToReturn)
                return{
                    'type':index.get_type().element,
                    'signed':True,
                    'value':ValueToReturn,
                    'address':Address
                }
            else:
                raise BaseException("the array isn't defined")
            
        else:
            '''
            对应语法：leftExpression:Identifier
            '''
            symbol = self.symbolTable.getProperty(ctx.getText())
            return {
                    'name':ctx.getText(),
                    'type':symbol.get_type(),
                    'signed':symbol.get_signed(),
                    'value':symbol.get_value()
                }

if __name__ == "__main__":
    input_stream = FileStream("test2.cpp")
    # lexer
    lexer = cpp20Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    # parser
    parser = cpp20Parser(stream)
    tree = parser.translationUnit()
    print(tree.toStringTree(recog=parser))
    visitor = myCpp20Visitor()
    visitor.visit(tree)
    print(visitor.Module)
    pass
