"""Gera uma PRÉVIA ILUSTRATIVA do painel a partir dos dados sintéticos.

Importante: a imagem NÃO é uma captura de tela do Power BI. Ela é desenhada em
Python (matplotlib) recalculando, com a mesma lógica das medidas DAX, os
indicadores de acompanhamento da meta por setor. Serve para o README mostrar o
que o modelo responde enquanto os visuais do relatório não são publicados.

Uso:
    pip install matplotlib
    python scripts/gerar_previa.py
"""

import csv
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "docs" / "previa-dashboard.png"

# tokens de cor: azul para a série, cinza para referência, cores de status reservadas
AZUL, CINZA, TEXTO, TEXTO_2, FUNDO, GRADE = "#2A5BD7", "#8A94A6", "#1F2633", "#5B6577", "#FFFFFF", "#E6E9EF"
STATUS_COR = {
    "Meta batida": "#2E7D32", "No ritmo": "#2E7D32", "Acelerar": "#B26A00",
    "Meta improvável": "#C62828", "Não atingida": "#C62828", "Sem produção": "#6B7280",
}
STATUS_ICONE = {
    "Meta batida": "✔", "No ritmo": "✔", "Acelerar": "▲",
    "Meta improvável": "✖", "Não atingida": "✖", "Sem produção": "–",
}


