import json
import os
import re
import sys

# --- GERAIS ---

# Determina o diretório do script para localizar o 'stock.json'
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
STOCK_FILE = os.path.join(SCRIPT_DIR, "stock.json")

stock = []              # O stock de produtos (carregado de stock.json)
saldo_atual = 0         # O dinheiro inserido, SEMPRE EM CÊNTIMOS

# Denominações aceites (em cêntimos)
MOEDAS_ACEITES = [200, 100, 50, 20, 10, 5, 2, 1]


# --- FUNÇÕES LEXER (Análise Léxica) ---

# Definição das especificações de tokens para a análise léxica (RegEx)
TOKEN_SPECS = [
    ('EURO',    r'\d+[eE]'),      # Ex: 1e, 2E
    ('CENT',    r'\d+[cC]'),      # Ex: 50c, 5C
    ('COMANDO', r'(LISTAR|MOEDA|SELECIONAR|SAIR)'),
    ('CODIGO',  r'[a-zA-Z]\d+'),
    ('SKIP',    r'[,\s]+'),       # Ignorar vírgulas e espaços
    ('INVALID', r'.'),            # Qualquer outra coisa
]

TOK_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECS)
COMPILED_REGEX = re.compile(TOK_REGEX, re.IGNORECASE)


def tokenizar(text):
    """DOC: Função Lexer que converte a string de input numa lista de tokens (TIPO, VALOR)."""
    token_list = []

    for mo in COMPILED_REGEX.finditer(text):
        kind = mo.lastgroup
        value = mo.group(kind)

        if kind != 'SKIP':
            token_list.append((kind, value.upper()))

    return token_list


# --- FUNÇÕES AUXILIARES E PERSISTÊNCIA ---

def load_stock():
    """DOC: Carrega o stock de produtos a partir do ficheiro JSON no arranque do programa."""
    if not os.path.exists(STOCK_FILE):
        print(
            f"maq: Aviso: O ficheiro '{STOCK_FILE}' não foi encontrado. A iniciar com stock vazio.")
        return []

    try:
        with open(STOCK_FILE, 'r', encoding='utf-8') as f:
            loaded_stock = json.load(f)
            print(f"maq: Stock carregado de '{STOCK_FILE}'.")
            return loaded_stock

    except json.JSONDecodeError:
        print(
            f"maq: Erro ao ler o ficheiro '{STOCK_FILE}'. Ficheiro JSON inválido.")
        return []

    except IOError:
        print(
            f"maq: Erro de I/O ao tentar carregar o ficheiro '{STOCK_FILE}'.")
        return []


def save_stock():
    """DOC: Grava o estado atual do stock de volta no ficheiro JSON."""
    global stock
    try:
        with open(STOCK_FILE, 'w', encoding='utf-8') as f:
            json.dump(stock, f, indent=4, ensure_ascii=False)
        print(f"maq: Stock guardado em '{STOCK_FILE}'.")
    except IOError:
        print(f"maq: Erro ao tentar gravar o ficheiro '{STOCK_FILE}'.")


def format_saldo(saldo_em_centimos):
    """DOC: Converte um valor em cêntimos (int) para o formato 'XeYc' (ex: 1e30c)."""
    euros = saldo_em_centimos // 100
    centimos = saldo_em_centimos % 100

    if euros > 0 and centimos > 0:
        return f"{euros}e{centimos}c"
    if euros > 0:
        return f"{euros}e"
    return f"{centimos}c"


# --- FUNÇÕES DE COMANDO ---

def comando_listar():
    """DOC: Lista todos os produtos disponíveis no stock com quantidade > 0."""
    global stock
    print("maq:")
    print(f"{'cod':<4} | {'nome':<20} | {'quant':<5} | {'preço':<5}")
    print("-" * 43)

    produtos_encontrados = False
    for produto in stock:
        if produto['quant'] > 0:
            cod = produto['cod']
            nome = produto['nome']
            quant = produto['quant']
            preco_formatado = f"{produto['preco']:.2f}"

            print(f"{cod:<4} | {nome:<20} | {quant:<5} | {preco_formatado:<5}")
            produtos_encontrados = True

    if not produtos_encontrados:
        print("maq: Stock de produtos vazio ou esgotado.")
    print()


