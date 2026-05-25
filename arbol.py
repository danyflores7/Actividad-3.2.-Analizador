from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass

class Literal(ASTNode):
    def __init__(self, value: Any, type: str) -> None:
        self.value = value
        self.type = type

    def accept(self, visitor: Visitor):
        visitor.visit_literal(self)

class Variable(ASTNode):
    def __init__(self, name: Any, type: str) -> None:
        self.name = name
        self.type = type

    def accept(self, visitor: Visitor):
        visitor.visit_variable(self)

class BinaryOp(ASTNode):
    def __init__(self, op: str, lhs: ASTNode, rhs: ASTNode) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def accept(self, visitor: Visitor):
        visitor.visit_binary_op(self)

class Program(ASTNode):
    def __init__(self, declarations: Any, statements: list[ASTNode]) -> None:
        self.declarations = declarations
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_program(self)

class BlockNode(ASTNode):
    def __init__(self, statements: list[ASTNode]) -> None:
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_block(self)

class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode) -> None:
        self.condition = condition
        self.body = body

    def accept(self, visitor: Visitor):
        visitor.visit_while(self)

class ForNode(ASTNode):
    def __init__(self, init_stmt: ASTNode, condition: ASTNode, incr_stmt: ASTNode, body: ASTNode) -> None:
        self.init_stmt = init_stmt
        self.condition = condition
        self.incr_stmt = incr_stmt
        self.body = body

    def accept(self, visitor: Visitor):
        visitor.visit_for(self)

class AssignmentNode(ASTNode):
    def __init__(self, var_name: str, expr: ASTNode) -> None:
        self.var_name = var_name
        self.expr = expr

    def accept(self, visitor: Visitor):
        visitor.visit_assignment(self)

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_stmt: ASTNode, else_stmt: ASTNode | None) -> None:
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def accept(self, visitor: Visitor):
        visitor.visit_if(self)

class ReturnNode(ASTNode):
    def __init__(self, expr: ASTNode) -> None:
        self.expr = expr

    def accept(self, visitor: Visitor):
        visitor.visit_return(self)

class FunctionNode(ASTNode):
    def __init__(self, return_type: str, func_name: str, parameters: list[Variable], declarations: list[ASTNode], statements: list[ASTNode]) -> None:
        self.return_type = return_type
        self.func_name = func_name
        self.parameters = parameters
        self.declarations = declarations
        self.statements = statements

    def accept(self, visitor: Visitor):
        visitor.visit_function(self)

class CallNode(ASTNode):
    def __init__(self, func_name: str, arguments: list[ASTNode]) -> None:
        self.func_name = func_name
        self.arguments = arguments

    def accept(self, visitor: Visitor):
        visitor.visit_call(self)

class Visitor(ABC):
    @abstractmethod
    def visit_literal(self, node: Literal) -> None:
        pass
    @abstractmethod
    def visit_variable(self, node: Variable) -> None:
        pass
    @abstractmethod
    def visit_binary_op(self, node: BinaryOp) -> None:
        pass
    @abstractmethod
    def visit_program(self, node: Program) -> None:
        pass
    @abstractmethod
    def visit_block(self, node: BlockNode) -> None:
        pass
    @abstractmethod
    def visit_while(self, node: WhileNode) -> None:
        pass
    @abstractmethod
    def visit_assignment(self, node: AssignmentNode) -> None:
        pass
    @abstractmethod
    def visit_if(self, node: IfNode) -> None:
        pass
    @abstractmethod
    def visit_return(self, node: ReturnNode) -> None:
        pass
    @abstractmethod
    def visit_function(self, node: FunctionNode) -> None:
        pass
    @abstractmethod
    def visit_call(self, node: CallNode) -> None:
        pass
    @abstractmethod
    def visit_for(self, node: ForNode) -> None:
        pass

class Calculator(Visitor):
    def __init__(self):
        self.stack = []

    def visit_literal(self, node: Literal) -> None:
        self.stack.append(node.value)
    
    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)
        rhs = self.stack.pop()
        lhs = self.stack.pop()
        if node.op == '+':
            self.stack.append(lhs + rhs)
        elif node.op == '-':
            self.stack.append(lhs - rhs)
        elif node.op == '*':
            self.stack.append(lhs * rhs)
        elif node.op == '/':
            self.stack.append(lhs / rhs)
        elif node.op == '%':
            self.stack.append(lhs % rhs)

    def visit_program(self, node: Program) -> None:
        for stmt in node.statements:
            stmt.accept(self)

    def visit_block(self, node: BlockNode) -> None:
        for stmt in node.statements:
            stmt.accept(self)

    def visit_while(self, node: WhileNode) -> None:
        node.condition.accept(self)
        node.body.accept(self)

    def visit_assignment(self, node: AssignmentNode) -> None:
        node.expr.accept(self)

    def visit_if(self, node: IfNode) -> None:
        node.condition.accept(self)
        node.then_stmt.accept(self)
        if node.else_stmt:
            node.else_stmt.accept(self)

    def visit_return(self, node: ReturnNode) -> None:
        node.expr.accept(self)

    def visit_function(self, node: FunctionNode) -> None:
        for decl in node.declarations:
            decl.accept(self)
        for stmt in node.statements:
            stmt.accept(self)

    def visit_call(self, node: CallNode) -> None:
        for arg in node.arguments:
            arg.accept(self)

    def visit_for(self, node: ForNode) -> None:
        node.init_stmt.accept(self)
        node.condition.accept(self)
        node.incr_stmt.accept(self)
        node.body.accept(self)