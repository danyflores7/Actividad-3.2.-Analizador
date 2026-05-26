import os
import ply.lex as lex
import ply.yacc as yacc
from llvmlite import ir
import analisis

def main():
    pruebas_dir = "pruebas"
    if not os.path.exists(pruebas_dir):
        print(f"Error: Directory '{pruebas_dir}' not found.")
        return

    # Files to verify in sorted order
    files = sorted([f for f in os.listdir(pruebas_dir) if f.endswith('.c')])

    print("==================================================")
    print("      Verificador de Pruebas del Compilador       ")
    print("==================================================")

    for filename in files:
        filepath = os.path.join(pruebas_dir, filename)
        print(f"\nProcesando: {filepath}...")
        
        try:
            # Read C source code
            with open(filepath, 'r') as f:
                code = f.read()

            # Reset LLVM module for this test file to prevent accumulation
            analisis.module = ir.Module(name="prog")

            # Build lexer and parser dynamically using rules from analisis
            lexer = lex.lex(module=analisis)
            parser = yacc.yacc(module=analisis, debug=False, write_tables=False)
            
            root = parser.parse(code, lexer=lexer)

            if root is None:
                print(f"❌ {filepath} - Error de Sintaxis (AST no generado)")
                continue

            # Run LLVM IR generation
            irgen = analisis.IRGenerator()
            for func_node in root:
                func_node.accept(irgen)

            # Verification: print success and the generated IR
            print(f"✅ {filepath} - ¡Compilación Exitosa!")
            print("--- LLVM IR Generado ---")
            print(str(analisis.module).strip())
            print("-" * 50)

        except Exception as e:
            print(f"❌ {filepath} - ¡Error de Compilación!")
            print(f"Detalle del error: {e}")
            print("-" * 50)

if __name__ == "__main__":
    main()
