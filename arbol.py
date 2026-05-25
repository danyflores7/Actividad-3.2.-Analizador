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

class AssignmentNode(ASTNode):
    def __init__(self, var_name: str, expr: ASTNode) -> None:
        self.var_name = var_name
        self.expr = expr

    def accept(self, visitor: Visitor):
        visitor.visit_assignment(self)

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