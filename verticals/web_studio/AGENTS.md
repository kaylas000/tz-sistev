# Контракт агентов Web Studio

| Агент | Модель | Вход | Выход |
|---|---|---|---|
| Planner | llama3.1:8b (T=0.3) | бриф после G1 | JSON DAG: {tasks:[{id,title,deps}]} |
| Coder | qwen2.5-coder:7b (T=0.7) | план + референсы (цвета/шрифты/layout) + Конституция | HTML-артефакт в ```блоке``` |
| Verifier | gemma2:9b (T=0.0) | артефакт | feedback JSON: passed + errors[V-xx,B-xx,Q-xx,A-xx] |
| Fixer | llama3.1:8b (T=0.3) | артефакт + коды ошибок | точечные правки, полный артефакт заново |

Эскалация: >10 циклов → Human Review (R-01). Бюджет: $2/run, $20/день (R-02).
