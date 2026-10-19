"""Gera os dados 100% sintéticos da "Metalúrgica Exemplo".

Nada aqui vem de uma empresa real: setores, famílias de produto, custos,
faixas de prêmio e movimentações são inventados com semente fixa, então a
execução é reproduzível.

Uso:
    python scripts/gerar_dados.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMENTE = 42
DATA_INICIO = date(2025, 11, 1)
DATA_REFERENCIA = date(2026, 10, 19)  # "hoje" do mock: último dia com produção
DATA_FIM = date(2026, 10, 31)  # calendário até o fim do mês da referência

PASTA = Path(__file__).resolve().parent.parent / "dados"

# cd_setor, nome, custo diário de salários (R$), valor médio por peça (R$)
SETORES = [
    (1, "Corte a Laser", 5200.00, 18.00),
    (2, "Dobra", 4300.00, 12.00),
    (3, "Usinagem", 6800.00, 46.00),
    (4, "Soldagem", 7400.00, 38.00),
    (5, "Pintura", 4900.00, 15.00),
    (6, "Montagem", 8100.00, 54.00),
]

# cd_familia, familia, categoria, multiplicador de valor por peça
FAMILIAS = [
    (1, "Suportes", "Estruturas", 0.8),
    (2, "Chassis", "Estruturas", 1.9),
    (3, "Flanges", "Usinados", 1.1),
    (4, "Eixos", "Usinados", 1.5),
    (5, "Carcaças", "Conjuntos", 1.7),
    (6, "Painéis", "Chapas", 0.9),
    (7, "Gabinetes", "Chapas", 1.2),
    (8, "Grades", "Acabamento", 0.7),
]

# eficiência mínima, eficiência máxima, % da diária de prêmio
FAIXAS_PREMIO = [
    (0.00, 0.70, 0.00),
    (0.70, 0.80, 0.20),
    (0.80, 0.90, 0.50),
    (0.90, 1.00, 0.80),
    (1.00, 9.99, 1.00),
]

PCT_PREMIO_SOBRE_SALARIOS = 0.12  # prêmio estimado diário = 12% do custo de salários
FERIADOS = {
    date(2025, 11, 20): "Consciência Negra",
    date(2025, 12, 25): "Natal",
    date(2026, 1, 1): "Confraternização Universal",
    date(2026, 2, 16): "Carnaval",
    date(2026, 2, 17): "Carnaval",
    date(2026, 4, 3): "Sexta-feira Santa",
    date(2026, 4, 21): "Tiradentes",
    date(2026, 5, 1): "Dia do Trabalho",
    date(2026, 6, 4): "Corpus Christi",
    date(2026, 9, 7): "Independência",
    date(2026, 10, 12): "Nossa Sra. Aparecida",
}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def escrever(nome, cabecalho, linhas):
    with open(PASTA / nome, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)
    print(f"{nome}: {len(linhas)} linhas")


def eh_dia_util(d):
    return d.weekday() < 5 and d not in FERIADOS


def main():
    random.seed(SEMENTE)
    PASTA.mkdir(exist_ok=True)

    # dimensões
    escrever("dim_setor.csv", ["cd_setor", "setor", "ordem_fluxo"],
             [(c, n, c) for c, n, _, _ in SETORES])
    escrever("dim_familia_produto.csv", ["cd_familia", "familia", "categoria"],
             [(c, f, cat) for c, f, cat, _ in FAMILIAS])
    escrever("dim_faixa_premio.csv", ["eficiencia_min", "eficiencia_max", "pct_diaria_premio"],
             FAIXAS_PREMIO)
    escrever("dim_feriado.csv", ["data", "feriado"],
             [(d.isoformat(), n) for d, n in sorted(FERIADOS.items())])

    # calendário
    dias = []
    d = DATA_INICIO
    while d <= DATA_FIM:
        dias.append(d)
        d += timedelta(days=1)
    escrever(
        "dim_calendario.csv",
        ["data", "ano", "mes_num", "mes_ano", "mes_ano_ordem", "dia_semana", "dia_util"],
        [
            (x.isoformat(), x.year, x.month, f"{MESES[x.month - 1]}/{x.year}",
             x.year * 100 + x.month, DIAS[x.weekday()], int(eh_dia_util(x)))
            for x in dias
        ],
    )

    # custo diário por setor (vigente em cada dia; reajuste de 5% em maio/2026
    # para exercitar o histórico: alterar o custo hoje não muda os dias passados)
    custo = []
    for x in dias:
        if not eh_dia_util(x):
            continue
        fator = 1.05 if x >= date(2026, 5, 1) else 1.0
        for cd, _, salarios, _ in SETORES:
            s = round(salarios * fator, 2)
            custo.append((x.isoformat(), cd, s, round(s * PCT_PREMIO_SOBRE_SALARIOS, 2)))
    escrever("fato_custo_setor_dia.csv",
             ["data", "cd_setor", "custo_salarios_dia", "premio_estimado_dia"], custo)

    # produção: cada setor gera de 3 a 7 movimentações por dia útil, somando
    # aproximadamente (meta do dia x eficiência sorteada)
    perfil = {1: 1.00, 2: 0.96, 3: 0.88, 4: 0.82, 5: 1.04, 6: 0.92}  # eficiência média
    producao = []
    n_mov = 0
    n_op = 10000
    for (x, cd, salarios, premio) in [(c[0], c[1], c[2], c[3]) for c in custo]:
        data = date.fromisoformat(x)
        if data > DATA_REFERENCIA:
            continue
        meta_dia = salarios + premio
        eficiencia = max(0.35, random.gauss(perfil[cd], 0.13))
        alvo = meta_dia * eficiencia
        qtd = random.randint(3, 7)
        pesos = [random.uniform(0.5, 1.5) for _ in range(qtd)]
        valor_base = next(v for c, _, _, v in SETORES if c == cd)
        for p in pesos:
            n_mov += 1
            n_op += random.randint(1, 3)
            fam = random.choice(FAMILIAS)
            valor_peca = valor_base * fam[3]
            valor = alvo * p / sum(pesos)
            pecas = max(1, round(valor / valor_peca))
            producao.append((n_mov, x, cd, f"OP{n_op}", fam[0], pecas,
                             round(pecas * valor_peca, 2)))
    escrever("fato_producao.csv",
             ["id_movimentacao", "data", "cd_setor", "nr_op", "cd_familia", "pecas",
              "valor_servico"], producao)

    # fila: onde cada OP em aberto está agora e quanto vale o serviço restante
    fila = []
    for i in range(1, 61):
        cd, _, _, valor_base = random.choice(SETORES)
        fam = random.choice(FAMILIAS)
        pecas = random.randint(40, 900)
        dias_parada = random.choice([0, 1, 2, 3, 4, 5, 7, 9, 12, 16, 20, 27])
        ultima = DATA_REFERENCIA - timedelta(days=dias_parada)
        fila.append((f"OP{20000 + i}", cd, fam[0], pecas,
                     round(pecas * valor_base * fam[3], 2), ultima.isoformat()))
    escrever("fato_fila_op.csv",
             ["nr_op", "cd_setor", "cd_familia", "pecas", "valor_servico_restante",
              "data_ultima_movimentacao"], fila)


if __name__ == "__main__":
    main()