def ler(nome):
    with open(DADOS / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def d(txt):
    return date.fromisoformat(txt)


def faixa(eficiencia, faixas):
    for f in faixas:
        if f["min"] <= eficiencia < f["max"]:
            return f["pct"]
    return 0.0


def calcular():
    setores = {int(r["cd_setor"]): r["setor"] for r in ler("dim_setor.csv")}
    cal = {d(r["data"]): int(r["dia_util"]) for r in ler("dim_calendario.csv")}
    producao = [(d(r["data"]), int(r["cd_setor"]), float(r["valor_servico"])) for r in ler("fato_producao.csv")]
    custo = [(d(r["data"]), int(r["cd_setor"]),
              float(r["custo_salarios_dia"]) + float(r["premio_estimado_dia"])) for r in ler("fato_custo_setor_dia.csv")]
    fila = [(int(r["cd_setor"]), float(r["valor_servico_restante"]), d(r["data_ultima_movimentacao"]))
            for r in ler("fato_fila_op.csv")]
    faixas = [{"min": float(r["eficiencia_min"]), "max": float(r["eficiencia_max"]),
               "pct": float(r["pct_diaria_premio"])} for r in ler("dim_faixa_premio.csv")]

    ref = max(p[0] for p in producao)  # Data Referencia
    ini = date(ref.year, ref.month, 1)
    fim = (date(ref.year + (ref.month == 12), ref.month % 12 + 1, 1) - timedelta(days=1))
    uteis = lambda a, b: sum(v for x, v in cal.items() if a <= x <= b)  # noqa: E731
    du_ciclo = uteis(ini, fim)
    du_decorridos = uteis(ini, ref - timedelta(days=1))
    du_restantes = du_ciclo - du_decorridos

    linhas = []
    for cd, nome in setores.items():
        meta = sum(v for x, s, v in custo if s == cd and ini <= x <= fim)
        fat_ciclo = sum(v for x, s, v in producao if s == cd and ini <= x <= ref)
        fat_ontem = sum(v for x, s, v in producao if s == cd and ini <= x < ref)
        ritmo = fat_ontem / du_decorridos if du_decorridos else 0
        falta = max(0.0, meta - fat_ciclo)
        necessario = falta / du_restantes if du_restantes else 0
        esforco = necessario / ritmo if ritmo else 0
        projecao = fat_ontem + ritmo * du_restantes
        pct_atual, pct_proj = fat_ciclo / meta, projecao / meta
        if falta == 0:
            status = "Meta batida"
        elif du_restantes <= 0:
            status = "Não atingida"
        elif du_decorridos > 0 and fat_ontem == 0:
            status = "Sem produção"
        elif esforco <= 1:
            status = "No ritmo"
        elif esforco <= 1.5:
            status = "Acelerar"
        else:
            status = "Meta improvável"
        fila_valor = sum(v for s, v, _ in fila if s == cd)
        linhas.append({
            "setor": nome, "pct_atual": pct_atual, "pct_proj": pct_proj, "status": status,
            "premio_atual": faixa(pct_atual, faixas), "premio_proj": faixa(pct_proj, faixas),
            "fila_cobre": fila_valor / falta if falta else None,
            "paradas": sum(1 for s, _, u in fila if s == cd and u < ref - timedelta(days=15)),
        })
    return ref, ini, fim, du_decorridos, du_ciclo, linhas


def desenhar(ref, ini, fim, du_dec, du_ciclo, linhas):
    ideal = du_dec / du_ciclo
    linhas = sorted(linhas, key=lambda r: r["pct_atual"])
    fig = plt.figure(figsize=(13, 6.6), facecolor=FUNDO, dpi=150)

    fig.text(0.04, 0.93, "Acompanhamento da meta por setor", fontsize=17, fontweight="bold", color=TEXTO)
    fig.text(0.04, 0.885, f"Competência {ini:%m/%Y} · dados até {ref:%d/%m/%Y} · "
             f"{du_dec} de {du_ciclo} dias úteis decorridos", fontsize=10.5, color=TEXTO_2)

    # painel esquerdo: % atual vs ideal vs projetado
    ax = fig.add_axes([0.14, 0.17, 0.36, 0.58], facecolor=FUNDO)
    y = range(len(linhas))
    ax.barh(list(y), [r["pct_atual"] for r in linhas], height=0.5, color=AZUL, zorder=3)
    ax.scatter([r["pct_proj"] for r in linhas], list(y), marker="D", s=46, color=FUNDO,
               edgecolor=TEXTO, linewidth=1.4, zorder=5)
    ax.axvline(ideal, color=CINZA, linestyle=(0, (4, 3)), linewidth=1.4, zorder=4)
    ax.text(ideal, len(linhas) - 0.42, f"ideal hoje {ideal:.0%}", ha="center", va="bottom",
            fontsize=9, color=TEXTO_2)
    ax.axvline(1.0, color=GRADE, linewidth=1.2, zorder=1)
    for i, r in enumerate(linhas):
        ax.text(r["pct_atual"] - 0.015, i, f"{r['pct_atual']:.0%}", ha="right", va="center",
                fontsize=9.5, color="white", fontweight="bold", zorder=6)
    ax.set_yticks(list(y))
    ax.set_yticklabels([r["setor"] for r in linhas], fontsize=10.5, color=TEXTO)
    ax.set_xlim(0, max(1.15, max(r["pct_proj"] for r in linhas) + 0.05))
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.tick_params(axis="x", colors=TEXTO_2, labelsize=9, length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRADE, zorder=0)
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.set_title("Faturamento do ciclo / meta do ciclo", loc="left", fontsize=10.5, color=TEXTO_2, pad=30)
    ax.legend(handles=[
        matplotlib.patches.Patch(color=AZUL, label="% atual"),
        matplotlib.lines.Line2D([], [], marker="D", color="none", markerfacecolor=FUNDO,
                                markeredgecolor=TEXTO, markersize=7, label="% projetado (mantendo o ritmo)"),
    ], loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2, frameon=False, fontsize=9,
        labelcolor=TEXTO_2)

    # painel direito: tabela
    tx = fig.add_axes([0.54, 0.17, 0.43, 0.58], facecolor=FUNDO)
    tx.axis("off")
    tx.set_xlim(0, 1)
    tx.set_ylim(0, len(linhas) + 0.9)
    colunas = [(0.00, "Setor"), (0.26, "Projetado"), (0.43, "Prêmio hoje → fim"), (0.69, "Status")]
    for x, nome in colunas:
        tx.text(x, len(linhas) + 0.35, nome, fontsize=9.5, color=TEXTO_2, va="center", fontweight="bold")
    tx.plot([0, 1], [len(linhas) + 0.05] * 2, color=GRADE, linewidth=1.2)
    for i, r in enumerate(reversed(linhas)):
        yy = len(linhas) - 0.5 - i
        cor = STATUS_COR[r["status"]]
        tx.text(0.00, yy, r["setor"], fontsize=10.5, color=TEXTO, va="center")
        tx.text(0.26, yy, f"{r['pct_proj']:.0%}", fontsize=10.5, color=TEXTO, va="center")
        tx.text(0.43, yy, f"{r['premio_atual']:.0%} → {r['premio_proj']:.0%}", fontsize=10.5,
                color=TEXTO, va="center")
        tx.text(0.69, yy, f"{STATUS_ICONE[r['status']]} {r['status']}", fontsize=10.5, color=cor,
                va="center", fontweight="bold")
        tx.plot([0, 1], [yy - 0.5] * 2, color=GRADE, linewidth=0.8)

    fig.text(0.04, 0.045,
             "Prévia ilustrativa, não é uma captura do Power BI. Desenhada em Python com os dados sintéticos "
             "do repositório e a mesma lógica das medidas DAX.\nTodos os dados são fictícios (Metalúrgica Exemplo).",
             fontsize=8.5, color=TEXTO_2, va="center")
    SAIDA.parent.mkdir(exist_ok=True)
    fig.savefig(SAIDA, facecolor=FUNDO)
    print("gerado:", SAIDA)


if __name__ == "__main__":
    ref, ini, fim, du_dec, du_ciclo, linhas = calcular()
    for r in linhas:
        print(f"{r['setor']:<14} atual {r['pct_atual']:6.1%}  projetado {r['pct_proj']:6.1%}  "
              f"{r['status']:<16} prêmio {r['premio_atual']:.0%}->{r['premio_proj']:.0%}  "
              f"fila cobre {('-' if r['fila_cobre'] is None else format(r['fila_cobre'], '.0%'))}  "
              f"paradas>15d {r['paradas']}")
    desenhar(ref, ini, fim, du_dec, du_ciclo, linhas)
