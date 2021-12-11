# Generated from grammar/cpp20Parser.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .cpp20Parser import cpp20Parser
else:
    from cpp20Parser import cpp20Parser

# This class defines a complete generic visitor for a parse tree produced by cpp20Parser.

class cpp20ParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by cpp20Parser#translationUnit.
    def visitTranslationUnit(self, ctx:cpp20Parser.TranslationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#constExpression.
    def visitConstExpression(self, ctx:cpp20Parser.ConstExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#expression.
    def visitExpression(self, ctx:cpp20Parser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#statement.
    def visitStatement(self, ctx:cpp20Parser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#block.
    def visitBlock(self, ctx:cpp20Parser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#functionCall.
    def visitFunctionCall(self, ctx:cpp20Parser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#ifStatement.
    def visitIfStatement(self, ctx:cpp20Parser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#caseStatement.
    def visitCaseStatement(self, ctx:cpp20Parser.CaseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#switchStatement.
    def visitSwitchStatement(self, ctx:cpp20Parser.SwitchStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#whileStatement.
    def visitWhileStatement(self, ctx:cpp20Parser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#doWhileStatement.
    def visitDoWhileStatement(self, ctx:cpp20Parser.DoWhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#forStatement.
    def visitForStatement(self, ctx:cpp20Parser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#returnStatement.
    def visitReturnStatement(self, ctx:cpp20Parser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#breakStatement.
    def visitBreakStatement(self, ctx:cpp20Parser.BreakStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#continueStatement.
    def visitContinueStatement(self, ctx:cpp20Parser.ContinueStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#declaration.
    def visitDeclaration(self, ctx:cpp20Parser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#variableDeclaration.
    def visitVariableDeclaration(self, ctx:cpp20Parser.VariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#functionDeclaration.
    def visitFunctionDeclaration(self, ctx:cpp20Parser.FunctionDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#functionParameter.
    def visitFunctionParameter(self, ctx:cpp20Parser.FunctionParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#typeSpecifier.
    def visitTypeSpecifier(self, ctx:cpp20Parser.TypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#integerTypeSpecifier.
    def visitIntegerTypeSpecifier(self, ctx:cpp20Parser.IntegerTypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#realTypeSpecifier.
    def visitRealTypeSpecifier(self, ctx:cpp20Parser.RealTypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#booleanTypeSpecifier.
    def visitBooleanTypeSpecifier(self, ctx:cpp20Parser.BooleanTypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#charTypeSpecifier.
    def visitCharTypeSpecifier(self, ctx:cpp20Parser.CharTypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by cpp20Parser#voidTypeSpecifier.
    def visitVoidTypeSpecifier(self, ctx:cpp20Parser.VoidTypeSpecifierContext):
        return self.visitChildren(ctx)



del cpp20Parser