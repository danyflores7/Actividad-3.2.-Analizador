# %%
import ply.lex as lex
import ply.yacc as yacc
from arbol import Literal, BinaryOp, Variable, Program, Visitor

tokens = ['ID', 'INTLIT', 'LE', 'GE']

t_LE = r'<='
t_GE = r'>='

t_ignore  = ' \t'
literals = '+-*/%(){}<>=;,' # ['+','-','*','/', '%', '(', ')', '<', '>', '=', ';', ]

def t_ID(t):
     r'[a-zA-Z_][a-zA-Z_0-9]*'
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
    Statements : Assignment
    """
    p[0] = p[1]

def p_Assignment(p):
    """ 
    Assignment : ID '=' Expression ';'
    """
    p[0] = p[3]

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
        node.statements.accept(self)

    def visit_literal(self, node: Literal) -> None:
        self.stack.append(
            intType(int(node.value))
        )
    
    def visit_variable(self, node: Variable):
        self.symbol_table[node.name] = node.type

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

    x = 10 * y;
}
"""
lexer = lex.lex()
parser = yacc.yacc()
root = parser.parse(data)

print(root)

irgen = IRGenerator()

root.accept(irgen)
# builder.ret(irgen.stack.pop())
# print(module)

# %%
irgen.stack
# %%
