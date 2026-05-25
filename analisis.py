# %%
import ply.lex as lex
import ply.yacc as yacc
from arbol import Literal, BinaryOp, Variable, Program, Visitor, BlockNode, WhileNode, AssignmentNode, IfNode, ReturnNode, FunctionNode, CallNode, ForNode, DoWhileNode

reserved = {
    'while': 'WHILE',
    'if': 'IF',
    'else': 'ELSE',
    'return': 'RETURN',
    'for': 'FOR',
    'do': 'DO'
}

tokens = ['ID', 'INTLIT', 'FLOATLIT', 'LE', 'GE'] + list(reserved.values())

t_LE = r'<='
t_GE = r'>='

t_ignore  = ' \t'
literals = '+-*/%(){}<>=;,' # ['+','-','*','/', '%', '(', ')', '<', '>', '=', ';', ]

def t_ID(t):
     r'[a-zA-Z_][a-zA-Z_0-9]*'
     t.type = reserved.get(t.value, 'ID')
     return t

def t_FLOATLIT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
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
    Program : Function Program
            | Function
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_Function(p):
    """
    Function : ID ID '(' Parameters ')' '{' Declarations Statements '}'
    """
    p[0] = FunctionNode(return_type=p[1], func_name=p[2], parameters=p[4], declarations=p[7], statements=p[8])

def p_Parameters_multiple(p):
    """
    Parameters : Parameters ',' Parameter
               | Parameter
               | empty
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_Parameter(p):
    """
    Parameter : ID ID
    """
    p[0] = Variable(p[2], p[1])

def p_empty(p):
    """
    empty :
    """
    p[0] = None

def p_Declarations(p):
    """
    Declarations : Declarations Declaration
                 | 
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

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

def p_Statement_if(p):
    """
    Statement : IF '(' Expression ')' Statement
    """
    p[0] = IfNode(p[3], p[5], None)

def p_Statement_if_else(p):
    """
    Statement : IF '(' Expression ')' Statement ELSE Statement
    """
    p[0] = IfNode(p[3], p[5], p[7])

def p_Statement_return(p):
    """
    Statement : RETURN Expression ';'
    """
    p[0] = ReturnNode(p[2])

def p_Statement_call(p):
    """
    Statement : ID '(' Arguments ')' ';'
    """
    p[0] = CallNode(p[1], p[3])

def p_Statement_for(p):
    """
    Statement : FOR '(' ForInit Expression ';' ForIncr ')' Statement
    """
    p[0] = ForNode(p[3], p[4], p[6], p[8])

def p_Statement_dowhile(p):
    """
    Statement : DO Statement WHILE '(' Expression ')' ';'
    """
    p[0] = DoWhileNode(p[2], p[5])

def p_ForInit(p):
    """
    ForInit : ID '=' Expression ';'
    """
    p[0] = AssignmentNode(p[1], p[3])

def p_ForIncr(p):
    """
    ForIncr : ID '=' Expression
    """
    p[0] = AssignmentNode(p[1], p[3])

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
             | Addition '-' Term
             | Term
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(p[2], p[1], p[3])

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

def p_Factor_FLOAT(p):
    '''
    Factor : FLOATLIT
    '''
    p[0] = Literal(p[1], 'FLOAT')

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

def p_Factor_call(p):
    """
    Factor : ID '(' Arguments ')'
    """
    p[0] = CallNode(p[1], p[3])

