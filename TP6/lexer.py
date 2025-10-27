# ficheiro: lexer.py

import ply.lex as lex

# Lista de nomes dos tokens. Isto é obrigatório.
tokens = (
    'INT',
    'MAIS',
    'MENOS',
    'VEZES',
    'DIVIDIR',
    'PA',
    'PF'
)

# Regras de Expressão Regular para os tokens simples
t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_DIVIDIR = r'/'
t_PA = r'\('
t_PF = r'\)'

# Uma regra para os números inteiros.
# A ação associada (o código) converte a string de dígitos num inteiro.


def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regra para seguir os números de linha


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Uma string com caracteres a ignorar (espaços e tabs)
t_ignore = ' \t'

# Regra para lidar com erros


def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)


# Constrói o lexer
lexer = lex.lex()
