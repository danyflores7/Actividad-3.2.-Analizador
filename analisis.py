# %%
import ply.lex as lex
import ply.yacc as yacc
from arbol import Literal, BinaryOp, Variable, Program, Visitor, BlockNode, WhileNode, AssignmentNode

reserved = {
    'while': 'WHILE'
}

tokens = ['ID', 'INTLIT', 'LE', 'GE'] + list(reserved.values())

t_LE = r'<='
t_GE = r'>='

t_ignore  = ' \t'
literals = '+-*/%(){}<>=;,' # ['+','-','*','/', '%', '(', ')', '<', '>', '=', ';', ]

def t_ID(t):
     r'[a-zA-Z_][a-zA-Z_0-9]*'
     t.type = reserved.get(t.value, 'ID')
     return t

def t_INTLIT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# %%

def p_Program(p):
    """
    Program : ID ID '(' ')' '{' Declarations Statements '}'
    """
    p[0] = Program(p[6], p[7])

def p_Declarations(p):
    """
    Declarations : Declaration
    """
    p[0] = p[1]

def p_Declartion(p):
    """
    Declaration : ID ID ';'
    """
    p[0] = Variable(p[2], p[1])

def p_Statements(p):
    """
    Statements : Statements Statement
               | Statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_Statement(p):
    """
    Statement : Assignment
    """
    p[0] = p[1]

def p_Statement_block(p):
    """
    Statement : '{' Statements '}'
    """
    p[0] = BlockNode(p[2])

def p_Statement_while(p):
    """
    Statement : WHILE '(' Expression ')' Statement
    """
    p[0] = WhileNode(p[3], p[5])

def p_Assignment(p):
    """ 
    Assignment : ID '=' Expression ';'
    """
    p[0] = AssignmentNode(p[1], p[3])

def p_Expression(p):
    """
    Expression : Expression RelOp Addition
               | Addition
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(p[2], p[1], p[3])

def p_RelOp(p):
    """
    RelOp : '<'
          | LE
          | '>' 
          | GE 
    """
    p[0] = p[1]

def p_Addition(p):
    '''
    Addition : Addition '+' Term
             | Term
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp('+', p[1], p[3])

def p_Term(p):
    '''
    Term : Term '*' Factor
         | Factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp('*', p[1], p[3])

def p_Factor_INT(p):
    '''
    Factor : INTLIT 
    '''
    p[0] = Literal(p[1], 'INT')

def p_Factor_ID(p):
    '''
    Factor : ID
    '''
    p[0] = Variable(p[1], 'INT')

def p_Factor_EXP(p):
    '''
    Factor : '(' Expression ')'
    '''
    p[0] = p[2]
        
def p_error(p):
    print("Syntax error in input!", p)


# %%
# from arbol import Calculator, Visitor

# data = '10 + 3 * 2'
# lexer = lex.lex()
# parser = yacc.yacc()
# root = parser.parse(data)
# print(root)
# calc = Calculator()
# root.accept(calc)
# print(root)

# %%
from llvmlite import ir

intType = ir.IntType(32)
module = ir.Module(name="prog")

# int main() {
fnty = ir.FunctionType(intType, [])
func = ir.Function(module, fnty, name='main')

entry = func.append_basic_block('entry')
builder = ir.IRBuilder(entry)


class IRGenerator(Visitor):
    def __init__(self):
        self.stack = []
        self.symbol_table = dict()

    def visit_program(self, node: Program):
        node.declarations.accept(self)
        for stmt in node.statements:
            stmt.accept(self)

    def visit_block(self, node: BlockNode):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_while(self, node: WhileNode):
        func = builder.function
        
        # 1. Create the basic blocks
        head_block = func.append_basic_block(name='while-head')
        body_block = func.append_basic_block(name='while-body')
        exit_block = func.append_basic_block(name='while-exit')
        
        # 2. Branch from current block to head_block
        builder.branch(head_block)
        
        # 3. Position in head_block and compile condition
        builder.position_at_end(head_block)
        node.condition.accept(self)
        cond_val = self.stack.pop()
        
        # Ensure condition is i1
        if cond_val.type != ir.IntType(1):
            cond_val = builder.icmp_signed('!=', cond_val, intType(0))
            
        builder.cbranch(cond_val, body_block, exit_block)
        
        # 4. Position in body_block and compile body
        builder.position_at_end(body_block)
        node.body.accept(self)
        builder.branch(head_block)
        
        # 5. Position in exit_block for subsequent instructions
        builder.position_at_end(exit_block)

    def visit_literal(self, node: Literal) -> None:
        self.stack.append(
            intType(int(node.value))
        )
    
    def visit_variable(self, node: Variable):
        if node.name not in self.symbol_table:
            # Declaration: allocate memory
            ptr = builder.alloca(intType, name=node.name)
            self.symbol_table[node.name] = ptr
        else:
            # Reference: load value from memory and push to stack
            ptr = self.symbol_table[node.name]
            val = builder.load(ptr, name=node.name)
            self.stack.append(val)

    def visit_assignment(self, node: AssignmentNode):
        node.expr.accept(self)
        val = self.stack.pop()
        ptr = self.symbol_table[node.var_name]
        builder.store(val, ptr)

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)
        rhs = self.stack.pop()
        lhs = self.stack.pop()
        if node.op == '+':
            self.stack.append(builder.add(lhs, rhs))
        elif node.op == '*':
            self.stack.append(builder.mul(lhs, rhs))
        else:
            tmp = builder.icmp_signed(node.op, lhs, rhs)
            self.stack.append(builder.zext(tmp, intType))

# %%
data = """
int main() {
    int y;
    y = 5;
    while (y < 10) {
        y = y + 1;
    }
}
"""
lexer = lex.lex()
parser = yacc.yacc()
root = parser.parse(data)

print("AST Root:", root)

irgen = IRGenerator()
root.accept(irgen)

print("\n--- LLVM IR Stack ---")
for val in irgen.stack:
    print(val)

# Complete main return with the last expression value on the stack if any
if irgen.stack:
    builder.ret(irgen.stack[-1])
else:
    builder.ret(intType(0)) # fallback

print("\n--- Generated LLVM IR Module ---")
print(module)
