# ficheiro: parser.py

from lexer import lexer

# Variável global para armazenar o próximo token (lookahead)
prox_simb = None


def parser_error(simbolo_esperado):
    """ Função para reportar erros sintáticos. """
    if prox_simb:
        print(
            f"Erro sintático: Esperado '{simbolo_esperado}', mas encontrei '{prox_simb.type}' ({prox_simb.value}) na linha {prox_simb.lineno}")
    else:
        print(
            f"Erro sintático: Esperado '{simbolo_esperado}', mas o input terminou.")
    # Em implementações mais complexas, poderia tentar-se recuperar do erro.
    # Por agora, terminamos a execução.
    exit(1)


def consome(tipo_token):
    """ Consome um token do tipo esperado e avança para o próximo. """
    global prox_simb
    if prox_simb and prox_simb.type == tipo_token:
        prox_simb = lexer.token()
    else:
        parser_error(tipo_token)

# ----------------- Funções da Gramática -----------------
# Gramática: Fator -> INT | "(" Expr ")"


def rec_Fator():
    print("Derivando por: Fator -> ...")
    if prox_simb and prox_simb.type == 'INT':
        # Aplica a regra Fator -> INT
        print("   Reconheci: Fator -> INT")
        consome('INT')
    elif prox_simb and prox_simb.type == 'PA':
        # Aplica a regra Fator -> ( Expr )
        print("   Reconheci: Fator -> ( Expr )")
        consome('PA')
        rec_Expr()
        consome('PF')
    else:
        # Se não for nem INT nem PA, é um erro.
        parser_error("INT ou (")

# Gramática: Termo2 -> "*" Fator Termo2 | "/" Fator Termo2 | Vazio


def rec_Termo2():
    print("Derivando por: Termo2 -> ...")
    if prox_simb and prox_simb.type == 'VEZES':
        # Aplica a regra Termo2 -> * Fator Termo2
        print("   Reconheci: Termo2 -> * Fator Termo2")
        consome('VEZES')
        rec_Fator()
        rec_Termo2()
    elif prox_simb and prox_simb.type == 'DIVIDIR':
        # Aplica a regra Termo2 -> / Fator Termo2
        print("   Reconheci: Termo2 -> / Fator Termo2")
        consome('DIVIDIR')
        rec_Fator()
        rec_Termo2()
    else:
        # Aplica a regra Vazio
        print("   Reconheci: Termo2 -> Vazio")
        pass  # Não faz nada (produção vazia)

# Gramática: Termo -> Fator Termo2


def rec_Termo():
    print("Derivando por: Termo -> Fator Termo2")
    rec_Fator()
    rec_Termo2()

# Gramática: Expr2 -> "+" Termo Expr2 | "-" Termo Expr2 | Vazio


def rec_Expr2():
    print("Derivando por: Expr2 -> ...")
    if prox_simb and prox_simb.type == 'MAIS':
        # Aplica a regra Expr2 -> + Termo Expr2
        print("   Reconheci: Expr2 -> + Termo Expr2")
        consome('MAIS')
        rec_Termo()
        rec_Expr2()
    elif prox_simb and prox_simb.type == 'MENOS':
        # Aplica a regra Expr2 -> - Termo Expr2
        print("   Reconheci: Expr2 -> - Termo Expr2")
        consome('MENOS')
        rec_Termo()
        rec_Expr2()
    else:
        # Aplica a regra Vazio
        print("   Reconheci: Expr2 -> Vazio")
        pass  # Não faz nada (produção vazia)

# Gramática: Expr -> Termo Expr2


def rec_Expr():
    print("Derivando por: Expr -> Termo Expr2")
    rec_Termo()
    rec_Expr2()


def run_parser(data):
    """ Função principal que inicia a análise. """
    global prox_simb
    lexer.input(data)
    prox_simb = lexer.token()
    rec_Expr()

    # Após reconhecer a expressão, não deve haver mais tokens.
    if prox_simb is not None:
        print(
            f"Erro: Input extra no final da expressão, a começar por '{prox_simb.value}'")
    else:
        print("\nAnálise sintática concluída com sucesso! A expressão é válida.")


# ---------- Programa Principal ----------
if __name__ == "__main__":
    try:
        # Pede input ao utilizador
        expressao = input("Introduza uma expressão aritmética: ")
        if expressao:
            run_parser(expressao)
        else:
            print("Nenhuma expressão fornecida.")
    except EOFError:
        # Lida com o caso de não haver mais input (Ctrl+D)
        print("\nInput terminado.")
