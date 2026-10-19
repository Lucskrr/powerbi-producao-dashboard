# Dicionário de medidas

45 medidas DAX do modelo, agrupadas por pasta de exibição. Gerado a partir de `MetalurgicaExemplo.SemanticModel/definition/tables/_Medidas.tmdl`.

## Cabeçalho

| Medida | O que faz |
| --- | --- |
| `Data Referencia` | Último dia com produção. No mock é fixa; num cenário real seria TODAY(). |
| `Ultima Atualizacao` | Texto para um cartão no cabeçalho do relatório. |

## Base

| Medida | O que faz |
| --- | --- |
| `Faturamento Produzido` | Soma do valor do serviço das movimentações de OP no contexto de filtro. |
| `Pecas Produzidas` | — |
| `OPs Movimentadas` | — |
| `% Atingimento` | Eficiência = faturamento produzido / meta do período filtrado. |

## Composição da Meta

| Medida | O que faz |
| --- | --- |
| `Custo Salarios Periodo` | Salários + encargos do período, somando o custo vigente em cada dia (usa o histórico: reajustes não alteram dias passados). |
| `Premio Estimado Periodo` | Prêmio pago com 100% de eficiência, somado dia a dia. |
| `Meta Custo Periodo` | Meta de faturamento do período = custo do setor + prêmio estimado. |
| `% Premio na Meta` | — |

## Acompanhamento da Meta › Calendário

| Medida | O que faz |
| --- | --- |
| `Inicio Ciclo` | Primeiro dia da competência (mês) da data de referência. |
| `Fim Ciclo` | — |
| `Dias Uteis Ciclo` | Dias úteis da competência, sem fins de semana e feriados. |
| `Dias Uteis Decorridos` | Dias úteis da competência antes da data de referência. |
| `Dias Uteis Restantes` | Dias úteis que faltam na competência, contando o dia de referência. |

## Acompanhamento da Meta

| Medida | O que faz |
| --- | --- |
| `Meta do Ciclo` | Meta da competência inteira (histórico nos dias passados, custo vigente nos dias futuros). |
| `Faturamento Ciclo` | Faturamento da competência até a data de referência (inclusive). |
| `Faturamento Ate Ontem` | Faturamento nos dias já encerrados da competência (base do ritmo). |
| `% Atual do Ciclo` | Faturamento da competência até agora / meta da competência inteira. |
| `Ritmo Diario` | Faturamento médio por dia útil já encerrado. |
| `Falta para Meta` | Quanto falta faturar para bater 100% da meta (0 se já bateu). |
| `Necessario por Dia` | Faturamento necessário por dia útil restante para bater a meta. |
| `Esforco x Ritmo` | Necessário por dia / ritmo atual. Até 1x = no ritmo; 2x = precisa dobrar a produção. |
| `Projecao Faturamento` | Faturamento previsto no fim da competência mantendo o ritmo atual. |
| `% Projetado` | Eficiência prevista no fim da competência mantendo o ritmo atual. |
| `Status` | Meta batida / No ritmo / Acelerar (até 1,5x o ritmo) / Meta improvável / Não atingida / Sem produção. |
| `Cor Status` | Cor para formatação condicional (Valor do campo) da coluna Status. |
| `Valor Medio por Peca` | — |
| `Pecas Faltantes` | Peças que faltam produzir para bater a meta, ao valor por peça típico do setor. |

## Prêmio

| Medida | O que faz |
| --- | --- |
| `Faixa Premio Atual` | % da diária de prêmio correspondente à eficiência atual da competência. |
| `Faixa Premio Projetada` | % da diária de prêmio que o setor atinge no fim da competência mantendo o ritmo. |
| `Eficiencia Minima do Premio` | Eficiência a partir da qual o prêmio começa a ser pago. |
| `Falta para Entrar no Premio` | Faturamento que falta para o setor atingir a eficiência mínima do prêmio. |
| `Valor de 1 Ponto` | Quanto de faturamento vale 1 ponto percentual de eficiência na competência. |

## Fila de OPs

| Medida | O que faz |
| --- | --- |
| `Fila no Setor` | Valor do serviço das OPs que estão agora no setor (peças x valor do serviço). |
| `OPs na Fila` | — |
| `Fila Cobre a Falta` | Fila / falta para a meta. 100% ou mais = o setor tem trabalho suficiente; abaixo, falta OP programada (problema de PCP, não de produtividade). |
| `OPs Paradas 15 Dias` | OPs no setor sem movimentação há mais de 15 dias (possível OP esquecida ou travada). |

## Mix de Produto

| Medida | O que faz |
| --- | --- |
| `Valor Medio por Peca Tipico` | Valor por peça normal do setor (todas as famílias) nos últimos 90 dias. |
| `Indice de Complexidade` | Valor por peça do período / valor típico (90 dias). Acima de 1x = peças mais trabalhosas que o normal. |
| `% do Faturamento` | Participação da família de produto no faturamento do setor no período. |
| `Pontos de Eficiencia` | Quantos pontos da eficiência do setor vieram de cada família (a soma das famílias = % Atingimento do setor). |
| `Familias Distintas` | Quantas famílias o setor trabalhou no período. Muitas no mesmo dia = mais troca de ferramenta/setup e menos eficiência. |

## Velocímetro

| Medida | O que faz |
| --- | --- |
| `Ideal Hoje` | Eficiência ideal para hoje = dias úteis encerrados / dias úteis da competência. Usar em "Valor de destino" dos velocímetros. |
| `Cor Velocimetro` | Cor do arco do velocímetro. Verde = no ideal ou acima; amarelo = até 20% abaixo; vermelho = mais de 20% abaixo. |