def comando_moeda(input_utilizador):
    """DOC: Processa a entrada de moedas/notas usando a função tokenizar."""
    global saldo_atual

    tokens = tokenizar(input_utilizador)
    total_inserido = 0
    moedas_nao_aceites = []

    for kind, value in tokens:
        if kind in ['EURO', 'CENT']:
            valor_str = value[:-1]
            valor_em_centimos = int(valor_str) * \
                100 if kind == 'EURO' else int(valor_str)

            if valor_em_centimos in MOEDAS_ACEITES:
                total_inserido += valor_em_centimos
            else:
                moedas_nao_aceites.append(value)

        elif kind == 'INVALID':
            moedas_nao_aceites.append(f"'{value}' (Token inválido)")

    saldo_atual += total_inserido

    if moedas_nao_aceites:
        print(
            f"maq: Aviso: Não aceitamos as seguintes denominações: {', '.join(moedas_nao_aceites)}.")

    print(f"maq: Saldo = {format_saldo(saldo_atual)}")
    return total_inserido


def comando_selecionar(cod_produto):
    """DOC: Processa a seleção de um produto, verificando stock e saldo."""
    global stock, saldo_atual

    # Encontrar o produto usando uma expressão geradora (mais limpo)
    produto_selecionado = next(
        (p for p in stock if p['cod'] == cod_produto), None)

    if not produto_selecionado:
        print(f"maq: Produto com código '{cod_produto}' inexistente.")
        return

    nome = produto_selecionado['nome']
    quant = produto_selecionado['quant']
    # Conversão de preço (float) para cêntimos (int)
    preco_centimos = int(round(produto_selecionado['preco'] * 100))

    if quant <= 0:
        print(f"maq: Produto '{nome}' esgotado.")
        return

    if saldo_atual < preco_centimos:
        print("maq: Saldo insuficiente para satisfazer o seu pedido")
        print(
            f"maq: Saldo = {format_saldo(saldo_atual)}; Pedido = {format_saldo(preco_centimos)}")
        return

    # Venda e Dispensação
    produto_selecionado['quant'] -= 1
    saldo_atual -= preco_centimos

    print(f"maq: Pode retirar o produto dispensado \"{nome}\"")
    print(f"maq: Saldo = {format_saldo(saldo_atual)}")


def comando_sair_troco():
    """DOC: Devolve o troco com o menor número de moedas/notas."""
    global saldo_atual

    troco_a_devolver = saldo_atual
    if troco_a_devolver == 0:
        print("maq: Pode retirar o troco: 0c.")
        return

    contagem_moedas = {}

    for moeda in MOEDAS_ACEITES:
        if troco_a_devolver >= moeda:
            quantidade = troco_a_devolver // moeda
            contagem_moedas[moeda] = quantidade
            troco_a_devolver %= moeda

            if troco_a_devolver == 0:
                break

    partes_troco = []

    for moeda_valor_centimos, quantidade in contagem_moedas.items():
        valor_str = f"{moeda_valor_centimos // 100}e" if moeda_valor_centimos >= 100 else f"{moeda_valor_centimos}c"
        partes_troco.append(f"{quantidade}x {valor_str}")

    # Formatação de troco (ex: "1x 50c e 1x 20c" ou "1x 50c")
    troco_str = partes_troco[0] if len(
        partes_troco) == 1 else f"{', '.join(partes_troco[:-1])} e {partes_troco[-1]}"

    print(f"maq: Pode retirar o troco: {troco_str}.")
    saldo_atual = 0


# --- FUNÇÃO PRINCIPAL ---

def main():
    global stock

    # 1. Carregar estado anterior do stock
    stock = load_stock()

    print("maq: Bom dia. Estou disponível para atender o seu pedido.")

    while True:
        # Lê o input e converte para maiúsculas
        user_input = input(">> ").strip().upper()

        if not user_input:
            print(f"maq: Saldo = {format_saldo(saldo_atual)}")
            continue

        partes = user_input.split()
        comando = partes[0] if partes else ""

        if comando == "LISTAR":
            comando_listar()
            print(f"maq: Saldo = {format_saldo(saldo_atual)}")

        elif comando == "MOEDA":
            # Argumentos são tudo o que vem depois do comando MOEDA
            argumentos = user_input[len("MOEDA"):].strip()
            comando_moeda(argumentos)

        elif comando == "SELECIONAR":
            if len(partes) < 2:
                print(
                    "maq: Erro: Comando SELECIONAR requer um código de produto (Ex: SELECIONAR A23).")
            else:
                cod_produto = partes[1]
                comando_selecionar(cod_produto)

        elif comando == "SAIR":
            comando_sair_troco()
            # 2. Guardar estado final do stock antes de sair
            save_stock()
            print("maq: Até à próxima")
            break

        else:
            print(
                f"maq: Comando desconhecido: '{comando}'. Comandos válidos: LISTAR, MOEDA, SELECIONAR [cod], SAIR.")


if __name__ == '__main__':
    main()