def p_Arguments(p):
    """
    Arguments : Arguments ',' Expression
              | Expression
              | empty
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []
        
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
floatType = ir.FloatType()
module = ir.Module(name="prog")

# int main() {
class IRGenerator(Visitor):
    def __init__(self):
        self.stack = []
        self.symbol_table = dict()
        self.variable_types = dict()
        self.builder = None
        self.current_func = None

    def visit_function(self, node: FunctionNode):
        self.symbol_table = dict()
        self.variable_types = dict()
        
        ret_type = floatType if node.return_type == 'float' else intType
        param_types = [floatType if p.type == 'float' else intType for p in node.parameters]
        
        fnty = ir.FunctionType(ret_type, param_types)
        func = ir.Function(module, fnty, name=node.func_name)
        self.current_func = func
        
        entry = func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(entry)
        
        # If there are parameters, allocate and store the arguments in order
        for i, param_node in enumerate(node.parameters):
            arg = func.args[i]
            arg.name = param_node.name
            
            p_type = param_node.type
            llvm_type = floatType if p_type == 'float' else intType
            
            ptr = self.builder.alloca(llvm_type, name=param_node.name)
            self.builder.store(arg, ptr)
            self.symbol_table[param_node.name] = ptr
            self.variable_types[param_node.name] = p_type
            
        for decl in node.declarations:
            decl.accept(self)
        for stmt in node.statements:
            stmt.accept(self)

    def visit_program(self, node: Program):
        for decl in node.declarations:
            decl.accept(self)
        for stmt in node.statements:
            stmt.accept(self)

    def visit_block(self, node: BlockNode):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_while(self, node: WhileNode):
        func = self.current_func
        
        # 1. Create the basic blocks
        head_block = func.append_basic_block(name='while-head')
        body_block = func.append_basic_block(name='while-body')
        exit_block = func.append_basic_block(name='while-exit')
        
        # 2. Branch from current block to head_block
        if not self.builder.block.is_terminated:
            self.builder.branch(head_block)
        
        # 3. Position in head_block and compile condition
        self.builder.position_at_end(head_block)
        node.condition.accept(self)
        cond_val = self.stack.pop()
        
        # Ensure condition is i1
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed('!=', cond_val, intType(0))
            
        self.builder.cbranch(cond_val, body_block, exit_block)
        
        # 4. Position in body_block and compile body
        self.builder.position_at_end(body_block)
        node.body.accept(self)
        if not self.builder.block.is_terminated:
            self.builder.branch(head_block)
        
        # 5. Position in exit_block for subsequent instructions
        self.builder.position_at_end(exit_block)

    def visit_if(self, node: IfNode):
        func = self.current_func
        
        # 1. Create blocks
        then_block = func.append_basic_block(name='if-then')
        else_block = func.append_basic_block(name='if-else') if node.else_stmt else None
        exit_block = func.append_basic_block(name='if-exit')
        
        # 2. Evaluate condition
        node.condition.accept(self)
        cond_val = self.stack.pop()
        
        # Ensure condition is i1
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed('!=', cond_val, intType(0))
            
        false_dest = else_block if else_block else exit_block
        self.builder.cbranch(cond_val, then_block, false_dest)
        
        # 3. Position in then_block and compile
        self.builder.position_at_end(then_block)
        node.then_stmt.accept(self)
        if not self.builder.block.is_terminated:
            self.builder.branch(exit_block)
        
        # 4. Position in else_block and compile (if exists)
        if else_block and node.else_stmt:
            self.builder.position_at_end(else_block)
            node.else_stmt.accept(self)
            if not self.builder.block.is_terminated:
                self.builder.branch(exit_block)
            
        # 5. Position in exit_block
        self.builder.position_at_end(exit_block)

    def visit_literal(self, node: Literal) -> None:
        if node.type == 'FLOAT':
            self.stack.append(
                floatType(float(node.value))
            )
        else:
            self.stack.append(
                intType(int(node.value))
            )
    
    def visit_variable(self, node: Variable):
        if node.name not in self.symbol_table:
            # Declaration: allocate memory
            v_type = node.type
            llvm_type = floatType if v_type == 'float' else intType
            ptr = self.builder.alloca(llvm_type, name=node.name)
            self.symbol_table[node.name] = ptr
            self.variable_types[node.name] = v_type
        else:
            # Reference: load value from memory and push to stack
            ptr = self.symbol_table[node.name]
            val = self.builder.load(ptr, name=node.name)
            self.stack.append(val)

    def visit_assignment(self, node: AssignmentNode):
        node.expr.accept(self)
        val = self.stack.pop()
        ptr = self.symbol_table[node.var_name]
        var_type = self.variable_types.get(node.var_name, 'int')
        
        if var_type == 'float' and val.type == intType:
            val = self.builder.sitofp(val, floatType)
        elif var_type == 'int' and val.type == floatType:
            val = self.builder.fptosi(val, intType)
            
        self.builder.store(val, ptr)

    def visit_return(self, node: ReturnNode):
        node.expr.accept(self)
        val = self.stack.pop()
        self.builder.ret(val)

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.lhs.accept(self)
        node.rhs.accept(self)
        rhs = self.stack.pop()
        lhs = self.stack.pop()
        if node.op == '+':
            self.stack.append(self.builder.add(lhs, rhs))
        elif node.op == '-':
            self.stack.append(self.builder.sub(lhs, rhs))
        elif node.op == '*':
            self.stack.append(self.builder.mul(lhs, rhs))
        else:
            tmp = self.builder.icmp_signed(node.op, lhs, rhs)
            self.stack.append(self.builder.zext(tmp, intType))

    def visit_call(self, node: CallNode):
        args_list = []
        for arg in node.arguments:
            arg.accept(self)
            args_list.append(self.stack.pop())
            
        if node.func_name == "printf":
            arg_val = args_list[0]
            printf_func = module.globals.get("printf")
            voidptr_ty = ir.IntType(8).as_pointer()
            if printf_func is None:
                printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
                printf_func = ir.Function(module, printf_ty, name="printf")
            
            fmt_str = "%d\n\0"
            c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_str)), bytearray(fmt_str.encode("utf8")))
            global_fmt = ir.GlobalVariable(module, c_fmt.type, name=f"fstr_{len(list(module.global_values))}")
            global_fmt.linkage = 'internal'
            global_fmt.global_constant = True
            global_fmt.initializer = c_fmt
            
            fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)
            res = self.builder.call(printf_func, [fmt_arg, arg_val])
            self.stack.append(res)
        else:
            callee_func = module.globals.get(node.func_name)
            if callee_func is None:
                raise ValueError(f"Function '{node.func_name}' not defined in module")
            res = self.builder.call(callee_func, args_list)
            self.stack.append(res)

    def visit_for(self, node: ForNode):
        node.init_stmt.accept(self)
        func = self.current_func
        
        head_block = func.append_basic_block(name='for-head')
        body_block = func.append_basic_block(name='for-body')
        exit_block = func.append_basic_block(name='for-exit')
        
        if not self.builder.block.is_terminated:
            self.builder.branch(head_block)
            
        self.builder.position_at_end(head_block)
        node.condition.accept(self)
        cond_val = self.stack.pop()
        
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed('!=', cond_val, intType(0))
            
        self.builder.cbranch(cond_val, body_block, exit_block)
        
        self.builder.position_at_end(body_block)
        node.body.accept(self)
        node.incr_stmt.accept(self)
        if not self.builder.block.is_terminated:
            self.builder.branch(head_block)
            
        self.builder.position_at_end(exit_block)

    def visit_dowhile(self, node: DoWhileNode):
        func = self.current_func
        
        body_block = func.append_basic_block(name='do-body')
        exit_block = func.append_basic_block(name='do-exit')
        
        if not self.builder.block.is_terminated:
            self.builder.branch(body_block)
            
        self.builder.position_at_end(body_block)
        node.body.accept(self)
        
        node.condition.accept(self)
        cond_val = self.stack.pop()
        
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed('!=', cond_val, intType(0))
            
        if not self.builder.block.is_terminated:
            self.builder.cbranch(cond_val, body_block, exit_block)
            
        self.builder.position_at_end(exit_block)

# %%
data = """
int main() {
    float x;
    int y;
    y = 10;
    x = y;
    printf(y);
    return 0;
}
"""
lexer = lex.lex()
parser = yacc.yacc()
root = parser.parse(data)

print("AST Root:", root)

irgen = IRGenerator()
for func_node in root:
    func_node.accept(irgen)

print("\n--- LLVM IR Stack ---")
for val in irgen.stack:
    print(val)

print("\n--- Generated LLVM IR Module ---")
print(module)
