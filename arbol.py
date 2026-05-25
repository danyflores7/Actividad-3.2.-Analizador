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
        if hasattr(visitor, 'symbol_table') and hasattr(visitor, 'stack'):
            if self.name in visitor.symbol_table:
                from llvmlite import ir
                intType = ir.IntType(32)
                visitor.stack.append(intType(0))
                visitor.visit_variable(self)
                return
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