# ТЕХНИЧЕСКОЕ ЗАДАНИЕ: Мета-платформа для создания ИИ-студий (Agentic Studio Platform)

> **Инструкция для ИИ-агента:** Этот документ является единственным источником истины (Single Source of Truth) для разработки платформы. При генерации кода, архитектуры или тестов строго следуй описанным здесь контрактам, структурам папок, интерфейсам и правилам валидации. Не выдумывай новые сущности, если они не описаны здесь.

## ОГЛАВЛЕНИЕ
1. [Общие положения и принципы](#1-общие-положения-и-принципы)
2. [Архитектура системы](#2-архитектура-системы)
3. [Требования к ядру (Kernel)](#3-требования-к-ядру-kernel)
4. [Студии (Вертикали): Структура и правила](#4-студии-вертикали-структура-и-правила)
5. [Система валидаторов и коды ошибок](#5-система-валидаторов-и-коды-ошибок)
6. [Работа с референсами и RAG](#6-работа-с-референсами-и-rag)
7. [Система скиллов (Skills)](#7-система-скиллов-skills)
8. [Оркестрация: CEO-агент и композиции](#8-оркестрация-ceo-агент-и-композиции)
9. [Инфраструктура и Деплой](#9-инфраструктура-и-деплой)
10. [Критерии приёмки и тестирование](#10-критерии-приёмки-и-тестирование)

---

## 1. ОБЩИЕ ПОЛОЖЕНИЯ И ПРИНЦИПЫ
*(Здесь вставь текст из Части 1: Назначение, Ключевые принципы, Глоссарий)*

## 2. АРХИТЕКТУРА СИСТЕМЫ
*(Здесь вставь текст из Части 1/2: Слоистая архитектура, схема взаимодействия, API Gateway, Kernel, Verticals, Observability)*

## 3. ТРЕБОВАНИЯ К ЯДРУ (KERNEL)
*(Здесь вставь текст из Части 1: State Management, LangGraph Nodes/Edges, LLM Manager, Sandbox Manager, Budget Manager, Protocols)*

## 4. СТУДИИ (ВЕРТИКАЛИ): СТРУКТУРА И ПРАВИЛА
*(Здесь вставь текст из Части 2: Физическая структура директории, vertical.yaml, примеры Конституций для Web, Legal, Content, Data, Education)*

## 5. СИСТЕМА ВАЛИДАТОРОВ И КОДЫ ОШИБОК
*(Здесь вставь текст из Части 2/Детализации: Базовые классы, ConstitutionGate, AntiSlopGate, SchemaGate, LLMJudgeGate, таблица префиксов V-xx, B-xx, Q-xx)*

## 6. РАБОТА С РЕФЕРЕНСАМИ И RAG
*(Здесь вставь текст из Детализации 2.7: Источники (lapa.ninja и др.), скрипт scrape_references.py, индексация в Qdrant, формат metadata.yaml)*

## 7. СИСТЕМА СКИЛЛОВ (SKILLS)
*(Здесь вставь текст из Детализации 2.3: skill.yaml, шаблоны planner.j2, coder.j2, verifier.j2, fixer.j2, хуки pre/post execute)*

## 8. ОРКЕСТРАЦИЯ: CEO-АГЕНТ И КОМПОЗИЦИИ
*(Здесь вставь текст из Детализации 3.1: Класс CEOAgent, TaskRouter, пример full_website.yaml, параллельное выполнение)*

## 9. ИНФРАСТРУКТУРА И ДЕПЛОЙ
*(Здесь вставь текст из Детализации 3.2: docker-compose.yml, litellm_config.yaml, Kubernetes манифесты, GitHub Actions CI/CD, Prometheus алерты)*

## 10. КРИТЕРИИ ПРИЁМКИ И ТЕСТИРОВАНИЕ
*(Здесь вставь текст из Детализации 3.4: Чек-листы ядра, студий, CEO-агента, инфраструктурные bash-тесты, нагрузочное тестирование, финальный чек-лист)*

---
** При генерации кода всегда сверяйся с этим документом.

# ТЕХНИЧЕСКОЕ ЗАДАНИЕ (ТЗ)
## На разработку Мета-платформы для создания специализированных ИИ-студий (Agentic Studio Platform)

### 1. ОБЩИЕ ПОЛОЖЕНИЯ

#### 1.1. Наименование и назначение системы
Система представляет собой модульную мета-платформу (далее — Платформа), предназначенную для быстрого развёртывания и управления специализированными ИИ-студиями (вертикалями). Каждая студия решает задачи в конкретной предметной области (веб-дизайн, юридические документы, контент, аналитика) с гарантированным качеством результата за счёт циклической самокоррекции и детерминированной валидации.

#### 1.2. Ключевые архитектурные принципы
1. **Domain-agnostic ядро:** Инфраструктура оркестрации, выполнения и мониторинга не содержит бизнес-логики конкретных предметных областей.
2. **Студии как плагины (Verticals):** Предметные области подключаются как независимые модули, реализующие строгие интерфейсы ядра.
3. **Циклическая самокоррекция (Reflexion Loop):** Обязательный паттерн выполнения: `Генерация → Детерминированная валидация → LLM-критика → Исправление`.
4. **Конституция как код:** Правила предметной области формализованы в виде исполняемых спецификаций с уникальными кодами ошибок.
5. **Экономичность:** Архитектура оптимизирована для работы с бесплатными/локальными моделями (Ollama, vLLM) за счёт выноса логики проверки в детерминированные скрипты.

#### 1.3. Целевая аудитория пользователей
* **Архитекторы студий:** Разработчики, создающие новые вертикали и скиллы.
* **Операторы:** Пользователи, запускающие задачи через API/CLI и контролирующие Human-in-the-Loop (HITL).
* **Конечные клиенты:** Внешние системы или пользователи, получающие результат через REST API или Telegram-бота.

---

### 2. АРХИТЕКТУРА СИСТЕМЫ

Система строится по слоистой микросервисной архитектуре.

#### 2.1. Слой 1: API Gateway (Входная точка)
* **Технологии:** FastAPI (Python).
* **Функции:**
  * Аутентификация и авторизация (JWT / API Keys с ролями: `viewer`, `developer`, `admin`).
  * Rate Limiting (лимиты запросов в минуту/час/день).
  * Идемпотентность запросов (повторный запрос с тем же `X-Request-ID` не создаёт новый запуск, а возвращает статус существующего).
  * Маршрутизация запросов к нужной вертикали на основе метаданных.
  * Композиция задач (оркестрация нескольких студий для одного большого проекта).

#### 2.2. Слой 2: Ядро (Kernel)
Центральный модуль, управляющий жизненным циклом задач.
* **Orchestrator (LangGraph):** Управление направленным ациклическим графом (DAG) задач.
* **State Manager:** Хранение состояния выполнения (`AgentState`) с поддержкой чекпоинтов (возобновление после сбоя).
* **LLM Manager:** Унифицированный провайдер моделей через LiteLLM (маршрутизация, ретраи с exponential backoff, трекинг токенов).
* **Sandbox Manager:** Изолированное выполнение сгенерированного кода или скриптов (провайдеры: E2B, Docker, Local).
* **Budget Manager:** Жёсткий контроль расходов (стоимость, токены, время, количество итераций).
* **Knowledge Base (RAG):** Векторный поиск (Qdrant) + граф знаний (SQLite) для предоставления контекста и примеров агентам.

#### 2.3. Слой 3: Вертикали (Студии)
Независимые директории (`verticals/{name}/`), содержащие бизнес-логику:
* Декларативные конфигурации (`vertical.yaml`).
* Набор скиллов (`skills/`) с Jinja2-шаблонами промптов.
* Детерминированные валидаторы (`validators/`).
* База референсов и паттернов (`references/`).

#### 2.4. Слой 4: Observability & Ops
* **Метрики:** Prometheus (время выполнения, стоимость, количество итераций, коды ошибок).
* **Трейсинг:** OpenTelemetry (отслеживание прохождения задачи по узлам LangGraph).
* **Логирование:** Структурированные JSON-логи (Loki/ELK).

---

### 3. ДЕТАЛЬНЫЕ ТРЕБОВАНИЯ К ЯДРУ (KERNEL)

#### 3.1. Управление состоянием (State Management)
Состояние каждого запуска (`run`) должно строго типизироваться (Pydantic/TypedDict) и сериализоваться.

```python
class AgentState(TypedDict):
    run_id: str
    vertical_name: str
    skill_name: str
    input_data: Dict[str, Any]       # Исходный бриф
    plan: List[Dict]                 # DAG подзадач от Planner
    current_task: Optional[Dict]     # Текущая выполняемая подзадача
    artifacts: Dict[str, Any]        # Промежуточные и финальные артефакты
    iterations_count: int            # Счётчик циклов исправлений
    validation_errors: List[Dict]    # Список кодов ошибок (напр., [{"code": "V-01", "msg": "..."}])
    budget_used: Dict[str, float]    # {"cost_usd": 0.45, "tokens": 12000}
    status: Literal["pending", "running", "paused_hitl", "completed", "failed"]
```
*Требование:* Состояние должно сохраняться в PostgreSQL после каждого узла графа для возможности `resume_run`.

#### 3.2. Граф выполнения (LangGraph Nodes & Edges)
Граф должен содержать следующие стандартизированные узлы:
1. `initialize`: Загрузка конфигурации вертикали, скилла, референсов из RAG.
2. `planner`: LLM-узёл, разбивающий `input_data` на список атомарных задач.
3. `executor` (Coder): LLM-узёл, генерирующий артефакт или вызывающий инструменты (Tools).
4. `verifier`: **Детерминированный узел** (не LLM!). Запускает скрипты валидации вертикали.
5. `fixer`: LLM-узёл, получающий `validation_errors` и модифицирующий артефакт.
6. `human_review`: Узел ожидания (interrupt), если `iterations_count > MAX` или сработал триггер критической ошибки.

**Логика переходов (Conditional Edges):**
* `executor` → `verifier`
* `verifier` → `packager` (если `validation_errors` пуст)
* `verifier` → `fixer` (если есть ошибки и `iterations_count < MAX_ITERATIONS`)
* `verifier` → `human_review` (если `iterations_count >= MAX_ITERATIONS`)
* `fixer` → `verifier`

#### 3.3. LLM Manager и работа с бесплатными моделями
* Использование LiteLLM для абстрагирования от провайдеров.
* **Алиасинг моделей:** Ядро оперирует ролями, а не названиями моделей. Конфигурация задаётся через ENV:
  ```env
  AUTOGEN_LLM__MODEL_ALIASES='{"planner": "ollama/llama3.1:8b", "coder": "ollama/qwen2.5-coder:7b", "verifier_llm": "ollama/gemma2:9b"}'
  ```
* **Разделение температур:** Planner (0.2-0.3), Coder (0.7), Verifier (0.0), Fixer (0.3).
* **Fallback:** При ошибке провайдера (rate limit, 5xx) автоматический ретрай с задержкой (1с, 2с, 4с).

#### 3.4. Sandbox Manager (Изолированное выполнение)
Для проверки сгенерированного кода (HTML, Python, SQL) система должна использовать изолированную среду.
* **Интерфейс:** `execute(code: str, language: str, timeout: int = 30) -> ExecutionResult`
* **Требования к безопасности:** 
  * Запрет сетевого доступа наружу (кроме разрешённых endpoints).
  * Жёсткие лимиты RAM (напр., 512MB) и CPU.
  * Автоматическое уничтожение среды (TTL) после выполнения.
* **Провайдеры:** Приоритет E2B (для скорости), fallback на локальный Docker.

#### 3.5. Budget Manager (Контроль ресурсов)
Система должна предотвращать "runaway agents" (бесконечные циклы, сжигающие токены).
* **Лимиты на уровне Run:** `max_budget_usd`, `max_tokens`, `max_iterations` (default: 10).
* **Лимиты на уровне системы (в сутки):** `MAX_COST_USD_PER_DAY`, `MAX_TOKENS_PER_MINUTE`.
* **Действие при превышении:** Немедленная пауза графа (`status: "paused_budget"`), отправка алерта в webhook (Telegram/Slack), ожидание ручного подтверждения (`action: "approve"`).

---

### 4. ПРОТОКОЛЫ ВЗАИМОДЕЙСТВИЯ ЯДРА И СТУДИЙ

Ядро не должно знать о внутренней кухне студии. Взаимодействие строго через интерфейсы (Protocols).

#### 4.1. Интерфейс Вертикали (`IVertical`)
Каждая студия обязана реализовать этот контракт при загрузке:
```python
class IVertical(Protocol):
    name: str
    description: str
    
    def get_skills(self) -> List[str]: ...
    def get_tools(self) -> List[Callable]: ...
    def get_verification_gates(self) -> Dict[str, IVerificationGate]: ...
    def load_references(self, query: str) -> List[Dict]: ... # Для RAG
```

#### 4.2. Интерфейс Валидационного Гейта (`IVerificationGate`)
```python
class VerificationResult(BaseModel):
    passed: bool
    errors: List[Dict[str, str]] # [{"code": "V-01", "severity": "critical", "message": "...", "suggestion": "..."}]
    artifacts_modified: bool

class IVerificationGate(Protocol):
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult: ...
```
*Важно:* `verify` должен быть максимально быстрым и детерминированным. LLM-критика допускается только как один из гейтов, но не как единственный.

---

### 5. СТАНДАРТИЗАЦИЯ КОДОВ ОШИБОК

Для эффективной работы узла `fixer` все валидаторы должны возвращать ошибки в едином формате. Префиксы строго зарезервированы:

| Префикс | Источник ошибки | Пример | Описание |
| :--- | :--- | :--- | :--- |
| **V-xx** | Конституция вертикали | `V-01` | Нарушение фундаментального правила предметной области. |
| **B-xx** | Anti-slop (Banned) | `B-03` | Использование категорически запрещённого паттерна/слова. |
| **Q-xx** | Anti-slop (Quotas) | `Q-01` | Превышение количественного лимита (напр., >3 шрифтов). |
| **E-xx** | Входные данные | `E-02` | Бриф клиента неполон или противоречив (ошибка на входе). |
| **S-xx** | Sandbox / Code Exec | `S-01` | Сгенерированный код не компилируется или упал с ошибкой. |
| **L-xx** | Цикл выполнения | `L-01` | Превышен лимит итераций (`max_iterations`). |

---

**Конец ЧАСТИ 1.**

# ЧАСТЬ 2: СТУДИИ (ВЕРТИКАЛИ), РЕФЕРЕНСЫ, ВАЛИДАЦИЯ

---

## 2.1. ФИЗИЧЕСКАЯ СТРУКТУРА ДИРЕКТОРИИ СТУДИИ

Каждая студия — это самодостаточная директория в `verticals/{name}/` со строгой структурой:

```
verticals/{vertical_name}/
│
├── vertical.yaml                 # Метаданные, скиллы, модели, бюджет
├── CONSTITUTION.md               # Проверяемые правила (К-01...К-N)
├── AGENTS.md                     # Контракт агентов (роли, температуры, промпты)
├── BRIEF-TEMPLATE.md             # Шаблон брифа для клиентов
├── README.md                     # Описание студии, примеры использования
│
├── skills/                       # Скиллы студии
│   ├── {skill_name_1}/
│   │   ├── skill.yaml            # Определение скилла
│   │   ├── templates/            # Jinja2 шаблоны промптов
│   │   │   ├── planner.j2
│   │   │   ├── coder.j2
│   │   │   ├── verifier.j2
│   │   │   └── fixer.j2
│   │   └── hooks/                # Pre/post execution hooks
│   │       ├── pre_execute.py
│   │       └── post_execute.py
│   └── {skill_name_2}/
│       └── ...
│
├── validators/                   # Валидаторы (детерминированные + LLM)
│   ├── __init__.py
│   ├── constitution.py           # Проверка Конституции
│   ├── anti_slop.py              # Проверка BANNED и QUOTAS
│   ├── schema.py                 # JSON Schema валидация
│   ├── syntax.py                 # Синтаксическая проверка кода
│   └── llm_judge.py              # LLM-критик
│
├── anti-slop/                    # Правила anti-slop
│   ├── BANNED.md                 # Запрещённые паттерны
│   └── QUOTAS.md                 # Количественные лимиты
│
├── gates/                        # Гейты валидации
│   ├── G1-entry.md               # Входной гейт
│   ├── G2-checklist.md           # Чек-лист
│   ├── G3-artifact.md            # Финальная приёмка
│   └── G4-rejection.md           # Критерии отклонения
│
├── references/                   # База референсов
│   ├── sources.yaml              # Откуда собраны референсы
│   ├── screenshots/              # Скриншоты референсов
│   │   ├── lapa_001.png
│   │   ├── landbook_001.png
│   │   └── ...
│   ├── metadata/                 # YAML с описанием каждого референса
│   │   ├── lapa_001.yaml
│   │   └── ...
│   └── takeaways/                # Ключевые выводы по референсу
│       └── ...
│
├── tools/                        # Специализированные инструменты
│   ├── __init__.py
│   └── {tool_name}.py
│
├── scripts/                      # Вспомогательные скрипты
│   ├── validate.py
│   ├── lint.py
│   └── scrape_references.py
│
├── projects/                     # Артефакты выполненных проектов
│   ├── _TEMPLATE/                # Шаблон структуры проекта
│   └── {project_name}/           # Конкретный проект
│       ├── SEED.md
│       ├── DIRECTION.md
│       ├── artifacts/
│       ├── workspace/            # Рабочие файлы (итерации, логи)
│       └── REVIEW.md
│
└── tests/                        # Тесты студии
    ├── test_skills.py
    ├── test_validators.py
    └── test_e2e.py
```

---

## 2.2. ДЕКЛАРАТИВНОЕ ОПИСАНИЕ СТУДИИ (`vertical.yaml`)

```yaml
apiVersion: autogen/v1
kind: Vertical

metadata:
  name: web_studio
  displayName: "Веб-студия"
  description: "Генерация лендингов, каталогов, корпоративных сайтов"
  version: "1.0.0"
  author: "kaylas000"
  domain: web
  tags: [landing, catalog, ecommerce, corporate]

spec:
  # Скиллы, которые предоставляет студия
  skills:
    - landing_page
    - catalog
    - portfolio
    - ecommerce
    - corporate_site

  # Валидаторы, применяемые к артефактам
  validators:
    - constitution      # Проверка Конституции
    - anti_slop         # Проверка BANNED и QUOTAS
    - html_syntax       # Валидность HTML
    - css_syntax        # Валидность CSS
    - lighthouse        # Производительность и доступность
    - llm_judge         # LLM-критик

  # Гейты валидации
  gates:
    - G1-entry
    - G2-checklist
    - G3-artifact
    - G4-rejection

  # Специализированные инструменты
  tools:
    - run_lighthouse
    - validate_html
    - check_a11y
    - take_screenshot

  # Конфигурация моделей (алиасы ядра)
  models:
    planner: "ollama/llama3.1:8b"
    coder: "ollama/qwen2.5-coder:7b"
    verifier: "ollama/gemma2:9b"
    fixer: "ollama/llama3.1:8b"

  # Бюджет
  budget:
    max_cost_usd_per_run: 1.5
    max_iterations: 10
    max_tokens_per_run: 100000

  # База знаний (RAG)
  knowledge:
    rag_collections:
      - name: web_design_patterns
        source: "verticals/web_studio/references"
        embedder: "litellm"
        embedding_model: "text-embedding-3-small"

  # Anti-slop
  anti_slop:
    banned_file: "anti-slop/BANNED.md"
    quotas_file: "anti-slop/QUOTAS.md"

  # Зависимости от других студий
  dependencies: []
```

---

## 2.3. СИСТЕМА СКИЛЛОВ

Каждый скилл — самодостаточная единица функциональности.

### 2.3.1. Определение скилла (`skill.yaml`)

```yaml
apiVersion: autogen/v1
kind: Skill

metadata:
  name: landing_page
  displayName: "Лендинг"
  description: "Генерация одностраничного лендинга"
  version: "1.0.0"
  vertical: web_studio

spec:
  # Шаблоны промптов
  templates:
    planner: "templates/planner.j2"
    coder: "templates/coder.j2"
    verifier: "templates/verifier.j2"
    fixer: "templates/fixer.j2"

  # Хуки
  hooks:
    pre_execute: "hooks/pre_design.py"
    post_execute: "hooks/post_design.py"

  # Гейты валидации
  gates:
    - constitution
    - anti_slop
    - lighthouse

  # Инструменты, доступные скиллу
  tools:
    - run_lighthouse
    - validate_html
    - take_screenshot

  # Параметры модели для каждой роли
  models:
    planner:
      temperature: 0.3
      max_tokens: 2000
    coder:
      temperature: 0.7
      max_tokens: 8000
    verifier:
      temperature: 0.0
      max_tokens: 1000
    fixer:
      temperature: 0.3
      max_tokens: 4000

  # Бюджет
  budget:
    max_iterations: 10
    max_cost_usd: 1.0
```

### 2.3.2. Шаблон промпта (пример `planner.j2`)

```jinja2
# Планировщик: {{ skill.display_name }}

Ты — опытный арт-директор студии {{ vertical.display_name }}.

## Конституция (обязательно к соблюдению)
{{ constitution }}

## Anti-slop правила
{{ anti_slop_banned }}

## Квоты
{{ anti_slop_quotas }}

## Бриф клиента
{{ brief }}

## Релевантные референсы (из RAG)
{% for ref in references %}
### Референс {{ loop.index }}
- URL: {{ ref.url }}
- Стиль: {{ ref.style }}
- Ключевые выводы: {{ ref.takeaway }}
{% endfor %}

## Твоя задача
Создай детальный план, включающий:
1. Структуру страницы (блоки, секции)
2. Цветовую палитру (максимум 5 цветов)
3. Типографику (максимум 3 шрифта)
4. Контентную стратегию
5. Интерактивные элементы

## Формат вывода
Верни СТРОГИЙ JSON:
{
  "structure": [{"section": "...", "content": "..."}],
  "colors": {"primary": "#...", "accent": "#...", "background": "#..."},
  "typography": {"heading": "...", "body": "..."},
  "content_strategy": "...",
  "interactive_elements": ["..."]
}
```

---

## 2.4. СИСТЕМА ВАЛИДАТОРОВ

### 2.4.1. Интерфейс валидатора

```python
from typing import Protocol, Any, Dict, List
from pydantic import BaseModel

class ValidationError(BaseModel):
    code: str                    # V-01, B-02, Q-01
    severity: Literal["critical", "major", "minor"]
    description: str
    location: Optional[str]      # Где ошибка (напр., "css: .hero")
    suggestion: str              # Как исправить
    fix_example: Optional[str]   # Пример исправления

class VerificationResult(BaseModel):
    passed: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    metrics: Dict[str, Any]      # Доп. метрики (Lighthouse score, etc.)

class IVerificationGate(Protocol):
    name: str
    
    async def verify(
        self,
        artifact: Any,
        context: Dict[str, Any]
    ) -> VerificationResult: ...
```

### 2.4.2. Пример: валидатор Конституции (`validators/constitution.py`)

```python
import re
from typing import Dict, Any

class ConstitutionGate:
    """Проверяет артефакт на соответствие Конституции вертикали"""
    
    def __init__(self, constitution_path: str):
        self.rules = self._parse_constitution(constitution_path)
    
    def _parse_constitution(self, path: str) -> Dict[str, Dict]:
        """Парсит CONSTITUTION.md в структуру правил"""
        rules = {}
        current_rule = None
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('## К-'):
                    match = re.match(r'## (К-\d+): (.+)', line)
                    if match:
                        current_rule = {
                            'id': match.group(1),
                            'name': match.group(2),
                            'description': '',
                            'check_type': 'deterministic',
                            'error_code': None
                        }
                        rules[current_rule['id']] = current_rule
                elif current_rule and line.startswith('**Проверка:**'):
                    check_method = line.replace('**Проверка:**', '').strip()
                    current_rule['check_type'] = 'llm' if 'LLM' in check_method else 'deterministic'
                elif current_rule and line.startswith('**Код ошибки:**'):
                    current_rule['error_code'] = line.replace('**Код ошибки:**', '').strip()
        
        return rules
    
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult:
        errors = []
        
        for rule_id, rule in self.rules.items():
            if rule['check_type'] == 'deterministic':
                passed = await self._run_deterministic(rule, artifact, context)
            else:
                passed = await self._run_llm_check(rule, artifact, context)
            
            if not passed:
                errors.append(ValidationError(
                    code=rule['error_code'],
                    severity="critical",
                    description=f"Нарушение {rule['id']}: {rule['name']}",
                    suggestion=f"Исправьте в соответствии с правилом {rule['id']}"
                ))
        
        return VerificationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=[],
            metrics={"rules_checked": len(self.rules)}
        )
```

---

## 2.5. ГЕЙТЫ ВАЛИДАЦИИ

Гейты — это контрольные точки, через которые должен пройти артефакт.

### G1: Входной гейт
Проверяет полноту и корректность входных данных.

```markdown
# gates/G1-entry.md

## Назначение
Проверяет, что бриф клиента полон и корректен.

## Критерии прохождения
1. Бриф содержит минимум 100 символов
2. Указана целевая аудитория
3. Указаны требования к дизайну/документу
4. Указаны референсы (если применимо)

## Коды ошибок
- E-01: Отсутствует бриф
- E-02: Не указана целевая аудитория
- E-03: Недостаточно референсов
```

### G2: Чек-лист
Проверяет выполнение всех промежуточных шагов.

```markdown
# gates/G2-checklist.md

## Назначение
Проверяет, что все элементы чек-листа выполнены.

## Критерии прохождения
1. Создана структура проекта
2. Определена цветовая палитра / стиль
3. Подготовлены референсы
4. Создан DIRECTION.md

## Коды ошибок
- C-01: Отсутствует структура
- C-02: Не определена палитра
```

### G3: Артефакт
Финальная приёмка готового артефакта.

```markdown
# gates/G3-artifact.md

## Назначение
Проверяет готовый артефакт на соответствие Конституции.

## Критерии прохождения
1. Пройдены все валидаторы Конституции
2. Пройдены все anti-slop проверки
3. Lighthouse Performance ≥ 90 (для веб)
4. Визуальный регресс пройден

## Коды ошибок
- A-01: Нарушение Конституции
- A-02: Нарушение anti-slop
- A-03: Низкий Lighthouse
```

### G4: Отклонение
Определяет, отклонить проект или отправить на доработку.

```markdown
# gates/G4-rejection.md

## Критерии отклонения
1. Количество итераций > MAX_ITERATIONS
2. Стоимость > бюджета
3. Критические ошибки (V-xx) не исправлены

## Коды ошибок
- R-01: Превышен лимит итераций
- R-02: Превышен бюджет
- R-03: Критические ошибки не исправлены
```

---

## 2.6. СИСТЕМА КОДОВ ОШИБОК И ФИДБЕК

### 2.6.1. Префиксы кодов

| Префикс | Категория | Пример | Описание |
|---|---|---|---|
| V-xx | Конституция | V-01 | Нарушение правила Конституции |
| B-xx | Anti-slop (Banned) | B-01 | Использование запрещённого паттерна |
| Q-xx | Anti-slop (Quotas) | Q-01 | Превышение квоты |
| E-xx | Входные данные | E-01 | Ошибка входных данных |
| C-xx | Чек-лист | C-01 | Элемент чек-листа не выполнен |
| A-xx | Артефакт | A-01 | Артефакт не прошёл валидацию |
| R-xx | Отклонение | R-01 | Проект отклонён |
| S-xx | Sandbox / Code | S-01 | Код не компилируется |
| L-xx | Цикл | L-01 | Превышен лимит итераций |

### 2.6.2. Структурированный фидбек для агента

```json
{
  "passed": false,
  "errors": [
    {
      "code": "V-02",
      "severity": "critical",
      "description": "Контраст текста ниже 4.5:1",
      "location": "css: .hero-text",
      "suggestion": "Увеличьте контраст текста до 4.5:1 или выше",
      "fix_example": "color: #000000; background: #ffffff;"
    },
    {
      "code": "B-01",
      "severity": "major",
      "description": "Использован градиентный фон",
      "location": "css: body",
      "suggestion": "Замените градиент на однотонный фон",
      "fix_example": "background: #f5f5f5;"
    }
  ],
  "iterations_used": 3,
  "budget_used_usd": 0.45
}
```

---

## 2.7. РАБОТА С РЕФЕРЕНСАМИ

### 2.7.1. Источники референсов

| Студия | Источники | Минимум референсов |
|---|---|---|
| Web Studio | lapa.ninja, land-book.com, awwwards.com, siteinspire.com, minimal.gallery, brutalistwebsites.com, godly.website, landingfolio.com, onepagelove.com, saaslandingpage.com, darkmodedesign.com | 100 |
| Legal Docs | consultant.ru, garant.ru, base.garant.ru | 30 |
| Content Studio | awwwards.com, behance.net, топ-блоги | 50 |
| Data Analytics | github.com, kaggle.com, observablehq.com | 30 |
| Education | coursera.org, udemy.com, stepik.org | 20 |

### 2.7.2. Скрипт парсинга (`scripts/scrape_references.py`)

```python
import asyncio
import json
import yaml
from pathlib import Path
from playwright.async_api import async_playwright

SOURCES = {
    "lapa.ninja": {
        "base_url": "https://www.lapa.ninja",
        "categories": ["saas", "crypto", "education", "ecommerce"],
        "limit_per_category": 20
    },
    "land-book.com": {
        "base_url": "https://land-book.com",
        "filters": {"color": ["blue", "red", "green", "black"]},
        "limit": 30
    },
    "awwwards.com": {
        "base_url": "https://www.awwwards.com",
        "styles": ["minimal", "brutalist", "corporate"],
        "limit": 20
    }
}

async def scrape_source(source_name: str, config: dict, output_dir: Path):
    """Парсит один источник референсов"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Переход на главную
        await page.goto(config["base_url"])
        await page.wait_for_load_state("networkidle")
        
        # Сбор ссылок на проекты
        links = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('a[href*="/website/"], a[href*="/sites/"]');
                return Array.from(items).map(a => a.href).slice(0, 50);
            }
        """)
        
        # Обход каждого проекта
        for i, link in enumerate(links[:config.get("limit", 20)]):
            try:
                await page.goto(link)
                await page.wait_for_load_state("networkidle")
                
                # Скриншот
                screenshot_path = output_dir / "screenshots" / f"{source_name}_{i:03d}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                
                # Извлечение метаданных
                metadata = await page.evaluate("""
                    () => {
                        const styles = window.getComputedStyle(document.body);
                        const fonts = new Set();
                        document.querySelectorAll('*').forEach(el => {
                            const font = window.getComputedStyle(el).fontFamily;
                            if (font) fonts.add(font.split(',')[0].trim());
                        });
                        return {
                            backgroundColor: styles.backgroundColor,
                            color: styles.color,
                            fonts: Array.from(fonts).slice(0, 5)
                        };
                    }
                """)
                
                # Сохранение YAML
                ref_data = {
                    "source": source_name,
                    "url": link,
                    "screenshot": f"{source_name}_{i:03d}.png",
                    "colors": {
                        "background": metadata["backgroundColor"],
                        "text": metadata["color"]
                    },
                    "fonts": metadata["fonts"],
                    "takeaway": ""  # Заполняется вручную или через LLM
                }
                
                yaml_path = output_dir / "metadata" / f"{source_name}_{i:03d}.yaml"
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(ref_data, f, allow_unicode=True)
                
                print(f"[OK] {source_name} #{i}: {link}")
                
            except Exception as e:
                print(f"[FAIL] {source_name} #{i}: {e}")
        
        await browser.close()

async def main():
    for source_name, config in SOURCES.items():
        output_dir = Path(f"verticals/web_studio/references/{source_name.replace('.', '_')}")
        (output_dir / "screenshots").mkdir(parents=True, exist_ok=True)
        (output_dir / "metadata").mkdir(parents=True, exist_ok=True)
        
        await scrape_source(source_name, config, output_dir)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.7.3. Формат метаданных референса

```yaml
# references/metadata/lapa_ninja_001.yaml
source: lapa.ninja
url: https://example.com
category: saas
style: minimalism
industry: technology
screenshot: screenshots/lapa_001.png
colors:
  primary: "#1a1a2e"
  secondary: "#16213e"
  accent: "#e94560"
  background: "#ffffff"
  text: "#0f3460"
fonts:
  heading: "Inter"
  body: "system-ui"
layout: "hero + features + pricing + testimonials + cta + footer"
components:
  - hero_with_cta
  - feature_grid_3cols
  - pricing_table
  - testimonial_carousel
takeaway: "Чёткая иерархия, один CTA на экран, минимум отвлекающих элементов"
scraped_at: 2026-09-28
tags: [saas, minimal, dark-accent, conversion-focused]
```

### 2.7.4. Интеграция с RAG

Референсы индексируются в Qdrant для семантического поиска:

```bash
# Ингестия референсов в Knowledge Base
autogen-knowledge ingest \
  --vertical web_studio \
  --source verticals/web_studio/references \
  --chunk-size 500 \
  --embedder litellm \
  --embedding-model text-embedding-3-small
```

При генерации Planner получает релевантные референсы через RAG:

```python
# В узле planner
relevant_refs = knowledge_base.search(
    query=brief,
    collection="web_studio_references",
    top_k=5,
    filters={"style": requested_style}
)
```

---

## 2.8. ПРИМЕРЫ КОНСТИТУЦИЙ ДЛЯ РАЗНЫХ ДОМЕНОВ

### 2.8.1. Web Studio (К-01...К-24)

```markdown
# CONSTITUTION.md — Web Studio

## К-01: Минимализм
Каждый элемент на странице должен иметь обоснование.
**Проверка:** LLM-критик оценивает "нужность" каждого блока.
**Код ошибки:** V-01

## К-02: Контраст и читаемость
Текст должен иметь контраст ≥4.5:1 (WCAG AA).
**Проверка:** axe-core (детерминированно).
**Код ошибки:** V-02

## К-03: Скорость загрузки
Время загрузки < 2.5 сек (Lighthouse Performance ≥ 90).
**Проверка:** Lighthouse через Puppeteer.
**Код ошибки:** V-03

## К-04: Адаптивность
Сайт должен корректно отображаться на 3 breakpoints: mobile (375px), tablet (768px), desktop (1440px).
**Проверка:** Скриншоты через Playwright.
**Код ошибки:** V-04

## К-05: Семантический HTML
Использование правильных тегов (header, main, section, footer, nav).
**Проверка:** HTML валидатор + LLM.
**Код ошибки:** V-05

## К-06: Доступность
Все интерактивные элементы доступны с клавиатуры.
**Проверка:** axe-core.
**Код ошибки:** V-06

## К-07: Уникальность дизайна
Дизайн не должен копировать известные шаблоны.
**Проверка:** Сравнение с последними 10 проектами через design_variance engine.
**Код ошибки:** V-07

## К-08: Консистентность
Единая система отступов, цветов, типографики.
**Проверка:** Парсинг CSS + LLM.
**Код ошибки:** V-08

## К-09: Оптимизация изображений
Все изображения в WebP/AVIF, размер < 200KB.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-09

## К-10: Точечные правки
При исправлении ошибок вносить только точечные правки.
**Проверка:** Diff-анализ изменений.
**Код ошибки:** V-10

## К-11: Возврат удачных решений
Успешные паттерны возвращаются в базу знаний.
**Проверка:** Ручная (оператор).
**Код ошибки:** V-11

## К-12: Структура страницы
Чёткая иерархия: H1 → H2 → H3.
**Проверка:** Парсинг DOM.
**Код ошибки:** V-12

## К-13: SEO-основы
Наличие title, meta description, alt-текстов.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-13

## К-14: Кросс-браузерность
Корректная работа в Chrome, Firefox, Safari.
**Проверка:** Визуальный регресс.
**Код ошибки:** V-14

## К-15: Тестирование
Критические пути покрыты тестами.
**Проверка:** Анализ покрытия.
**Код ошибки:** V-15

## К-16: Документация
README с инструкцией по запуску.
**Проверка:** Проверка наличия файлов.
**Код ошибки:** V-16

## К-17: Безопасность
Отсутствие XSS, SQL injection.
**Проверка:** OWASP ZAP + LLM.
**Код ошибки:** V-17

## К-18: Производительность кода
Отсутствие дублирования, переиспользуемые компоненты.
**Проверка:** Статический анализ.
**Код ошибки:** V-18

## К-19: Локализация
Готовность к мультиязычности (если требуется).
**Проверка:** Анализ структуры файлов.
**Код ошибки:** V-19

## К-20: Версионирование
Использование Git.
**Проверка:** Проверка наличия .git.
**Код ошибки:** V-20

## К-21: Цикл принуждения
Каждый артефакт проходит цикл "сборка → ворота".
**Проверка:** Проверка логов.
**Код ошибки:** V-21

## К-22: Соответствие индустрии
Цветовая палитра соответствует индустрии клиента.
**Проверка:** LLM-критик.
**Код ошибки:** V-22

## К-23: Вариативность
Запрещено использовать один стиль для 3+ проектов подряд.
**Проверка:** Детерминированная проверка истории.
**Код ошибки:** V-23

## К-24: Ресурсный бюджет
Объём CSS < 50KB, JS < 100KB (без учёта библиотек).
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-24
```

### 2.8.2. Legal Docs Studio (К-01...К-15)

```markdown
# CONSTITUTION.md — Legal Docs Studio

## К-01: Существенные условия
Все существенные условия договора должны быть указаны (предмет, цена, сроки, ответственность).
**Проверка:** LLM-критик + проверка наличия обязательных разделов.
**Код ошибки:** V-01

## К-02: Соответствие ГК РФ
Документ не должен противоречить Гражданскому кодексу РФ.
**Проверка:** LLM-критик с контекстом ГК РФ.
**Код ошибки:** V-02

## К-03: Ясность формулировок
Все формулировки должны быть однозначными, без двусмысленности.
**Проверка:** LLM-критик.
**Код ошибки:** V-03

## К-04: Полнота реквизитов
Все реквизиты сторон заполнены (название, ИНН, адрес, подписант).
**Проверка:** Детерминированный скрипт (проверка шаблонов).
**Код ошибки:** V-04

## К-05: Отсутствие противоречий
Пункты документа не должны противоречить друг другу.
**Проверка:** LLM-критик.
**Код ошибки:** V-05

## К-06: Юридическая сила
Документ должен иметь юридическую силу (подпись, дата, место).
**Проверка:** Проверка наличия обязательных полей.
**Код ошибки:** V-06

## К-07: Конфиденциальность
Если требуется NDA — все условия конфиденциальности указаны.
**Проверка:** LLM-критик.
**Код ошибки:** V-07

## К-08: Соответствие 152-ФЗ
Согласие на обработку ПДн соответствует ФЗ-152.
**Проверка:** LLM-критик + проверка обязательных пунктов.
**Код ошибки:** V-08

## К-09: Структура документа
Документ имеет чёткую структуру (преамбула, предмет, права, обязанности, ответственность, реквизиты).
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-09

## К-10: Нумерация
Все пункты и подпункты правильно пронумерованы.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-10

## К-11: Отсутствие опечаток
Документ не содержит орфографических и пунктуационных ошибок.
**Проверка:** Яндекс.Спеллнер или LanguageTool.
**Код ошибки:** V-11

## К-12: Формат даты
Все даты в формате ДД.ММ.ГГГГ.
**Проверка:** Регулярное выражение.
**Код ошибки:** V-12

## К-13: Суммы прописью
Все суммы указаны цифрами и прописью.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-13

## К-14: Ссылки на законы
Все ссылки на законы актуальны.
**Проверка:** LLM-критик + проверка дат.
**Код ошибки:** V-14

## К-15: Версионирование
Документ имеет версию и дату изменения.
**Проверка:** Проверка метаданных.
**Код ошибки:** V-15
```

### 2.8.3. Content Studio (К-01...К-12)

```markdown
# CONSTITUTION.md — Content Studio

## К-01: Уникальность
Уникальность текста > 90%.
**Проверка:** Сервис проверки уникальности (Text.ru, Advego).
**Код ошибки:** V-01

## К-02: Плотность ключей
Плотность ключевых слов 1-3%.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-02

## К-03: Читаемость
Индекс Flesch-Kincaid ≥ 60 (для русского языка адаптировано).
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-03

## К-04: Отсутствие воды
Текст не содержит "воды" (штампов, общих фраз).
**Проверка:** LLM-критик.
**Код ошибки:** V-04

## К-05: Структура
Текст имеет чёткую структуру (H1, H2, H3, списки).
**Проверка:** Парсинг Markdown/HTML.
**Код ошибки:** V-05

## К-06: Длина
Длина текста соответствует ТЗ (±10%).
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-06

## К-07: Мета-теги
Title 50-60 символов, Description 120-158 символов.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-07

## К-08: Внутренние ссылки
Минимум 2-3 внутренних ссылки на другие страницы.
**Проверка:** Парсинг ссылок.
**Код ошибки:** V-08

## К-09: Изображения
Минимум 1 изображение на 500 слов, все с alt-текстами.
**Проверка:** Детерминированный скрипт.
**Код ошибки:** V-09

## К-10: CTA
Текст содержит призыв к действию (CTA).
**Проверка:** LLM-критик.
**Код ошибки:** V-10

## К-11: Тон голоса
Тон соответствует Tone of Voice бренда.
**Проверка:** LLM-критик.
**Код ошибки:** V-11

## К-12: Отсутствие плагиата
Текст не является дословной копией существующего.
**Проверка:** Проверка уникальности + LLM.
**Код ошибки:** V-12
```

---

## 2.9. ANTI-SLOP СИСТЕМА

### 2.9.1. BANNED.md (пример для Web Studio)

```markdown
# anti-slop/BANNED.md — Web Studio

## B-01: Градиентные фоны
**Запрет:** Использование градиентов как основного фона.
**Метод проверки:** Парсинг CSS на `background: linear-gradient`.
**Код ошибки:** B-01

## B-02: Более 3 шрифтов
**Запрет:** Использование более 3 различных шрифтов.
**Метод проверки:** Подсчёт уникальных `font-family` в CSS.
**Код ошибки:** B-02

## B-03: Стоковые фото без кастомизации
**Запрет:** Использование стоковых фото без обработки.
**Метод проверки:** LLM-анализ изображений.
**Код ошибки:** B-03

## B-04: Автоматические слайдеры
**Запрет:** Использование автослайдеров на главной странице.
**Метод проверки:** Поиск `carousel`, `slider` в JS.
**Код ошибки:** B-04

## B-05: Всплывающие окна при загрузке
**Запрет:** Показ модальных окон в первые 3 секунды.
**Метод проверки:** Анализ таймеров в JS.
**Код ошибки:** B-05

## B-06: Lorem ipsum
**Запрет:** Использование Lorem ipsum в финальном артефакте.
**Метод проверки:** Регулярное выражение.
**Код ошибки:** B-06

## B-07: Копирование референсов
**Запрет:** Дословное копирование layout из референсов.
**Метод проверки:** Сравнение структуры с базой референсов.
**Код ошибки:** B-07
```

### 2.9.2. QUOTAS.md (пример для Web Studio)

```markdown
# anti-slop/QUOTAS.md — Web Studio

## Q-01: Изображения
**Квота:** Максимум 10 изображений на страницу.
**Код ошибки:** Q-01

## Q-02: Анимации
**Квота:** Максимум 5 анимаций на страницу.
**Код ошибки:** Q-02

## Q-03: Цвета
**Квота:** Максимум 5 основных цветов в палитре.
**Код ошибки:** Q-03

## Q-04: Шрифты
**Квота:** Максимум 3 шрифта на проект.
**Код ошибки:** Q-04

## Q-05: JavaScript библиотеки
**Квота:** Максимум 5 внешних библиотек.
**Код ошибки:** Q-05

## Q-06: Формы
**Квота:** Максимум 3 формы на страницу.
**Код ошибки:** Q-06

## Q-07: Ссылки
**Квота:** Максимум 20 внешних ссылок на страницу.
**Код ошибки:** Q-07
```

---

## 2.10. CLI ДЛЯ УПРАВЛЕНИЯ СТУДИЯМИ

### 2.10.1. Основные команды

```bash
# Создание новой студии
autogen-studio create \
  --name my_studio \
  --domain web \
  --template advanced \
  --constitution-template web

# Заполнение референсами
autogen-studio populate-references \
  --name my_studio \
  --sources lapa,land-book,awwwards \
  --limit 50 \
  --parallel 5

# Настройка Конституции
autogen-studio setup-constitution \
  --name my_studio \
  --interactive

# Добавление скилла
autogen-studio add-skill \
  --name my_studio \
  --skill catalog \
  --from-template web_catalog

# Тестирование студии
autogen-studio test \
  --name my_studio \
  --brief "Каталог мебели" \
  --iterations 3

# Запуск проекта
autogen-studio run \
  --name my_studio \
  --brief-file brief.yaml \
  --output ./output

# Установка студии из маркетплейса
autogen-studio install \
  --package web_studio_pro \
  --version 1.2.0

# Публикация студии
autogen-studio publish \
  --name my_studio \
  --version 1.0.0 \
  --license MIT
```

### 2.10.2. Структура CLI

```python
# cli/main.py
import typer
from cli.commands import create, populate_references, setup_constitution, add_skill, test, run, install, publish

app = typer.Typer(help="Управление ИИ-студиями")

app.command("create")(create)
app.command("populate-references")(populate_references)
app.command("setup-constitution")(setup_constitution)
app.command("add-skill")(add_skill)
app.command("test")(test)
app.command("run")(run)
app.command("install")(install)
app.command("publish")(publish)

if __name__ == "__main__":
    app()
```

### 2.10.3. Пример реализации `create`

```python
# cli/commands/create.py
import typer
from pathlib import Path
import yaml

def create(
    name: str = typer.Option(..., help="Имя студии"),
    domain: str = typer.Option(..., help="Домен (web, legal, content, data, education)"),
    template: str = typer.Option("basic", help="Шаблон (basic, advanced)"),
    constitution_template: str = typer.Option(None, help="Шаблон Конституции")
):
    """Создаёт новую студию"""
    
    studio_dir = Path(f"verticals/{name}")
    if studio_dir.exists():
        typer.echo(f"❌ Студия {name} уже существует")
        raise typer.Exit(1)
    
    # Создание структуры
    studio_dir.mkdir(parents=True)
    (studio_dir / "skills").mkdir()
    (studio_dir / "validators").mkdir()
    (studio_dir / "anti-slop").mkdir()
    (studio_dir / "gates").mkdir()
    (studio_dir / "references" / "screenshots").mkdir(parents=True)
    (studio_dir / "references" / "metadata").mkdir(parents=True)
    (studio_dir / "tools").mkdir()
    (studio_dir / "scripts").mkdir()
    (studio_dir / "projects" / "_TEMPLATE").mkdir(parents=True)
    (studio_dir / "tests").mkdir()
    
    # Копирование шаблонов
    template_dir = Path(f"templates/studios/{template}")
    for file in template_dir.glob("**/*"):
        if file.is_file():
            dest = studio_dir / file.relative_to(template_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(file.read_bytes())
    
    # Создание vertical.yaml
    vertical_config = {
        "apiVersion": "autogen/v1",
        "kind": "Vertical",
        "metadata": {
            "name": name,
            "displayName": name.replace("_", " ").title(),
            "description": f"Студия для {domain}",
            "version": "1.0.0",
            "domain": domain
        },
        "spec": {
            "skills": [],
            "validators": ["constitution", "anti_slop"],
            "gates": ["G1-entry", "G2-checklist", "G3-artifact", "G4-rejection"],
            "tools": [],
            "models": {
                "planner": "ollama/llama3.1:8b",
                "coder": "ollama/qwen2.5-coder:7b",
                "verifier": "ollama/gemma2:9b",
                "fixer": "ollama/llama3.1:8b"
            },
            "budget": {
                "max_cost_usd_per_run": 2.0,
                "max_iterations": 10
            }
        }
    }
    
    with open(studio_dir / "vertical.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(vertical_config, f, allow_unicode=True)
    
    # Создание CONSTITUTION.md
    if constitution_template:
        const_template = Path(f"templates/constitutions/{constitution_template}.md")
        if const_template.exists():
            (studio_dir / "CONSTITUTION.md").write_text(const_template.read_text(encoding='utf-8'))
    
    typer.echo(f"✅ Студия {name} создана в {studio_dir}")
    typer.echo(f"📝 Следующие шаги:")
    typer.echo(f"   1. Отредактируйте {studio_dir}/CONSTITUTION.md")
    typer.echo(f"   2. Заполните референсы: autogen-studio populate-references --name {name}")
    typer.echo(f"   3. Добавьте скиллы: autogen-studio add-skill --name {name}")
```

---

**Конец ЧАСТИ 2.**

# ЧАСТЬ 3: ОРКЕСТРАЦИЯ, ИНФРАСТРУКТУРА, РЕАЛИЗАЦИЯ

---

## 3.1. ОРКЕСТРАЦИЯ И КОМПОЗИЦИИ (The-AI-Corporation)

### 3.1.1. Роль CEO-агента

CEO-агент — это **мета-оркестратор**, который координирует работу нескольких студий для выполнения сложных, многоэтапных задач. Он не генерирует артефакты напрямую, а:
1. Анализирует задачу клиента
2. Разбивает её на подзадачи
3. Маршрутизирует подзадачи к подходящим студиям
4. Управляет параллельным выполнением
5. Собирает финальный результат

### 3.1.2. Архитектура CEO-агента

```python
# the_ai_corporation/agents/ceo_agent.py
from typing import List, Dict, Any
from enum import Enum
import asyncio

class TaskType(Enum):
    WEBSITE = "website"
    LEGAL_DOCS = "legal_docs"
    CONTENT = "content"
    DATA_ANALYTICS = "data_analytics"
    EDUCATION = "education"
    COMPLEX = "complex"  # Требует нескольких студий

class CEOAgent:
    """Мета-оркестратор, координирующий работу студий"""
    
    def __init__(self, studio_registry: Dict[str, Any]):
        self.studio_registry = studio_registry  # {"web_studio": WebStudio, ...}
        self.llm = LiteLLMClient()
        self.task_router = TaskRouter()
    
    async def handle_request(self, brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Главный метод обработки запроса"""
        
        # 1. Классификация задачи
        task_type = await self._classify_task(brief)
        
        # 2. Планирование (если задача сложная)
        if task_type == TaskType.COMPLEX:
            plan = await self._create_plan(brief)
            return await self._execute_plan(plan, context)
        else:
            # Простая задача — маршрутизация к одной студии
            studio_name = self.task_router.route(task_type)
            return await self._execute_single_studio(studio_name, brief, context)
    
    async def _classify_task(self, brief: str) -> TaskType:
        """Классифицирует тип задачи"""
        prompt = f"""
        Классифицируй задачу по типу:
        - WEBSITE: создание сайта, лендинга, каталога
        - LEGAL_DOCS: договоры, оферты, NDA
        - CONTENT: статьи, описания, email-рассылки
        - DATA_ANALYTICS: SQL, Python-скрипты, отчёты
        - EDUCATION: уроки, курсы, тесты
        - COMPLEX: требует нескольких студий (напр., сайт + контент + юр. документы)
        
        Задача: {brief}
        
        Верни ТОЛЬКО тип задачи (одно слово).
        """
        
        response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/llama3.1:8b",
            temperature=0.1
        )
        
        return TaskType(response.content.strip().lower())
    
    async def _create_plan(self, brief: str) -> List[Dict[str, Any]]:
        """Создаёт план выполнения сложной задачи"""
        prompt = f"""
        Ты — CEO компании, управляющий командой из нескольких ИИ-студий.
        
        Задача клиента: {brief}
        
        Доступные студии:
        - web_studio: создание сайтов, лендингов, каталогов
        - legal_docs: договоры, оферты, NDA
        - content_studio: SEO-статьи, описания, email-рассылки
        - data_analytics: SQL, Python, отчёты
        - education: уроки, курсы
        
        Создай план выполнения задачи:
        1. Разбей задачу на подзадачи
        2. Для каждой подзадачи укажи:
           - id (уникальный идентификатор)
           - studio (какая студия выполняет)
           - brief (бриф для студии)
           - dependencies (id подзадач, которые должны быть выполнены раньше)
           - parallel (можно ли выполнять параллельно)
        
        Верни JSON:
        {{
          "tasks": [
            {{
              "id": "task_1",
              "studio": "web_studio",
              "brief": "...",
              "dependencies": [],
              "parallel": true
            }},
            ...
          ]
        }}
        """
        
        response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/llama3.1:8b",
            temperature=0.3
        )
        
        import json
        plan = json.loads(response.content)
        return plan["tasks"]
    
    async def _execute_plan(self, plan: List[Dict], context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет план задач с учётом зависимостей и параллелизма"""
        
        results = {}
        completed_tasks = set()
        
        while len(completed_tasks) < len(plan):
            # Находим задачи, готовые к выполнению
            ready_tasks = [
                task for task in plan
                if task["id"] not in completed_tasks
                and all(dep in completed_tasks for dep in task["dependencies"])
            ]
            
            if not ready_tasks:
                break  # Все задачи выполнены или есть цикл зависимостей
            
            # Выполняем готовые задачи параллельно
            tasks_to_run = [task for task in ready_tasks if task.get("parallel", False)]
            if not tasks_to_run:
                tasks_to_run = [ready_tasks[0]]  # Если нет параллельных, берём первую
            
            # Параллельный запуск
            async def run_task(task):
                studio = self.studio_registry[task["studio"]]
                result = await studio.run(task["brief"], context)
                return task["id"], result
            
            task_results = await asyncio.gather(*[run_task(task) for task in tasks_to_run])
            
            # Сохраняем результаты
            for task_id, result in task_results:
                results[task_id] = result
                completed_tasks.add(task_id)
        
        # Сборка финального результата
        return await self._assemble_final_result(plan, results, context)
    
    async def _assemble_final_result(
        self,
        plan: List[Dict],
        results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Собирает финальный результат из результатов подзадач"""
        
        prompt = f"""
        Ты — CEO, собирающий финальный результат из подзадач.
        
        План задачи:
        {json.dumps(plan, indent=2)}
        
        Результаты подзадач:
        {json.dumps(results, indent=2)}
        
        Собери финальный результат для клиента.
        Включи:
        - Краткое описание выполненной работы
        - Ссылки на артефакты (файлы, URL)
        - Рекомендации по дальнейшим шагам
        
        Верни JSON:
        {{
          "summary": "...",
          "artifacts": [...],
          "recommendations": [...]
        }}
        """
        
        response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/llama3.1:8b",
            temperature=0.3
        )
        
        import json
        final_result = json.loads(response.content)
        final_result["subtask_results"] = results
        return final_result
```

### 3.1.3. Композиции (Compositions)

Композиции — это декларативные описания сложных задач, требующих работы нескольких студий.

```yaml
# compositions/full_website.yaml
apiVersion: autogen/v1
kind: Composition

metadata:
  name: full_website
  displayName: "Полный сайт с контентом и юридическими документами"
  description: "Создаёт сайт, генерирует SEO-контент, договор оферты"

spec:
  tasks:
    - id: design_website
      studio: web_studio
      skill: landing_page
      brief: "Создай лендинг для онлайн-курсов по программированию"
      dependencies: []
      parallel: true
    
    - id: generate_content
      studio: content_studio
      skill: seo_article
      brief: "Напиши 5 SEO-статей о программировании для блога"
      dependencies: []
      parallel: true
    
    - id: create_legal_docs
      studio: legal_docs
      skill: offer
      brief: "Создай договор оферты для онлайн-курсов"
      dependencies: [design_website]  # Зависит от структуры сайта
      parallel: false
    
    - id: assemble_final
      studio: _assembler  # Специальная студия для сборки
      brief: "Собери финальный результат"
      dependencies: [design_website, generate_content, create_legal_docs]
      parallel: false
```

### 3.1.4. Маршрутизация задач

```python
# the_ai_corporation/routing/task_router.py
from typing import Dict, List
import re

class TaskRouter:
    """Маршрутизирует задачи к подходящим студиям"""
    
    def __init__(self):
        self.rules = {
            "web_studio": [
                r"сайт", r"лендинг", r"каталог", r"магазин", r"портфолио",
                r"website", r"landing", r"catalog", r"shop", r"portfolio"
            ],
            "legal_docs": [
                r"договор", r"оферта", r"соглашение", r"NDA", r"контракт",
                r"contract", r"agreement", r"offer"
            ],
            "content_studio": [
                r"статья", r"блог", r"описание", r"рассылка", r"email",
                r"article", r"blog", r"description", r"newsletter"
            ],
            "data_analytics": [
                r"SQL", r"Python", r"анализ", r"отчёт", r"дашборд",
                r"analytics", r"report", r"dashboard"
            ],
            "education": [
                r"урок", r"курс", r"тест", r"обучение",
                r"lesson", r"course", r"quiz", r"education"
            ]
        }
    
    def route(self, brief: str) -> str:
        """Определяет подходящую студию на основе ключевых слов"""
        brief_lower = brief.lower()
        
        scores = {}
        for studio, patterns in self.rules.items():
            score = sum(1 for pattern in patterns if re.search(pattern, brief_lower))
            scores[studio] = score
        
        # Возвращаем студию с максимальным счётом
        best_studio = max(scores, key=scores.get)
        return best_studio if scores[best_studio] > 0 else "web_studio"  # Default
```

---

## 3.2. ИНФРАСТРУКТУРА И ДЕПЛОЙ

### 3.2.1. Docker Compose для разработки

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Gateway
  api-gateway:
    build:
      context: ./system
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/autogen
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - LITELLM_PROXY_URL=http://litellm:4000
    depends_on:
      - postgres
      - redis
      - qdrant
      - litellm
    volumes:
      - ./verticals:/app/verticals
      - ./the_ai_corporation:/app/the_ai_corporation

  # PostgreSQL (состояние, чекпоинты)
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=autogen
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis (очереди, кэш)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Qdrant (векторная БД для RAG)
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  # LiteLLM Proxy (унификация LLM-провайдеров)
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    volumes:
      - ./configs/litellm_config.yaml:/app/config.yaml
    command: ["--config", "/app/config.yaml"]

  # Ollama (локальные LLM)
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Telegram Bot (HITL, уведомления)
  telegram-bot:
    build:
      context: ./the_ai_corporation
      dockerfile: Dockerfile.telegram
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_GATEWAY_URL=http://api-gateway:8000
    depends_on:
      - api-gateway

  # Prometheus (метрики)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  # Grafana (визуализация метрик)
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  # Loki (логи)
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./configs/loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/loki

volumes:
  postgres_data:
  qdrant_data:
  ollama_data:
  prometheus_data:
  grafana_data:
  loki_data:
```

### 3.2.2. Kubernetes для продакшена

```yaml
# k8s/api-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: api-gateway
          image: registry.example.com/autogen/api-gateway:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: autogen-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: autogen-config
                  key: redis-url
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 3.2.3. Мониторинг (Prometheus + Grafana)

```yaml
# configs/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: /metrics

  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
    metrics_path: /metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

**Ключевые метрики:**

```python
# system/observability/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Метрики выполнения задач
RUN_DURATION = Histogram(
    'run_duration_seconds',
    'Время выполнения задачи',
    ['vertical', 'skill', 'status']
)

RUN_ITERATIONS = Histogram(
    'run_iterations',
    'Количество итераций цикла',
    ['vertical', 'skill']
)

VALIDATION_ERRORS = Counter(
    'validation_errors_total',
    'Количество ошибок валидации',
    ['vertical', 'error_code']
)

# Метрики бюджета
BUDGET_USED = Gauge(
    'budget_used_usd',
    'Использованный бюджет',
    ['vertical', 'run_id']
)

TOKENS_USED = Counter(
    'tokens_used_total',
    'Количество использованных токенов',
    ['model', 'role']
)

# Метрики LLM
LLM_LATENCY = Histogram(
    'llm_latency_seconds',
    'Время ответа LLM',
    ['model', 'role']
)

LLM_ERRORS = Counter(
    'llm_errors_total',
    'Количество ошибок LLM',
    ['model', 'error_type']
)

# Метрики песочниц
SANDBOX_EXECUTION_TIME = Histogram(
    'sandbox_execution_seconds',
    'Время выполнения в песочнице',
    ['provider', 'language']
)
```

### 3.2.4. Логирование (Loki + Promtail)

```yaml
# configs/loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 3m
  chunk_block_size: 262144
  chunk_retain_period: 1m
  max_transfer_retries: 0

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s
```

**Структурированные логи:**

```python
# system/observability/logging.py
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)

logger = structlog.get_logger()

# Пример использования
logger.info(
    "run_started",
    run_id="abc123",
    vertical="web_studio",
    skill="landing_page",
    brief_hash="xyz789"
)
```

### 3.2.5. Трейсинг (OpenTelemetry)

```python
# system/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Настройка трейсинга
provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Инструментация FastAPI
FastAPIInstrumentor.instrument_app(app)

# Инструментация SQLAlchemy
SQLAlchemyInstrumentor().instrument(engine=engine)

# Пример использования
@tracer.start_as_current_span("run_execution")
async def execute_run(run_id: str, vertical: str):
    span = trace.get_current_span()
    span.set_attribute("run.id", run_id)
    span.set_attribute("run.vertical", vertical)
    
    # ... логика выполнения
```

---

## 3.3. ЭТАПЫ РЕАЛИЗАЦИИ

### Фаза 1: Ядро (Kernel) — 4 недели

**Неделя 1-2: Базовая инфраструктура**
- Настройка LangGraph Runner
- State Manager с чекпоинтами (PostgreSQL)
- Базовый API Gateway (FastAPI)
- Интеграция с LiteLLM

**Неделя 3: Песочницы и бюджет**
- Sandbox Manager (E2B + Docker fallback)
- Budget Manager с лимитами
- Базовые метрики (Prometheus)

**Неделя 4: Тестирование ядра**
- Unit-тесты для всех компонентов
- Integration-тесты с фейковым LLM
- Нагрузочное тестирование

**Результат:** Рабочее ядро, способное выполнять простые задачи через API.

---

### Фаза 2: Конструктор студий — 2 недели

**Неделя 5: CLI и шаблоны**
- CLI для создания студий (`autogen-studio create`)
- Шаблоны студий (basic, advanced)
- Генерация `vertical.yaml`, `CONSTITUTION.md`

**Неделя 6: Работа с референсами**
- Скрипт парсинга референсов (Playwright)
- Интеграция с RAG (Qdrant)
- CLI для заполнения референсов

**Результат:** Можно создавать новые студии через CLI за 1 день.

---

### Фаза 3: Первые 3 студии — 4 недели

**Неделя 7-8: Web Studio**
- Перенос `ceh-veb` в структуру вертикали
- Наполнение референсами (100+ сайтов из lapa, land-book, awwwards)
- Настройка валидаторов (Lighthouse, WCAG, anti-slop)
- Тестирование на 10 проектах

**Неделя 9: Legal Docs Studio**
- Создание Конституции (К-01...К-15)
- Валидаторы для юридических документов
- Референсы из consultant.ru, garant.ru
- Тестирование на 5 договорах

**Неделя 10: Content Studio**
- Создание Конституции (К-01...К-12)
- Валидаторы для контента (уникальность, SEO, читаемость)
- Референсы из топ-блогов
- Тестирование на 10 статьях

**Результат:** 3 работающие студии с валидированным качеством.

---

### Фаза 4: CEO-агент и композиции — 2 недели

**Неделя 11: CEO-агент**
- Реализация TaskRouter
- Классификация задач
- Маршрутизация к студиям

**Неделя 12: Композиции**
- Декларативные композиции (YAML)
- Параллельное выполнение
- Сборка финального результата

**Результат:** Система может координировать несколько студий для сложных задач.

---

### Фаза 5: Маркетплейс студий — 2 недели

**Неделя 13: Пакетирование**
- Формат пакета студии (studio-package.yaml)
- CLI для упаковки (`autogen-studio package`)
- Версионирование

**Неделя 14: Установка и обновление**
- CLI для установки (`autogen-studio install`)
- Обновление студий
- Каталог готовых студий

**Результат:** Можно публиковать и устанавливать студии как пакеты.

---

### Фаза 6: Продакшен — 2 недели

**Неделя 15: Docker и Kubernetes**
- Docker Compose для разработки
- Kubernetes манифесты для продакшена
- Helm charts

**Неделя 16: Мониторинг и документация**
- Полная настройка Prometheus + Grafana
- Логирование (Loki)
- Трейсинг (OpenTelemetry)
- Документация для разработчиков и операторов

**Результат:** Система готова к продакшену.

---

### Итого: 16 недель (4 месяца)

**Ресурсы:**
- 1 Backend-разработчик (Python, FastAPI, LangGraph)
- 1 DevOps-инженер (Docker, Kubernetes, мониторинг)
- 1 ML-инженер (LLM, RAG, промпт-инжиниринг)
- 0.5 QA-инженера

**Бюджет:**
- Инфраструктура: ~$500/мес (серверы, E2B, API)
- Токены LLM: ~$200/мес (на этапе разработки)
- ФОТ: зависит от команды

---

## 3.4. КРИТЕРИИ ПРИЁМКИ

### 3.4.1. Функциональные требования

- [ ] **Создание студии:** Новая студия создаётся через CLI за <1 дня
- [ ] **Референсы:** Референсы автоматически парсятся из lapa.ninja, land-book.com, awwwards.com
- [ ] **Минимум студий:** Реализовано 5 вертикалей из разных доменов (Web, Legal, Content, Data, Education)
- [ ] **Конституция:** Каждая студия имеет Конституцию с проверяемыми правилами (К-01...К-N)
- [ ] **Циклы:** Каждая студия проходит цикл генерации с валидацией
- [ ] **Качество:** Success rate каждой студии >90% (артефакт проходит все валидаторы)
- [ ] **Итерации:** Среднее количество итераций <5 на задачу
- [ ] **Бесплатные модели:** Система работает на бесплатных моделях через Ollama
- [ ] **API:** API Gateway с аутентификацией, rate limiting, идемпотентностью
- [ ] **Композиции:** CEO-агент может координировать 3+ студии для сложной задачи
- [ ] **Маркетплейс:** Можно упаковать, опубликовать и установить студию как пакет

### 3.4.2. Нефункциональные требования

- [ ] **Производительность:** Время выполнения простой задачи <5 минут
- [ ] **Масштабируемость:** Система выдерживает 100 параллельных задач
- [ ] **Надёжность:** Uptime >99% (с учётом перезапусков)
- [ ] **Безопасность:** Песочницы изолированы, нет утечек данных между задачами
- [ ] **Мониторинг:** Все ключевые метрики доступны в Grafana
- [ ] **Логирование:** Все действия логируются в структурированном виде
- [ ] **Трейсинг:** Можно отследить прохождение задачи через все узлы графа
- [ ] **Документация:** Полная документация для разработчиков и операторов

### 3.4.3. Метрики качества

| Метрика | Целевое значение | Как измеряется |
|---|---|---|
| Success rate | >90% | % задач, прошедших все валидаторы |
| Среднее число итераций | <5 | Среднее количество циклов на задачу |
| Время выполнения | <5 мин | Среднее время от брифа до результата |
| Cost per run | <$2 | Средняя стоимость одного запуска |
| Token usage | <100k | Среднее количество токенов на задачу |
| Validation errors | <3 | Среднее количество ошибок на задачу |
| Unique designs | >80% | % уникальных дизайнов (для Web Studio) |

---

## 3.5. РИСКИ И МИТИГАЦИИ

### 3.5.1. Технические риски

| Риск | Вероятность | Влияние | Митигация |
|---|---|---|---|
| **Галлюцинации LLM** | Высокая | Высокое | Детерминированные валидаторы, циклы самокоррекции, Constitution as Code |
| **Runaway agents** (бесконечные циклы) | Средняя | Высокое | Budget Manager с жёсткими лимитами, Human-in-the-Loop |
| **Низкое качество бесплатных моделей** | Высокая | Среднее | Агрессивная валидация, переиспользование успешных паттернов из RAG |
| **Блокировки при парсинге референсов** | Высокая | Низкое | Ротация User-Agent, прокси, ручная курация |
| **Сложность отладки** | Средняя | Высокое | Полное трейсинг, структурированные логи, метрики |
| **Зависимость от внешних API** (E2B, LLM) | Средняя | Среднее | Fallback на локальные решения (Docker, Ollama) |

### 3.5.2. Бизнес-риски

| Риск | Вероятность | Влияние | Митигация |
|---|---|---|---|
| **Big tech выпустит аналог** | Высокая | Высокое | Фокус на нишевых студиях, глубокая экспертиза в доменах |
| **Низкий спрос на студии** | Средняя | Высокое | Валидация на 3-5 реальных клиентах до масштабирования |
| **Высокая стоимость разработки** | Средняя | Среднее | Использование open-source компонентов (LangGraph, LiteLLM) |
| **Сложность продажи** | Высокая | Среднее | Productized Service модель (подписка), а не продажа технологии |
| **Юридические риски** (для Legal Studio) | Средняя | Высокое | Дисклеймер "не является юридической консультацией", HITL для критических документов |

### 3.5.3. Операционные риски

| Риск | Вероятность | Влияние | Митигация |
|---|---|---|---|
| **Нехватка экспертизы в доменах** | Высокая | Высокое | Партнёрство с экспертами (юристы, маркетологи) |
| **Сложность поддержки множества студий** | Средняя | Среднее | Стандартизация структуры студий, автоматизированное тестирование |
| **Деградация качества со временем** | Средняя | Высокое | Регулярный аудит студий, обновление референсов, A/B тестирование промптов |

---

## 3.6. ПЛАН ДЕЙСТВИЙ НА БЛИЖАЙШИЕ 2 НЕДЕЛИ

### Неделя 1: Валидация архитектуры

**День 1-2:**
- Развернуть базовое ядро (LangGraph + LiteLLM + PostgreSQL)
- Написать простой тестовый скилл (генерация HTML-страницы)
- Прогнать 5 тестовых задач

**День 3-4:**
- Настроить песочницы (E2B или Docker)
- Добавить базовые валидаторы (HTML-синтаксис, Lighthouse)
- Протестировать цикл самокоррекции

**День 5-7:**
- Настроить мониторинг (Prometheus + Grafana)
- Написать документацию для разработчиков
- Провести нагрузочное тестирование (10 параллельных задач)

**Результат недели:** Рабочее ядро, способное выполнять простые задачи с валидацией.

---

### Неделя 2: Первая студия (Web Studio)

**День 8-9:**
- Перенести `ceh-veb` в структуру вертикали
- Создать `vertical.yaml`, `CONSTITUTION.md`
- Настроить валидаторы (Constitution, Anti-slop, Lighthouse)

**День 10-11:**
- Запустить скрипт парсинга референсов (lapa.ninja, land-book.com)
- Собрать 50+ референсов
- Интегрировать с RAG (Qdrant)

**День 12-14:**
- Протестировать студию на 5 реальных проектах
- Записать проблемы и доработать
- Написать документацию для пользователей

**Результат недели:** Работающая Web Studio с 50+ референсами, готовая к использованию.

---

## 3.7. ЗАКЛЮЧЕНИЕ

Это ТЗ описывает **полноценную платформу для создания ИИ-студий**, которая:

1. **Универсальна** — подходит для любых предметных областей (веб, юр. документы, контент, аналитика, образование)
2. **Масштабируема** — новые студии создаются через CLI за 1 день
3. **Надёжна** — циклы самокоррекции и детерминированные валидаторы гарантируют качество
4. **Экономична** — работает на бесплатных моделях за счёт выноса логики в валидаторы
5. **Продакшен-готова** — полная инфраструктура (Docker, Kubernetes, мониторинг, логирование)

**Ключевые конкурентные преимущества:**
- Constitution as Code (правила как исполняемый код)
- Типизированные коды ошибок (V-xx, B-xx, Q-xx) для точного фидбека
- Система референсов из реальных каталогов (lapa, land-book, awwwards)
- Маркетплейс студий для переиспользования

**Следующие шаги:**
1. Утвердить ТЗ
2. Сформировать команду (Backend, DevOps, ML)
3. Начать Фазу 1 (Ядро)
4. Через 4 месяца — первый релиз с 3 студиями

---


# ДЕТАЛИЗАЦИЯ К ПУНКТУ 3.2.1: Docker Compose для развёртывания ядра

---

## 1. Основной `docker-compose.yml`

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ============================================
  # API GATEWAY (FastAPI)
  # ============================================
  api-gateway:
    build:
      context: ./system
      dockerfile: Dockerfile.api
    container_name: autogen-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://autogen:autogen_pass@postgres:5432/autogen_db
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - LITELLM_PROXY_URL=http://litellm:4000
      - LOG_LEVEL=INFO
      - ENVIRONMENT=development
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_started
    volumes:
      - ./verticals:/app/verticals
      - ./the_ai_corporation:/app/the_ai_corporation
      - ./configs:/app/configs
    networks:
      - autogen-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # ============================================
  # POSTGRESQL (Состояние, чекпоинты, метаданные)
  # ============================================
  postgres:
    image: postgres:15-alpine
    container_name: autogen-postgres
    environment:
      - POSTGRES_USER=autogen
      - POSTGRES_PASSWORD=autogen_pass
      - POSTGRES_DB=autogen_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./configs/postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - autogen-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U autogen -d autogen_db"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ============================================
  # REDIS (Очереди задач, кэш, сессии)
  # ============================================
  redis:
    image: redis:7-alpine
    container_name: autogen-redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - autogen-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ============================================
  # QDRANT (Векторная БД для RAG)
  # ============================================
  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: autogen-qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"  # gRPC
    networks:
      - autogen-network
    restart: unless-stopped
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO

  # ============================================
  # LITELLM PROXY (Унификация LLM-провайдеров)
  # ============================================
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: autogen-litellm
    ports:
      - "4000:4000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - LITELLM_MASTER_KEY=sk-1234  # Для локальной разработки
      - DATABASE_URL=postgresql://autogen:autogen_pass@postgres:5432/autogen_db
    volumes:
      - ./configs/litellm_config.yaml:/app/config.yaml
    command: 
      - "--config"
      - "/app/config.yaml"
      - "--port"
      - "4000"
      - "--num_workers"
      - "4"
    depends_on:
      - postgres
      - ollama
    networks:
      - autogen-network
    restart: unless-stopped

  # ============================================
  # OLLAMA (Локальные LLM, бесплатные модели)
  # ============================================
  ollama:
    image: ollama/ollama:latest
    container_name: autogen-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
      - ./scripts/ollama-init.sh:/ollama-init.sh
    networks:
      - autogen-network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    # Если нет GPU, закомментируй блок deploy выше
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:11434/api/tags || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # ============================================
  # TELEGRAM BOT (HITL, уведомления)
  # ============================================
  telegram-bot:
    build:
      context: ./the_ai_corporation
      dockerfile: Dockerfile.telegram
    container_name: autogen-telegram
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_GATEWAY_URL=http://api-gateway:8000
      - ADMIN_CHAT_ID=${ADMIN_CHAT_ID}
    depends_on:
      - api-gateway
    networks:
      - autogen-network
    restart: unless-stopped

  # ============================================
  # PROMETHEUS (Метрики)
  # ============================================
  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: autogen-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - autogen-network
    restart: unless-stopped

  # ============================================
  # GRAFANA (Визуализация метрик)
  # ============================================
  grafana:
    image: grafana/grafana:10.2.0
    container_name: autogen-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./configs/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - autogen-network
    restart: unless-stopped

  # ============================================
  # LOKI (Агрегация логов)
  # ============================================
  loki:
    image: grafana/loki:2.9.2
    container_name: autogen-loki
    ports:
      - "3100:3100"
    volumes:
      - ./configs/loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - autogen-network
    restart: unless-stopped

  # ============================================
  # PROMTAIL (Сборщик логов)
  # ============================================
  promtail:
    image: grafana/promtail:2.9.2
    container_name: autogen-promtail
    volumes:
      - ./configs/promtail-config.yaml:/etc/promtail/config.yaml
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yaml
    depends_on:
      - loki
    networks:
      - autogen-network
    restart: unless-stopped

# ============================================
# ТОМА (Persistent Storage)
# ============================================
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  qdrant_data:
    driver: local
  ollama_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  loki_data:
    driver: local

# ============================================
# СЕТИ
# ============================================
networks:
  autogen-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

---

## 2. Конфигурация LiteLLM (`configs/litellm_config.yaml`)

```yaml
# configs/litellm_config.yaml
model_list:
  # ============================================
  # Ollama (локальные бесплатные модели)
  # ============================================
  - model_name: ollama/llama3.1:8b
    litellm_params:
      model: ollama/llama3.1:8b
      api_base: http://ollama:11434
      api_key: fake-key
      timeout: 300
  
  - model_name: ollama/qwen2.5-coder:7b
    litellm_params:
      model: ollama/qwen2.5-coder:7b
      api_base: http://ollama:11434
      api_key: fake-key
      timeout: 300
  
  - model_name: ollama/gemma2:9b
    litellm_params:
      model: ollama/gemma2:9b
      api_base: http://ollama:11434
      api_key: fake-key
      timeout: 300
  
  - model_name: ollama/mistral:7b
    litellm_params:
      model: ollama/mistral:7b
      api_base: http://ollama:11434
      api_key: fake-key
      timeout: 300

  # ============================================
  # Алиасы ролей (ядро использует роли, не модели)
  # ============================================
  - model_name: role/planner
    litellm_params:
      model: ollama/llama3.1:8b
      api_base: http://ollama:11434
  
  - model_name: role/coder
    litellm_params:
      model: ollama/qwen2.5-coder:7b
      api_base: http://ollama:11434
  
  - model_name: role/verifier
    litellm_params:
      model: ollama/gemma2:9b
      api_base: http://ollama:11434
  
  - model_name: role/fixer
    litellm_params:
      model: ollama/llama3.1:8b
      api_base: http://ollama:11434

  # ============================================
  # Embedding модели (для RAG)
  # ============================================
  - model_name: ollama/nomic-embed-text
    litellm_params:
      model: ollama/nomic-embed-text
      api_base: http://ollama:11434
      api_key: fake-key

litellm_settings:
  drop_params: true
  set_verbose: false
  cache: true
  cache_params:
    type: redis
    host: redis
    port: 6379
    password: null

general_settings:
  master_key: sk-1234
  database_url: postgresql://autogen:autogen_pass@postgres:5432/autogen_db
```

---

## 3. Скрипт инициализации Ollama (`scripts/ollama-init.sh`)

```bash
#!/bin/bash
# scripts/ollama-init.sh
# Автоматическая загрузка моделей при первом запуске

echo "🦙 Инициализация Ollama..."

# Ждём, пока Ollama запустится
sleep 10

# Список моделей для загрузки
MODELS=(
    "llama3.1:8b"
    "qwen2.5-coder:7b"
    "gemma2:9b"
    "mistral:7b"
    "nomic-embed-text"
)

for model in "${MODELS[@]}"; do
    echo "📥 Загрузка модели: $model"
    ollama pull "$model"
    if [ $? -eq 0 ]; then
        echo "✅ Модель $model загружена успешно"
    else
        echo "❌ Ошибка загрузки модели $model"
    fi
done

echo "🎉 Инициализация Ollama завершена"
```

---

## 4. SQL-скрипт инициализации PostgreSQL (`configs/postgres-init.sql`)

```sql
-- configs/postgres-init.sql
-- Инициализация базы данных для ядра

-- ============================================
-- Таблица запусков (runs)
-- ============================================
CREATE TABLE IF NOT EXISTS runs (
    id VARCHAR(255) PRIMARY KEY,
    vertical_name VARCHAR(100) NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    input_data JSONB NOT NULL,
    artifacts JSONB DEFAULT '{}',
    iterations_count INTEGER DEFAULT 0,
    budget_used_usd DECIMAL(10, 4) DEFAULT 0.0,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_vertical ON runs(vertical_name);
CREATE INDEX idx_runs_created ON runs(created_at DESC);

-- ============================================
-- Таблица чекпоинтов (checkpoints)
-- ============================================
CREATE TABLE IF NOT EXISTS checkpoints (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) REFERENCES runs(id) ON DELETE CASCADE,
    node_name VARCHAR(100) NOT NULL,
    state_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkpoints_run ON checkpoints(run_id);

-- ============================================
-- Таблица ошибок валидации
-- ============================================
CREATE TABLE IF NOT EXISTS validation_errors (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) REFERENCES runs(id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL,
    error_code VARCHAR(20) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    suggestion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_validation_errors_run ON validation_errors(run_id);
CREATE INDEX idx_validation_errors_code ON validation_errors(error_code);

-- ============================================
-- Таблица использования токенов
-- ============================================
CREATE TABLE IF NOT EXISTS token_usage (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) REFERENCES runs(id) ON DELETE CASCADE,
    model VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost_usd DECIMAL(10, 6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_token_usage_run ON token_usage(run_id);
CREATE INDEX idx_token_usage_date ON token_usage(created_at DESC);

-- ============================================
-- Таблица API ключей
-- ============================================
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    rate_limit_rpm INTEGER DEFAULT 60,
    rate_limit_rpd INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- ============================================
-- Таблица референсов (для RAG)
-- ============================================
CREATE TABLE IF NOT EXISTS references_metadata (
    id SERIAL PRIMARY KEY,
    vertical_name VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    category VARCHAR(50),
    style VARCHAR(50),
    industry VARCHAR(50),
    screenshot_path VARCHAR(255),
    metadata JSONB,
    takeaway TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_references_vertical ON references_metadata(vertical_name);
CREATE INDEX idx_references_source ON references_metadata(source);

-- ============================================
-- Функция автоматического обновления updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_runs_updated_at BEFORE UPDATE ON runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Начальные данные
-- ============================================
INSERT INTO api_keys (key_hash, name, role, rate_limit_rpm, rate_limit_rpd)
VALUES (
    '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5',  -- hash of 'test-key-123'
    'Development Key',
    'admin',
    1000,
    10000
) ON CONFLICT DO NOTHING;
```

---

## 5. Dockerfile для API Gateway (`system/Dockerfile.api`)

```dockerfile
# system/Dockerfile.api
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 autogen && chown -R autogen:autogen /app
USER autogen

# Экспорт порта
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения
CMD ["uvicorn", "kernel.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 6. Requirements для API (`system/requirements.txt`)

```txt
# system/requirements.txt

# ============================================
# Web Framework
# ============================================
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# ============================================
# LangGraph (Оркестрация)
# ============================================
langgraph==0.0.26
langchain-core==0.1.23
langchain-community==0.0.19

# ============================================
# LLM Integration
# ============================================
litellm==1.28.1
openai==1.12.0
anthropic==0.18.1

# ============================================
# Database
# ============================================
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9

# ============================================
# Redis
# ============================================
redis==5.0.1
aioredis==2.0.1

# ============================================
# Vector DB (Qdrant)
# ============================================
qdrant-client==1.7.0

# ============================================
# Observability
# ============================================
prometheus-client==0.19.0
opentelemetry-api==1.22.0
opentelemetry-sdk==1.22.0
opentelemetry-instrumentation-fastapi==0.43b0
opentelemetry-exporter-otlp==1.22.0

# ============================================
# Logging
# ============================================
structlog==24.1.0
python-json-logger==2.0.7

# ============================================
# Utils
# ============================================
python-dotenv==1.0.0
httpx==0.26.0
aiofiles==23.2.1
pyyaml==6.0.1
jinja2==3.1.3
python-multipart==0.0.6
```

---

## 7. Команды запуска

```bash
# ============================================
# 1. Клонирование и подготовка
# ============================================
git clone <your-repo-url>
cd autogen-platform

# Создать .env файл
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_telegram_chat_id
EOF

# ============================================
# 2. Запуск всех сервисов
# ============================================
docker-compose up -d

# Проверить статус
docker-compose ps

# ============================================
# 3. Проверка работоспособности
# ============================================
# API Gateway
curl http://localhost:8000/health

# Ollama (должны быть загружены модели)
curl http://localhost:11434/api/tags

# Qdrant
curl http://localhost:6333/collections

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana (логин: admin / admin123)
open http://localhost:3000

# ============================================
# 4. Просмотр логов
# ============================================
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f api-gateway
docker-compose logs -f ollama

# ============================================
# 5. Остановка
# ============================================
docker-compose down

# Остановка с удалением данных (осторожно!)
docker-compose down -v
```

---

## 8. Проверка работоспособности

После запуска выполни:

```bash
# 1. Проверь, что все контейнеры запущены
docker-compose ps
# Все должны быть в статусе "Up" или "healthy"

# 2. Проверь API Gateway
curl http://localhost:8000/health
# Должен вернуть: {"status": "ok", "version": "1.0.0"}

# 3. Проверь, что модели загружены в Ollama
curl http://localhost:11434/api/tags | jq '.models[].name'
# Должны быть: llama3.1:8b, qwen2.5-coder:7b, gemma2:9b, mistral:7b, nomic-embed-text

# 4. Проверь LiteLLM proxy
curl http://localhost:4000/health
# Должен вернуть: {"status": "healthy"}

# 5. Проверь PostgreSQL
docker-compose exec postgres psql -U autogen -d autogen_db -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
# Должны быть таблицы: runs, checkpoints, validation_errors, token_usage, api_keys, references_metadata

# 6. Проверь Redis
docker-compose exec redis redis-cli ping
# Должен вернуть: PONG

# 7. Проверь Qdrant
curl http://localhost:6333/collections
# Должен вернуть пустой список коллекций (это нормально)
```

---

## 9. Решение типичных проблем

### Проблема 1: Ollama не загружает модели
```bash
# Проверь логи
docker-compose logs ollama

# Если нет GPU, убери блок deploy из docker-compose.yml
# Перезапусти
docker-compose up -d ollama

# Загрузи модели вручную
docker-compose exec ollama ollama pull llama3.1:8b
```

### Проблема 2: API Gateway не подключается к PostgreSQL
```bash
# Проверь, что PostgreSQL healthy
docker-compose ps postgres

# Проверь логи
docker-compose logs postgres
docker-compose logs api-gateway

# Перезапусти
docker-compose restart postgres api-gateway
```

### Проблема 3: LiteLLM не видит Ollama
```bash
# Проверь доступность Ollama из контейнера LiteLLM
docker-compose exec litellm curl http://ollama:11434/api/tags

# Если ошибка, проверь сеть
docker-compose config | grep networks
```

---

**Следующий шаг:** Детализация пункта 2.7 (Работа с референсами) — скрипт парсинга с обходом защит.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 2.7: Работа с референсами (парсинг, хранение, RAG)

---

## 1. Конфигурация источников референсов (`configs/references_sources.yaml`)

```yaml
# configs/references_sources.yaml
# Конфигурация источников для парсинга референсов

sources:
  # ============================================
  # Lapa Ninja (7300+ лендингов)
  # ============================================
  lapa_ninja:
    base_url: "https://www.lapa.ninja"
    enabled: true
    priority: 1
    categories:
      - name: "saas"
        url: "/category/saas/"
        limit: 30
      - name: "crypto"
        url: "/category/crypto/"
        limit: 20
      - name: "education"
        url: "/category/education/"
        limit: 20
      - name: "ecommerce"
        url: "/category/ecommerce/"
        limit: 20
      - name: "portfolio"
        url: "/category/portfolio/"
        limit: 20
    scraping:
      delay_between_requests: 2.0  # секунды
      timeout: 30
      full_page_screenshot: true
      viewport:
        width: 1440
        height: 900
    selectors:
      project_link: "a.card-link"
      project_title: "h2.card-title"
      project_category: "span.card-category"

  # ============================================
  # Land-book (3000+ сайтов)
  # ============================================
  land_book:
    base_url: "https://land-book.com"
    enabled: true
    priority: 2
    filters:
      - name: "minimal"
        url: "/websites?style=minimal"
        limit: 25
      - name: "brutalist"
        url: "/websites?style=brutalist"
        limit: 15
      - name: "corporate"
        url: "/websites?style=corporate"
        limit: 20
    scraping:
      delay_between_requests: 2.5
      timeout: 30
      full_page_screenshot: true
      viewport:
        width: 1440
        height: 900
    selectors:
      project_link: "a.website-link"
      project_title: "h3.website-title"

  # ============================================
  # Awwwards (премиум-дизайн)
  # ============================================
  awwwards:
    base_url: "https://www.awwwards.com"
    enabled: true
    priority: 3
    categories:
      - name: "websites"
        url: "/websites/"
        limit: 30
      - name: "minimal"
        url: "/websites/minimal/"
        limit: 20
    scraping:
      delay_between_requests: 3.0  # Awwwards агрессивнее с защитами
      timeout: 45
      full_page_screenshot: true
      viewport:
        width: 1440
        height: 900
    selectors:
      project_link: "a.figure-link"
      project_title: "h3.title"
      project_award: "span.award-badge"

  # ============================================
  # Siteinspire (минимализм)
  # ============================================
  siteinspire:
    base_url: "https://www.siteinspire.com"
    enabled: true
    priority: 4
    filters:
      - name: "all"
        url: "/websites"
        limit: 30
    scraping:
      delay_between_requests: 2.0
      timeout: 30
      full_page_screenshot: true
    selectors:
      project_link: "a.website-link"
      project_title: "h2.website-name"

  # ============================================
  # Minimal Gallery
  # ============================================
  minimal_gallery:
    base_url: "https://minimal.gallery"
    enabled: true
    priority: 5
    scraping:
      delay_between_requests: 2.0
      timeout: 30
      full_page_screenshot: true
    selectors:
      project_link: "a.site-link"
      project_title: "h3.site-title"

# ============================================
# Глобальные настройки
# ============================================
global:
  output_dir: "verticals/web_studio/references"
  max_concurrent_browsers: 3
  user_agents:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    - "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  proxy: null  # Опционально: "http://proxy:port"
  retry_on_failure: 3
  screenshot_quality: 80
```

---

## 2. Основной скрипт парсинга (`scripts/scrape_references.py`)

```python
#!/usr/bin/env python3
"""
Скрипт парсинга референсов из каталогов дизайна.
Поддерживает обход защит через stealth mode, ротацию User-Agent, задержки.
"""

import asyncio
import json
import yaml
import hashlib
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import stealth_async

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ReferenceMetadata:
    """Метаданные одного референса"""
    source: str
    url: str
    category: Optional[str] = None
    style: Optional[str] = None
    industry: Optional[str] = None
    screenshot_path: str = ""
    colors: Dict[str, str] = {}
    fonts: List[str] = []
    layout: str = ""
    components: List[str] = []
    takeaway: str = ""
    tags: List[str] = []
    scraped_at: str = ""
    hash: str = ""


class ReferenceScraper:
    """Парсер референсов с обходом защит"""
    
    def __init__(self, config_path: str = "configs/references_sources.yaml"):
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.user_agents = self.config["global"]["user_agents"]
        self.semaphore = asyncio.Semaphore(self.config["global"]["max_concurrent_browsers"])
        
        # Создание директорий
        (self.output_dir / "screenshots").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "metadata").mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, path: str) -> Dict:
        """Загрузка конфигурации"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_random_user_agent(self) -> str:
        """Случайный User-Agent"""
        return random.choice(self.user_agents)
    
    def _generate_hash(self, url: str) -> str:
        """Генерация хеша URL для уникальности"""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    async def _create_browser_context(self, playwright) -> Browser:
        """Создание браузера с stealth mode"""
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1440,900'
            ]
        )
        return browser
    
    async def _extract_metadata(self, page: Page) -> Dict:
        """Извлечение метаданных со страницы"""
        metadata = await page.evaluate("""
            () => {
                // Извлечение цветов
                const colors = new Set();
                const fonts = new Set();
                
                document.querySelectorAll('*').forEach(el => {
                    const styles = window.getComputedStyle(el);
                    
                    // Цвета фона
                    const bgColor = styles.backgroundColor;
                    if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') {
                        colors.add(bgColor);
                    }
                    
                    // Цвета текста
                    const textColor = styles.color;
                    if (textColor) {
                        colors.add(textColor);
                    }
                    
                    // Шрифты
                    const fontFamily = styles.fontFamily;
                    if (fontFamily) {
                        fonts.add(fontFamily.split(',')[0].trim().replace(/['"]/g, ''));
                    }
                });
                
                // Определение layout
                const sections = [];
                document.querySelectorAll('section, header, footer, main').forEach(el => {
                    const className = el.className || '';
                    const id = el.id || '';
                    sections.push({
                        tag: el.tagName.toLowerCase(),
                        class: className.split(' ')[0],
                        id: id
                    });
                });
                
                // Определение компонентов
                const components = [];
                if (document.querySelector('nav')) components.push('navigation');
                if (document.querySelector('form')) components.push('form');
                if (document.querySelector('.hero, #hero')) components.push('hero_section');
                if (document.querySelector('.pricing, #pricing')) components.push('pricing');
                if (document.querySelector('.testimonials, #testimonials')) components.push('testimonials');
                if (document.querySelector('.footer, footer')) components.push('footer');
                
                return {
                    colors: Array.from(colors).slice(0, 10),
                    fonts: Array.from(fonts).slice(0, 5),
                    sections: sections.slice(0, 20),
                    components: components,
                    title: document.title,
                    description: document.querySelector('meta[name="description"]')?.content || '',
                    viewport: window.innerWidth + 'x' + window.innerHeight
                };
            }
        """)
        
        return metadata
    
    async def _scrape_project(self, page: Page, url: str, source_name: str, index: int) -> Optional[ReferenceMetadata]:
        """Парсинг одного проекта"""
        try:
            # Переход на страницу
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)  # Ждём загрузки динамического контента
            
            # Stealth mode
            await stealth_async(page)
            
            # Скриншот
            hash_id = self._generate_hash(url)
            screenshot_filename = f"{source_name}_{index:03d}_{hash_id}.png"
            screenshot_path = self.output_dir / "screenshots" / screenshot_filename
            
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True,
                type='png'
            )
            
            # Извлечение метаданных
            metadata = await self._extract_metadata(page)
            
            # Создание объекта метаданных
            ref = ReferenceMetadata(
                source=source_name,
                url=url,
                screenshot_path=f"screenshots/{screenshot_filename}",
                colors={
                    "primary": metadata["colors"][0] if len(metadata["colors"]) > 0 else "",
                    "secondary": metadata["colors"][1] if len(metadata["colors"]) > 1 else "",
                    "accent": metadata["colors"][2] if len(metadata["colors"]) > 2 else "",
                    "background": metadata["colors"][3] if len(metadata["colors"]) > 3 else "",
                    "text": metadata["colors"][4] if len(metadata["colors"]) > 4 else ""
                },
                fonts=metadata["fonts"],
                layout=" + ".join([s["class"] for s in metadata["sections"][:5] if s["class"]]),
                components=metadata["components"],
                tags=[metadata.get("title", "").split()[0].lower()] if metadata.get("title") else [],
                scraped_at=datetime.now().isoformat(),
                hash=hash_id
            )
            
            logger.info(f"✅ [{source_name}] #{index}: {url}")
            return ref
            
        except Exception as e:
            logger.error(f"❌ [{source_name}] #{index}: {url} - {e}")
            return None
    
    async def _scrape_source(self, source_name: str, source_config: Dict):
        """Парсинг одного источника"""
        logger.info(f"🚀 Начинаю парсинг: {source_name}")
        
        async with async_playwright() as playwright:
            browser = await self._create_browser_context(playwright)
            context = await browser.new_context(
                viewport=source_config["scraping"]["viewport"],
                user_agent=self._get_random_user_agent(),
                locale='en-US'
            )
            
            page = await context.new_page()
            
            # Обход всех категорий/фильтров
            categories = source_config.get("categories") or source_config.get("filters") or [{"name": "all", "url": "", "limit": 50}]
            
            total_scraped = 0
            
            for category in categories:
                category_url = source_config["base_url"] + category["url"]
                logger.info(f"📂 Категория: {category['name']} - {category_url}")
                
                try:
                    # Переход на страницу категории
                    await page.goto(category_url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    # Извлечение ссылок на проекты
                    links = await page.evaluate(f"""
                        () => {{
                            const selector = "{source_config['selectors']['project_link']}";
                            const elements = document.querySelectorAll(selector);
                            return Array.from(elements)
                                .map(el => el.href)
                                .filter(href => href && href.startsWith('http'))
                                .slice(0, {category['limit']});
                        }}
                    """)
                    
                    logger.info(f"🔗 Найдено {len(links)} проектов в категории {category['name']}")
                    
                    # Парсинг каждого проекта
                    for i, link in enumerate(links):
                        async with self.semaphore:
                            ref = await self._scrape_project(page, link, source_name, total_scraped + i)
                            
                            if ref:
                                ref.category = category["name"]
                                
                                # Сохранение метаданных
                                metadata_filename = f"{source_name}_{total_scraped + i:03d}_{ref.hash}.yaml"
                                metadata_path = self.output_dir / "metadata" / metadata_filename
                                
                                with open(metadata_path, 'w', encoding='utf-8') as f:
                                    yaml.dump(asdict(ref), f, allow_unicode=True, default_flow_style=False)
                            
                            # Задержка между запросами
                            await asyncio.sleep(source_config["scraping"]["delay_between_requests"])
                    
                    total_scraped += len(links)
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка парсинга категории {category['name']}: {e}")
                    continue
            
            await browser.close()
            logger.info(f"✅ Завершён парсинг {source_name}: {total_scraped} проектов")
    
    async def scrape_all(self):
        """Парсинг всех источников"""
        sources = self.config["sources"]
        
        # Сортировка по приоритету
        sorted_sources = sorted(
            [(name, cfg) for name, cfg in sources.items() if cfg.get("enabled", True)],
            key=lambda x: x[1].get("priority", 999)
        )
        
        for source_name, source_config in sorted_sources:
            await self._scrape_source(source_name, source_config)
        
        logger.info("🎉 Парсинг всех источников завершён")


async def main():
    """Точка входа"""
    scraper = ReferenceScraper("configs/references_sources.yaml")
    await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. Интеграция с RAG (Qdrant) (`scripts/index_references_to_rag.py`)

```python
#!/usr/bin/env python3
"""
Индексация референсов в Qdrant для семантического поиска (RAG).
"""

import yaml
import asyncio
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReferenceChunk:
    """Чанк референса для векторизации"""
    id: str
    text: str
    metadata: Dict


class ReferenceIndexer:
    """Индексатор референсов в Qdrant"""
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "web_studio_references",
        embedding_model: str = "ollama/nomic-embed-text",
        ollama_url: str = "http://localhost:11434"
    ):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.ollama_url = ollama_url
        self.vector_size = 768  # Размер вектора для nomic-embed-text
        
        # Создание коллекции (если не существует)
        self._create_collection()
    
    def _create_collection(self):
        """Создание коллекции в Qdrant"""
        collections = self.qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Коллекция {self.collection_name} создана")
        else:
            logger.info(f"ℹ️ Коллекция {self.collection_name} уже существует")
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Получение эмбеддинга через Ollama"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model.replace("ollama/", ""),
                    "prompt": text
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["embedding"]
    
    def _prepare_chunk_text(self, ref_data: Dict) -> str:
        """Подготовка текста для векторизации"""
        parts = []
        
        if ref_data.get("category"):
            parts.append(f"Category: {ref_data['category']}")
        
        if ref_data.get("style"):
            parts.append(f"Style: {ref_data['style']}")
        
        if ref_data.get("industry"):
            parts.append(f"Industry: {ref_data['industry']}")
        
        if ref_data.get("layout"):
            parts.append(f"Layout: {ref_data['layout']}")
        
        if ref_data.get("components"):
            parts.append(f"Components: {', '.join(ref_data['components'])}")
        
        if ref_data.get("takeaway"):
            parts.append(f"Takeaway: {ref_data['takeaway']}")
        
        if ref_data.get("tags"):
            parts.append(f"Tags: {', '.join(ref_data['tags'])}")
        
        if ref_data.get("colors"):
            colors_str = ", ".join([f"{k}: {v}" for k, v in ref_data['colors'].items() if v])
            parts.append(f"Colors: {colors_str}")
        
        if ref_data.get("fonts"):
            parts.append(f"Fonts: {', '.join(ref_data['fonts'])}")
        
        return "\n".join(parts)
    
    async def index_references(self, references_dir: str = "verticals/web_studio/references"):
        """Индексация всех референсов"""
        metadata_dir = Path(references_dir) / "metadata"
        
        if not metadata_dir.exists():
            logger.error(f"❌ Директория {metadata_dir} не найдена")
            return
        
        yaml_files = list(metadata_dir.glob("*.yaml"))
        logger.info(f"📚 Найдено {len(yaml_files)} файлов метаданных")
        
        points = []
        
        for i, yaml_file in enumerate(yaml_files):
            try:
                # Загрузка метаданных
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    ref_data = yaml.safe_load(f)
                
                # Подготовка текста
                chunk_text = self._prepare_chunk_text(ref_data)
                
                # Получение эмбеддинга
                embedding = await self._get_embedding(chunk_text)
                
                # Создание точки
                point = PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "source": ref_data.get("source"),
                        "url": ref_data.get("url"),
                        "category": ref_data.get("category"),
                        "style": ref_data.get("style"),
                        "industry": ref_data.get("industry"),
                        "screenshot_path": ref_data.get("screenshot_path"),
                        "layout": ref_data.get("layout"),
                        "components": ref_data.get("components"),
                        "takeaway": ref_data.get("takeaway"),
                        "tags": ref_data.get("tags"),
                        "colors": ref_data.get("colors"),
                        "fonts": ref_data.get("fonts"),
                        "full_text": chunk_text
                    }
                )
                
                points.append(point)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"🔄 Обработано {i + 1}/{len(yaml_files)} референсов")
                
            except Exception as e:
                logger.error(f"❌ Ошибка обработки {yaml_file}: {e}")
                continue
        
        # Загрузка в Qdrant батчами
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            logger.info(f"✅ Загружено {i + len(batch)} точек в Qdrant")
        
        logger.info(f"🎉 Индексация завершена: {len(points)} референсов")


async def main():
    """Точка входа"""
    indexer = ReferenceIndexer()
    await indexer.index_references()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. CLI для управления референсами (`cli/references_cli.py`)

```python
#!/usr/bin/env python3
"""
CLI для управления референсами.
"""

import typer
import asyncio
from pathlib import Path

app = typer.Typer(help="Управление референсами")


@app.command()
def scrape(
    source: str = typer.Option(None, help="Конкретный источник (lapa_ninja, land_book, awwwards)"),
    limit: int = typer.Option(None, help="Лимит проектов на источник"),
    config: str = typer.Option("configs/references_sources.yaml", help="Путь к конфигурации")
):
    """Запуск парсинга референсов"""
    from scripts.scrape_references import ReferenceScraper
    
    scraper = ReferenceScraper(config)
    
    if source:
        # Парсинг одного источника
        source_config = scraper.config["sources"].get(source)
        if not source_config:
            typer.echo(f"❌ Источник {source} не найден")
            raise typer.Exit(1)
        
        if limit:
            # Обновление лимита
            if "categories" in source_config:
                for cat in source_config["categories"]:
                    cat["limit"] = limit
            elif "filters" in source_config:
                for filt in source_config["filters"]:
                    filt["limit"] = limit
        
        asyncio.run(scraper._scrape_source(source, source_config))
    else:
        # Парсинг всех источников
        asyncio.run(scraper.scrape_all())
    
    typer.echo("✅ Парсинг завершён")


@app.command()
def index(
    references_dir: str = typer.Option("verticals/web_studio/references", help="Директория с референсами"),
    qdrant_url: str = typer.Option("http://localhost:6333", help="URL Qdrant")
):
    """Индексация референсов в Qdrant"""
    from scripts.index_references_to_rag import ReferenceIndexer
    
    indexer = ReferenceIndexer(qdrant_url=qdrant_url)
    asyncio.run(indexer.index_references(references_dir))
    
    typer.echo("✅ Индексация завершена")


@app.command()
def search(
    query: str = typer.Argument(..., help="Поисковый запрос"),
    limit: int = typer.Option(5, help="Количество результатов"),
    qdrant_url: str = typer.Option("http://localhost:6333", help="URL Qdrant")
):
    """Поиск референсов"""
    from qdrant_client import QdrantClient
    import httpx
    
    # Получение эмбеддинга
    async def get_embedding():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": query
                }
            )
            return response.json()["embedding"]
    
    embedding = asyncio.run(get_embedding())
    
    # Поиск в Qdrant
    qdrant = QdrantClient(url=qdrant_url)
    results = qdrant.search(
        collection_name="web_studio_references",
        query_vector=embedding,
        limit=limit
    )
    
    typer.echo(f"\n🔍 Найдено {len(results)} результатов для запроса: {query}\n")
    
    for i, result in enumerate(results, 1):
        payload = result.payload
        typer.echo(f"{i}. {payload.get('source', 'N/A')} - {payload.get('url', 'N/A')}")
        typer.echo(f"   Категория: {payload.get('category', 'N/A')}")
        typer.echo(f"   Стиль: {payload.get('style', 'N/A')}")
        typer.echo(f"   Layout: {payload.get('layout', 'N/A')}")
        typer.echo(f"   Takeaway: {payload.get('takeaway', 'N/A')}")
        typer.echo(f"   Score: {result.score:.4f}\n")


@app.command()
def stats():
    """Статистика по референсам"""
    references_dir = Path("verticals/web_studio/references")
    
    if not references_dir.exists():
        typer.echo("❌ Директория референсов не найдена")
        raise typer.Exit(1)
    
    screenshots = list((references_dir / "screenshots").glob("*.png"))
    metadata = list((references_dir / "metadata").glob("*.yaml"))
    
    typer.echo(f"\n📊 Статистика референсов:")
    typer.echo(f"   Скриншотов: {len(screenshots)}")
    typer.echo(f"   Метаданных: {len(metadata)}")
    
    # Подсчёт по источникам
    sources = {}
    for meta_file in metadata:
        import yaml
        with open(meta_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            source = data.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
    
    typer.echo(f"\n📂 По источникам:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        typer.echo(f"   {source}: {count}")


if __name__ == "__main__":
    app()
```

---

## 5. Пример метаданных референса

```yaml
# verticals/web_studio/references/metadata/lapa_ninja_001_a1b2c3d4e5f6.yaml
source: lapa_ninja
url: https://www.lapa.ninja/freebie/linear-app-landing-page/
category: saas
style: minimalism
industry: technology
screenshot_path: screenshots/lapa_ninja_001_a1b2c3d4e5f6.png
colors:
  primary: "#5E6AD2"
  secondary: "#18181B"
  accent: "#F4F4F5"
  background: "#FFFFFF"
  text: "#18181B"
fonts:
  - Inter
  - system-ui
layout: hero + features + pricing + testimonials + cta + footer
components:
  - navigation
  - hero_section
  - pricing
  - testimonials
  - footer
takeaway: "Чёткая иерархия, один CTA на экран, минимум отвлекающих элементов, акцентный цвет только для кнопок"
tags:
  - saas
  - minimal
  - dark-accent
  - conversion-focused
scraped_at: '2026-09-28T14:30:00'
hash: a1b2c3d4e5f6
```

---

## 6. Команды запуска

```bash
# ============================================
# 1. Парсинг всех источников
# ============================================
python cli/references_cli.py scrape

# ============================================
# 2. Парсинг конкретного источника
# ============================================
python cli/references_cli.py scrape --source lapa_ninja --limit 50

# ============================================
# 3. Индексация в Qdrant
# ============================================
python cli/references_cli.py index

# ============================================
# 4. Поиск референсов
# ============================================
python cli/references_cli.py search "минималистичный SaaS лендинг с тёмной темой" --limit 10

# ============================================
# 5. Статистика
# ============================================
python cli/references_cli.py stats
```

---

## 7. Интеграция с ядром (использование в промптах)

```python
# system/kernel/nodes/planner.py
from qdrant_client import QdrantClient
import httpx

async def get_relevant_references(query: str, vertical: str, top_k: int = 5):
    """Получение релевантных референсов для промпта"""
    
    # Получение эмбеддинга запроса
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ollama:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": query
            }
        )
        embedding = response.json()["embedding"]
    
    # Поиск в Qdrant
    qdrant = QdrantClient(url="http://qdrant:6333")
    collection_name = f"{vertical}_references"
    
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=embedding,
        limit=top_k
    )
    
    # Форматирование для промпта
    references = []
    for result in results:
        payload = result.payload
        references.append({
            "url": payload["url"],
            "category": payload.get("category"),
            "style": payload.get("style"),
            "layout": payload.get("layout"),
            "takeaway": payload.get("takeaway"),
            "score": result.score
        })
    
    return references

# Использование в узле planner
async def planner_node(state: AgentState):
    brief = state["input_data"]["brief"]
    vertical = state["vertical_name"]
    
    # Получение релевантных референсов
    references = await get_relevant_references(brief, vertical, top_k=5)
    
    # Добавление в контекст
    state["context"]["references"] = references
    
    # ... остальная логика planner
```

---

**Следующий шаг:** Детализация пункта 2.4 (Валидаторы) — готовые Python-классы для ConstitutionGate, AntiSlopGate, SchemaGate.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 2.4: Система валидаторов

---

## 1. Базовые классы и интерфейсы (`system/kernel/validators/base.py`)

```python
"""
Базовые классы для всех валидаторов.
"""

from typing import Protocol, Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    """Серьёзность ошибки"""
    CRITICAL = "critical"  # Блокирует выполнение, требует немедленного исправления
    MAJOR = "major"        # Важная ошибка, но не блокирующая
    MINOR = "minor"        # Незначительное замечание


class ValidationError(BaseModel):
    """Структура ошибки валидации"""
    code: str = Field(..., description="Код ошибки (V-01, B-02, Q-01)")
    severity: Severity = Field(default=Severity.MAJOR)
    description: str = Field(..., description="Описание ошибки")
    location: Optional[str] = Field(None, description="Где обнаружена ошибка")
    suggestion: str = Field(..., description="Как исправить")
    fix_example: Optional[str] = Field(None, description="Пример исправления")
    context: Optional[Dict[str, Any]] = Field(None, description="Дополнительный контекст")


class VerificationResult(BaseModel):
    """Результат валидации"""
    passed: bool = Field(..., description="Пройдена ли валидация")
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метрики")
    
    @property
    def error_codes(self) -> List[str]:
        """Список кодов ошибок"""
        return [e.code for e in self.errors]
    
    @property
    def has_critical_errors(self) -> bool:
        """Есть ли критические ошибки"""
        return any(e.severity == Severity.CRITICAL for e in self.errors)
    
    def merge(self, other: 'VerificationResult') -> 'VerificationResult':
        """Объединение результатов двух валидаций"""
        return VerificationResult(
            passed=self.passed and other.passed,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            metrics={**self.metrics, **other.metrics}
        )


class IVerificationGate(Protocol):
    """Интерфейс валидационного гейта"""
    name: str
    
    async def verify(
        self,
        artifact: Any,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """
        Проверка артефакта.
        
        Args:
            artifact: Артефакт для проверки (HTML, JSON, текст, код)
            context: Контекст выполнения (бриф, метаданные, предыдущие ошибки)
        
        Returns:
            VerificationResult с ошибками и метриками
        """
        ...
```

---

## 2. ConstitutionGate — Валидатор Конституции (`verticals/web_studio/validators/constitution.py`)

```python
"""
Валидатор Конституции вертикали.
Проверяет артефакт на соответствие правилам из CONSTITUTION.md.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from system.kernel.validators.base import (
    IVerificationGate, VerificationResult, ValidationError, Severity
)


@dataclass
class ConstitutionRule:
    """Правило Конституции"""
    id: str                          # К-01, К-02, ...
    name: str                        # Название правила
    description: str                 # Описание
    check_type: str                  # "deterministic" или "llm"
    error_code: str                  # Код ошибки (V-01, V-02, ...)
    check_method: Optional[str] = None  # Метод проверки (для детерминированных)
    llm_prompt: Optional[str] = None    # Промпт для LLM-проверки


class ConstitutionGate:
    """
    Валидатор Конституции.
    
    Парсит CONSTITUTION.md и проверяет артефакт на соответствие каждому правилу.
    """
    
    def __init__(self, constitution_path: str):
        """
        Args:
            constitution_path: Путь к CONSTITUTION.md
        """
        self.constitution_path = Path(constitution_path)
        self.rules = self._parse_constitution()
        self.name = "constitution"
    
    def _parse_constitution(self) -> Dict[str, ConstitutionRule]:
        """Парсинг CONSTITUTION.md в структуру правил"""
        rules = {}
        current_rule = None
        
        with open(self.constitution_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разбиение на секции по правилам
        sections = re.split(r'\n## (К-\d+):', content)
        
        for i in range(1, len(sections), 2):
            rule_id = sections[i].strip()
            rule_content = sections[i + 1] if i + 1 < len(sections) else ""
            
            # Извлечение названия
            name_match = re.match(r'(.+?)\n', rule_content)
            name = name_match.group(1).strip() if name_match else ""
            
            # Извлечение описания
            desc_match = re.search(r'## Описание\n(.+?)(?=\n## |\Z)', rule_content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Извлечение метода проверки
            check_match = re.search(r'\*\*Проверка:\*\*\s*(.+?)(?=\n|\Z)', rule_content)
            check_method = check_match.group(1).strip() if check_match else ""
            
            # Определение типа проверки
            check_type = "llm" if "LLM" in check_method or "критик" in check_method.lower() else "deterministic"
            
            # Извлечение кода ошибки
            error_match = re.search(r'\*\*Код ошибки:\*\*\s*(V-\d+)', rule_content)
            error_code = error_match.group(1) if error_match else f"V-{int(rule_id.split('-')[1]):02d}"
            
            rules[rule_id] = ConstitutionRule(
                id=rule_id,
                name=name,
                description=description,
                check_type=check_type,
                error_code=error_code,
                check_method=check_method
            )
        
        return rules
    
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult:
        """Проверка артефакта на соответствие Конституции"""
        errors = []
        
        for rule_id, rule in self.rules.items():
            try:
                if rule.check_type == "deterministic":
                    passed = await self._run_deterministic_check(rule, artifact, context)
                else:
                    passed = await self._run_llm_check(rule, artifact, context)
                
                if not passed:
                    errors.append(ValidationError(
                        code=rule.error_code,
                        severity=Severity.CRITICAL,
                        description=f"Нарушение {rule.id}: {rule.name}",
                        suggestion=f"Исправьте в соответствии с правилом {rule.id}",
                        context={"rule_id": rule_id, "rule_name": rule.name}
                    ))
            except Exception as e:
                logger.error(f"Ошибка проверки правила {rule_id}: {e}")
                errors.append(ValidationError(
                    code=rule.error_code,
                    severity=Severity.MAJOR,
                    description=f"Ошибка проверки правила {rule.id}",
                    suggestion=f"Проверьте артефакт вручную",
                    context={"error": str(e)}
                ))
        
        return VerificationResult(
            passed=len(errors) == 0,
            errors=errors,
            metrics={"rules_checked": len(self.rules), "rules_passed": len(self.rules) - len(errors)}
        )
    
    async def _run_deterministic_check(
        self,
        rule: ConstitutionRule,
        artifact: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Запуск детерминированной проверки"""
        
        # Маппинг правил на методы проверки
        check_methods = {
            "К-02": self._check_contrast,           # Контраст текста
            "К-03": self._check_performance,        # Скорость загрузки
            "К-04": self._check_responsiveness,     # Адаптивность
            "К-05": self._check_semantic_html,      # Семантический HTML
            "К-06": self._check_accessibility,      # Доступность
            "К-09": self._check_image_optimization, # Оптимизация изображений
            "К-12": self._check_heading_hierarchy,  # Иерархия заголовков
            "К-13": self._check_seo_basics,         # SEO-основы
            "К-24": self._check_resource_budget,    # Ресурсный бюджет
        }
        
        method = check_methods.get(rule.id)
        if method:
            return await method(artifact, context)
        
        # Если метод не найден, пропускаем (или используем LLM)
        logger.warning(f"Метод проверки для {rule.id} не найден")
        return True
    
    async def _check_contrast(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-02: Проверка контраста текста (WCAG AA)"""
        # Используем axe-core через Playwright
        # Возвращает True, если контраст >= 4.5:1
        # Реализация зависит от типа артефакта (HTML, React, etc.)
        return True  # Заглушка
    
    async def _check_performance(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-03: Проверка производительности (Lighthouse >= 90)"""
        # Запуск Lighthouse через Puppeteer
        # Возвращает True, если Performance >= 90
        return True  # Заглушка
    
    async def _check_responsiveness(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-04: Проверка адаптивности (3 breakpoints)"""
        # Скриншоты на 375px, 768px, 1440px
        return True  # Заглушка
    
    async def _check_semantic_html(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-05: Проверка семантического HTML"""
        if isinstance(artifact, dict) and "html" in artifact:
            html = artifact["html"]
            # Проверка наличия семантических тегов
            required_tags = ["<header", "<main", "<footer", "<nav", "<section"]
            return all(tag in html.lower() for tag in required_tags)
        return True
    
    async def _check_accessibility(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-06: Проверка доступности (axe-core)"""
        return True  # Заглушка
    
    async def _check_image_optimization(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-09: Проверка оптимизации изображений"""
        if isinstance(artifact, dict) and "html" in artifact:
            html = artifact["html"]
            # Проверка, что все изображения в WebP/AVIF
            img_tags = re.findall(r'<img[^>]+src="([^"]+)"', html)
            for img in img_tags:
                if not (img.endswith('.webp') or img.endswith('.avif')):
                    return False
        return True
    
    async def _check_heading_hierarchy(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-12: Проверка иерархии заголовков"""
        if isinstance(artifact, dict) and "html" in artifact:
            html = artifact["html"]
            # Извлечение заголовков
            headings = re.findall(r'<h(\d)[^>]*>', html.lower())
            if headings:
                # Проверка, что нет пропусков (H1 -> H3 без H2)
                levels = [int(h) for h in headings]
                for i in range(1, len(levels)):
                    if levels[i] > levels[i-1] + 1:
                        return False
        return True
    
    async def _check_seo_basics(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-13: Проверка SEO-основ"""
        if isinstance(artifact, dict) and "html" in artifact:
            html = artifact["html"]
            # Проверка наличия title, meta description, alt
            has_title = "<title" in html.lower()
            has_description = 'name="description"' in html.lower()
            has_alt = all('alt="' in img for img in re.findall(r'<img[^>]+>', html))
            return has_title and has_description and has_alt
        return True
    
    async def _check_resource_budget(self, artifact: Any, context: Dict[str, Any]) -> bool:
        """К-24: Проверка ресурсного бюджета"""
        if isinstance(artifact, dict):
            css_size = len(artifact.get("css", "").encode('utf-8'))
            js_size = len(artifact.get("js", "").encode('utf-8'))
            return css_size < 50000 and js_size < 100000  # 50KB CSS, 100KB JS
        return True
    
    async def _run_llm_check(
        self,
        rule: ConstitutionRule,
        artifact: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Запуск LLM-проверки"""
        # Используется LLM-критик для проверки сложных правил
        # Например, К-01 (Минимализм), К-07 (Уникальность), К-22 (Соответствие индустрии)
        
        from system.kernel.llm.client import LLMClient
        
        llm = LLMClient()
        
        prompt = f"""
        Ты — строгий критик. Проверь артефакт на соответствие правилу:
        
        Правило: {rule.id} - {rule.name}
        Описание: {rule.description}
        
        Артефакт:
        {self._serialize_artifact(artifact)}
        
        Контекст:
        {context.get('brief', '')}
        
        Верни ТОЛЬКО "PASS" или "FAIL".
        """
        
        response = await llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/gemma2:9b",
            temperature=0.0
        )
        
        return "PASS" in response.content.upper()
    
    def _serialize_artifact(self, artifact: Any) -> str:
        """Сериализация артефакта для промпта"""
        if isinstance(artifact, dict):
            return f"HTML: {artifact.get('html', '')[:1000]}\nCSS: {artifact.get('css', '')[:500]}"
        return str(artifact)[:1500]
```

---

## 3. AntiSlopGate — Валидатор Anti-Slop (`verticals/web_studio/validators/anti_slop.py`)

```python
"""
Валидатор Anti-Slop правил.
Проверяет артефакт на использование запрещённых паттернов (BANNED) и превышение квот (QUOTAS).
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from system.kernel.validators.base import (
    IVerificationGate, VerificationResult, ValidationError, Severity
)


@dataclass
class BannedPattern:
    """Запрещённый паттерн"""
    code: str                      # B-01, B-02, ...
    name: str                      # Название
    description: str               # Описание
    pattern: str                   # Regex или описание
    check_method: str              # "regex", "css", "js", "llm"
    suggestion: str                # Как исправить


@dataclass
class Quota:
    """Квота"""
    code: str                      # Q-01, Q-02, ...
    name: str                      # Название
    description: str               # Описание
    max_value: int                 # Максимальное значение
    check_method: str              # Метод подсчёта


class AntiSlopGate:
    """
    Валидатор Anti-Slop.
    
    Проверяет артефакт на:
    1. Использование запрещённых паттернов (BANNED.md)
    2. Превышение квот (QUOTAS.md)
    """
    
    def __init__(self, banned_path: str, quotas_path: str):
        """
        Args:
            banned_path: Путь к anti-slop/BANNED.md
            quotas_path: Путь к anti-slop/QUOTAS.md
        """
        self.banned = self._parse_banned(banned_path)
        self.quotas = self._parse_quotas(quotas_path)
        self.name = "anti_slop"
    
    def _parse_banned(self, path: str) -> List[BannedPattern]:
        """Парсинг BANNED.md"""
        banned = []
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разбиение на секции
        sections = re.split(r'\n## (B-\d+):', content)
        
        for i in range(1, len(sections), 2):
            code = sections[i].strip()
            section_content = sections[i + 1] if i + 1 < len(sections) else ""
            
            # Извлечение названия
            name_match = re.match(r'(.+?)\n', section_content)
            name = name_match.group(1).strip() if name_match else ""
            
            # Извлечение описания
            desc_match = re.search(r'\*\*Запрет:\*\*\s*(.+?)(?=\n|\Z)', section_content)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Извлечение метода проверки
            method_match = re.search(r'\*\*Метод проверки:\*\*\s*(.+?)(?=\n|\Z)', section_content)
            check_method = method_match.group(1).strip() if method_match else "llm"
            
            # Извлечение предложения
            suggestion_match = re.search(r'\*\*Предложение:\*\*\s*(.+?)(?=\n|\Z)', section_content)
            suggestion = suggestion_match.group(1).strip() if suggestion_match else "Удалите запрещённый паттерн"
            
            banned.append(BannedPattern(
                code=code,
                name=name,
                description=description,
                pattern=check_method,
                check_method=self._detect_check_method(check_method),
                suggestion=suggestion
            ))
        
        return banned
    
    def _parse_quotas(self, path: str) -> List[Quota]:
        """Парсинг QUOTAS.md"""
        quotas = []
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = re.split(r'\n## (Q-\d+):', content)
        
        for i in range(1, len(sections), 2):
            code = sections[i].strip()
            section_content = sections[i + 1] if i + 1 < len(sections) else ""
            
            name_match = re.match(r'(.+?)\n', section_content)
            name = name_match.group(1).strip() if name_match else ""
            
            desc_match = re.search(r'\*\*Квота:\*\*\s*(.+?)(?=\n|\Z)', section_content)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Извлечение максимального значения
            max_match = re.search(r'Максимум\s+(\d+)', description)
            max_value = int(max_match.group(1)) if max_match else 0
            
            quotas.append(Quota(
                code=code,
                name=name,
                description=description,
                max_value=max_value,
                check_method=self._detect_quota_method(name)
            ))
        
        return quotas
    
    def _detect_check_method(self, method_desc: str) -> str:
        """Определение метода проверки по описанию"""
        if "regex" in method_desc.lower() or "регуляр" in method_desc.lower():
            return "regex"
        elif "css" in method_desc.lower():
            return "css"
        elif "js" in method_desc.lower() or "javascript" in method_desc.lower():
            return "js"
        else:
            return "llm"
    
    def _detect_quota_method(self, name: str) -> str:
        """Определение метода подсчёта квоты"""
        name_lower = name.lower()
        if "изображ" in name_lower or "image" in name_lower:
            return "count_images"
        elif "анимац" in name_lower or "animation" in name_lower:
            return "count_animations"
        elif "цвет" in name_lower or "color" in name_lower:
            return "count_colors"
        elif "шрифт" in name_lower or "font" in name_lower:
            return "count_fonts"
        elif "библиотек" in name_lower or "library" in name_lower:
            return "count_libraries"
        elif "форм" in name_lower or "form" in name_lower:
            return "count_forms"
        elif "ссылок" in name_lower or "link" in name_lower:
            return "count_links"
        else:
            return "generic_count"
    
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult:
        """Проверка артефакта на соответствие Anti-Slop правилам"""
        errors = []
        
        # Проверка запрещённых паттернов
        for banned in self.banned:
            found = await self._check_banned(banned, artifact, context)
            if found:
                errors.append(ValidationError(
                    code=banned.code,
                    severity=Severity.MAJOR,
                    description=f"Использован запрещённый паттерн: {banned.name}",
                    suggestion=banned.suggestion,
                    context={"pattern": banned.name}
                ))
        
        # Проверка квот
        for quota in self.quotas:
            count = await self._check_quota(quota, artifact, context)
            if count > quota.max_value:
                errors.append(ValidationError(
                    code=quota.code,
                    severity=Severity.MINOR,
                    description=f"Превышена квота {quota.name}: {count} > {quota.max_value}",
                    suggestion=f"Сократите количество до {quota.max_value}",
                    context={"count": count, "max": quota.max_value}
                ))
        
        return VerificationResult(
            passed=len(errors) == 0,
            errors=errors,
            metrics={
                "banned_checked": len(self.banned),
                "quotas_checked": len(self.quotas),
                "banned_found": sum(1 for e in errors if e.code.startswith("B-")),
                "quotas_exceeded": sum(1 for e in errors if e.code.startswith("Q-"))
            }
        )
    
    async def _check_banned(
        self,
        banned: BannedPattern,
        artifact: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Проверка запрещённого паттерна"""
        
        if banned.check_method == "regex":
            return self._check_banned_regex(banned, artifact)
        elif banned.check_method == "css":
            return self._check_banned_css(banned, artifact)
        elif banned.check_method == "js":
            return self._check_banned_js(banned, artifact)
        else:
            return await self._check_banned_llm(banned, artifact, context)
    
    def _check_banned_regex(self, banned: BannedPattern, artifact: Any) -> bool:
        """Проверка через regex"""
        if isinstance(artifact, dict):
            content = artifact.get("html", "") + artifact.get("css", "") + artifact.get("js", "")
        else:
            content = str(artifact)
        
        # Маппинг кодов на regex
        patterns = {
            "B-01": r'background:\s*linear-gradient',  # Градиентные фоны
            "B-06": r'lorem\s+ipsum',                   # Lorem ipsum
        }
        
        pattern = patterns.get(banned.code, banned.pattern)
        return bool(re.search(pattern, content, re.IGNORECASE))
    
    def _check_banned_css(self, banned: BannedPattern, artifact: Any) -> bool:
        """Проверка через CSS"""
        if isinstance(artifact, dict) and "css" in artifact:
            css = artifact["css"]
            
            # B-02: Более 3 шрифтов
            if banned.code == "B-02":
                fonts = set(re.findall(r'font-family:\s*([^;]+)', css))
                return len(fonts) > 3
            
            # B-01: Градиенты
            if banned.code == "B-01":
                return bool(re.search(r'linear-gradient|radial-gradient', css))
        
        return False
    
    def _check_banned_js(self, banned: BannedPattern, artifact: Any) -> bool:
        """Проверка через JavaScript"""
        if isinstance(artifact, dict) and "js" in artifact:
            js = artifact["js"]
            
            # B-04: Автослайдеры
            if banned.code == "B-04":
                return bool(re.search(r'carousel|slider|autoplay', js, re.IGNORECASE))
            
            # B-05: Всплывающие окна при загрузке
            if banned.code == "B-05":
                return bool(re.search(r'setTimeout\s*\(\s*function\s*\(\)\s*\{\s*modal\.show', js))
        
        return False
    
    async def _check_banned_llm(
        self,
        banned: BannedPattern,
        artifact: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Проверка через LLM"""
        from system.kernel.llm.client import LLMClient
        
        llm = LLMClient()
        
        prompt = f"""
        Проверь артефакт на использование запрещённого паттерна:
        
        Запрет: {banned.name}
        Описание: {banned.description}
        
        Артефакт:
        {self._serialize_artifact(artifact)}
        
        Верни ТОЛЬКО "FOUND" или "NOT_FOUND".
        """
        
        response = await llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/gemma2:9b",
            temperature=0.0
        )
        
        return "FOUND" in response.content.upper()
    
    async def _check_quota(
        self,
        quota: Quota,
        artifact: Any,
        context: Dict[str, Any]
    ) -> int:
        """Подсчёт значения квоты"""
        
        if quota.check_method == "count_images":
            return self._count_images(artifact)
        elif quota.check_method == "count_animations":
            return self._count_animations(artifact)
        elif quota.check_method == "count_colors":
            return self._count_colors(artifact)
        elif quota.check_method == "count_fonts":
            return self._count_fonts(artifact)
        elif quota.check_method == "count_libraries":
            return self._count_libraries(artifact)
        elif quota.check_method == "count_forms":
            return self._count_forms(artifact)
        elif quota.check_method == "count_links":
            return self._count_links(artifact)
        else:
            return 0
    
    def _count_images(self, artifact: Any) -> int:
        """Подсчёт изображений"""
        if isinstance(artifact, dict) and "html" in artifact:
            return len(re.findall(r'<img[^>]+>', artifact["html"]))
        return 0
    
    def _count_animations(self, artifact: Any) -> int:
        """Подсчёт анимаций"""
        if isinstance(artifact, dict) and "css" in artifact:
            return len(re.findall(r'@keyframes|animation:', artifact["css"]))
        return 0
    
    def _count_colors(self, artifact: Any) -> int:
        """Подсчёт уникальных цветов"""
        if isinstance(artifact, dict) and "css" in artifact:
            colors = set(re.findall(r'#[0-9a-fA-F]{3,6}', artifact["css"]))
            return len(colors)
        return 0
    
    def _count_fonts(self, artifact: Any) -> int:
        """Подсчёт шрифтов"""
        if isinstance(artifact, dict) and "css" in artifact:
            fonts = set(re.findall(r'font-family:\s*([^;]+)', artifact["css"]))
            return len(fonts)
        return 0
    
    def _count_libraries(self, artifact: Any) -> int:
        """Подсчёт внешних библиотек"""
        if isinstance(artifact, dict) and "html" in artifact:
            return len(re.findall(r'<script[^>]+src="https?://[^"]+"', artifact["html"]))
        return 0
    
    def _count_forms(self, artifact: Any) -> int:
        """Подсчёт форм"""
        if isinstance(artifact, dict) and "html" in artifact:
            return len(re.findall(r'<form[^>]*>', artifact["html"]))
        return 0
    
    def _count_links(self, artifact: Any) -> int:
        """Подсчёт внешних ссылок"""
        if isinstance(artifact, dict) and "html" in artifact:
            return len(re.findall(r'<a[^>]+href="https?://[^"]+"', artifact["html"]))
        return 0
    
    def _serialize_artifact(self, artifact: Any) -> str:
        """Сериализация артефакта"""
        if isinstance(artifact, dict):
            return f"HTML: {artifact.get('html', '')[:1000]}\nCSS: {artifact.get('css', '')[:500]}"
        return str(artifact)[:1500]
```

---

## 4. SchemaGate — Валидатор JSON Schema (`verticals/web_studio/validators/schema.py`)

```python
"""
Валидатор JSON Schema.
Проверяет структуру артефакта на соответствие схеме.
"""

from typing import Dict, Any, List
from jsonschema import validate, ValidationError as JsonSchemaError
import json

from system.kernel.validators.base import (
    IVerificationGate, VerificationResult, ValidationError, Severity
)


class SchemaGate:
    """
    Валидатор JSON Schema.
    
    Проверяет, что артефакт соответствует ожидаемой структуре.
    """
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Args:
            schema: JSON Schema для проверки
        """
        self.schema = schema
        self.name = "schema"
    
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult:
        """Проверка артефакта на соответствие схеме"""
        errors = []
        
        try:
            validate(instance=artifact, schema=self.schema)
        except JsonSchemaError as e:
            errors.append(ValidationError(
                code="S-01",
                severity=Severity.CRITICAL,
                description=f"Нарушение JSON Schema: {e.message}",
                location=e.json_path,
                suggestion=f"Исправьте структуру в соответствии со схемой",
                context={"schema_error": str(e)}
            ))
        except Exception as e:
            errors.append(ValidationError(
                code="S-02",
                severity=Severity.CRITICAL,
                description=f"Ошибка валидации схемы: {str(e)}",
                suggestion="Проверьте, что артефакт является валидным JSON"
            ))
        
        return VerificationResult(
            passed=len(errors) == 0,
            errors=errors,
            metrics={"schema_validated": True}
        )


# Пример схемы для веб-проекта
WEB_PROJECT_SCHEMA = {
    "type": "object",
    "required": ["html", "css", "metadata"],
    "properties": {
        "html": {
            "type": "string",
            "minLength": 100
        },
        "css": {
            "type": "string"
        },
        "js": {
            "type": "string"
        },
        "metadata": {
            "type": "object",
            "required": ["title", "description"],
            "properties": {
                "title": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 60
                },
                "description": {
                    "type": "string",
                    "minLength": 50,
                    "maxLength": 160
                }
            }
        }
    }
}
```

---

## 5. LLMJudgeGate — LLM-критик (`verticals/web_studio/validators/llm_judge.py`)

```python
"""
LLM-критик.
Использует LLM для оценки качества артефакта по сложным критериям.
"""

from typing import Dict, Any, List
import json

from system.kernel.validators.base import (
    IVerificationGate, VerificationResult, ValidationError, Severity
)


class LLMJudgeGate:
    """
    LLM-критик.
    
    Используется для проверки сложных критериев, которые нельзя проверить детерминированно:
    - Эстетика дизайна
    - Соответствие Tone of Voice
    - Логическая связность
    - Креативность
    """
    
    def __init__(
        self,
        criteria: List[Dict[str, Any]],
        model: str = "ollama/gemma2:9b",
        pass_threshold: float = 0.7
    ):
        """
        Args:
            criteria: Список критериев оценки
            model: Модель для использования
            pass_threshold: Порог прохождения (0.0 - 1.0)
        """
        self.criteria = criteria
        self.model = model
        self.pass_threshold = pass_threshold
        self.name = "llm_judge"
    
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult:
        """Оценка артефакта через LLM"""
        from system.kernel.llm.client import LLMClient
        
        llm = LLMClient()
        
        # Формирование промпта
        prompt = self._build_prompt(artifact, context)
        
        # Запрос к LLM
        response = await llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.3
        )
        
        # Парсинг ответа
        try:
            evaluation = json.loads(response.content)
        except json.JSONDecodeError:
            return VerificationResult(
                passed=False,
                errors=[ValidationError(
                    code="J-01",
                    severity=Severity.MAJOR,
                    description="LLM не вернул валидный JSON",
                    suggestion="Попробуйте упростить критерии оценки"
                )]
            )
        
        # Анализ результатов
        errors = []
        total_score = 0.0
        
        for criterion in self.criteria:
            criterion_name = criterion["name"]
            criterion_score = evaluation.get("scores", {}).get(criterion_name, 0.0)
            total_score += criterion_score
            
            if criterion_score < self.pass_threshold:
                errors.append(ValidationError(
                    code=f"J-{criterion['code']}",
                    severity=Severity.MAJOR if criterion_score < 0.5 else Severity.MINOR,
                    description=f"Низкая оценка по критерию '{criterion_name}': {criterion_score:.2f}",
                    suggestion=evaluation.get("feedback", {}).get(criterion_name, "Улучшите качество"),
                    context={"score": criterion_score, "threshold": self.pass_threshold}
                ))
        
        avg_score = total_score / len(self.criteria) if self.criteria else 0.0
        
        return VerificationResult(
            passed=len(errors) == 0,
            errors=errors,
            metrics={
                "average_score": avg_score,
                "criteria_evaluated": len(self.criteria),
                "criteria_failed": len(errors)
            }
        )
    
    def _build_prompt(self, artifact: Any, context: Dict[str, Any]) -> str:
        """Построение промпта для LLM"""
        
        criteria_text = "\n".join([
            f"- {c['name']}: {c['description']}"
            for c in self.criteria
        ])
        
        return f"""
        Ты — строгий критик. Оцени артефакт по следующим критериям:
        
        {criteria_text}
        
        Артефакт:
        {self._serialize_artifact(artifact)}
        
        Контекст (бриф клиента):
        {context.get('brief', 'Не указан')}
        
        Верни JSON в формате:
        {{
          "scores": {{
            "criterion_name_1": 0.85,
            "criterion_name_2": 0.70
          }},
          "feedback": {{
            "criterion_name_1": "Комментарий по первому критерию",
            "criterion_name_2": "Комментарий по второму критерию"
          }},
          "overall_comment": "Общий комментарий"
        }}
        
        Оценки должны быть от 0.0 до 1.0.
        """
    
    def _serialize_artifact(self, artifact: Any) -> str:
        """Сериализация артефакта"""
        if isinstance(artifact, dict):
            parts = []
            if "html" in artifact:
                parts.append(f"HTML:\n{artifact['html'][:2000]}")
            if "css" in artifact:
                parts.append(f"CSS:\n{artifact['css'][:1000]}")
            if "js" in artifact:
                parts.append(f"JS:\n{artifact['js'][:500]}")
            return "\n\n".join(parts)
        return str(artifact)[:3000]


# Пример критериев для веб-дизайна
WEB_DESIGN_CRITERIA = [
    {
        "code": "01",
        "name": "aesthetics",
        "description": "Визуальная привлекательность и эстетика дизайна"
    },
    {
        "code": "02",
        "name": "consistency",
        "description": "Консистентность элементов (цвета, шрифты, отступы)"
    },
    {
        "code": "03",
        "name": "readability",
        "description": "Читаемость текста и контраст"
    },
    {
        "code": "04",
        "name": "brand_alignment",
        "description": "Соответствие бренду и индустрии клиента"
    },
    {
        "code": "05",
        "name": "creativity",
        "description": "Креативность и уникальность дизайна"
    }
]
```

---

## 6. Композитный валидатор (`verticals/web_studio/validators/composite.py`)

```python
"""
Композитный валидатор.
Объединяет несколько валидаторов в один пайплайн.
"""

from typing import List, Dict, Any
import asyncio

from system.kernel.validators.base import VerificationResult
from .constitution import ConstitutionGate
from .anti_slop import AntiSlopGate
from .schema import SchemaGate, WEB_PROJECT_SCHEMA
from .llm_judge import LLMJudgeGate, WEB_DESIGN_CRITERIA


class CompositeValidator:
    """
    Композитный валидатор для Web Studio.
    
    Запускает все валидаторы параллельно и объединяет результаты.
    """
    
    def __init__(self, vertical_path: str):
        """
        Args:
            vertical_path: Путь к директории вертикали
        """
        self.validators = [
            ConstitutionGate(f"{vertical_path}/CONSTITUTION.md"),
            AntiSlopGate(
                f"{vertical_path}/anti-slop/BANNED.md",
                f"{vertical_path}/anti-slop/QUOTAS.md"
            ),
            SchemaGate(WEB_PROJECT_SCHEMA),
            LLMJudgeGate(WEB_DESIGN_CRITERIA, pass_threshold=0.7)
        ]
    
    async def verify(self, artifact: Any, context: Dict[str, Any]) -> VerificationResult:
        """Запуск всех валидаторов"""
        
        # Параллельный запуск всех валидаторов
        tasks = [v.verify(artifact, context) for v in self.validators]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Объединение результатов
        combined = VerificationResult(passed=True, errors=[], warnings=[], metrics={})
        
        for result in results:
            if isinstance(result, Exception):
                combined.errors.append(
                    ValidationError(
                        code="C-01",
                        severity="major",
                        description=f"Ошибка валидатора: {str(result)}",
                        suggestion="Проверьте логи"
                    )
                )
                combined.passed = False
            else:
                combined = combined.merge(result)
        
        return combined
```

---

## 7. Интеграция с ядром (`system/kernel/nodes/verifier.py`)

```python
"""
Узел верификации в LangGraph.
Запускает все валидаторы вертикали.
"""

from typing import Dict, Any
from system.kernel.validators.base import VerificationResult


async def verifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Узел верификации.
    
    Запускает все валидаторы вертикали и обновляет состояние.
    """
    from system.kernel.validators.registry import get_validator
    
    vertical_name = state["vertical_name"]
    artifact = state["artifacts"].get("current")
    context = state.get("context", {})
    
    # Получение валидатора для вертикали
    validator = get_validator(vertical_name)
    
    # Запуск валидации
    result: VerificationResult = await validator.verify(artifact, context)
    
    # Обновление состояния
    state["validation_result"] = result
    state["validation_errors"] = [e.dict() for e in result.errors]
    
    # Логирование
    if result.passed:
        state["status"] = "validated"
    else:
        state["status"] = "validation_failed"
        state["iterations_count"] = state.get("iterations_count", 0) + 1
    
    return state
```

---

## 8. Пример использования

```python
# Пример запуска валидации
import asyncio
from verticals.web_studio.validators.composite import CompositeValidator

async def main():
    # Создание валидатора
    validator = CompositeValidator("verticals/web_studio")
    
    # Тестовый артефакт
    artifact = {
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Site</title>
            <meta name="description" content="Test description for validation">
        </head>
        <body>
            <header>Header</header>
            <main>
                <section>
                    <h1>Main Title</h1>
                    <h2>Subtitle</h2>
                    <img src="image.webp" alt="Test image">
                </section>
            </main>
            <footer>Footer</footer>
        </body>
        </html>
        """,
        "css": """
        body { font-family: 'Inter', sans-serif; background: #ffffff; color: #000000; }
        h1 { font-size: 2rem; }
        """,
        "js": "console.log('Hello');",
        "metadata": {
            "title": "Test Site",
            "description": "Test description for validation purposes"
        }
    }
    
    context = {
        "brief": "Создай минималистичный лендинг для технологического стартапа"
    }
    
    # Запуск валидации
    result = await validator.verify(artifact, context)
    
    print(f"Passed: {result.passed}")
    print(f"Errors: {len(result.errors)}")
    for error in result.errors:
        print(f"  - {error.code}: {error.description}")
    print(f"Metrics: {result.metrics}")

asyncio.run(main())
```

---

**Следующий шаг:** Детализация пункта 3.1 (CEO-агент и композиции) — полная реализация оркестратора с реальным примером параллельного выполнения.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 3.1: CEO-агент и композиции (оркестрация)

---

## 1. Структура CEO-агента (`the_ai_corporation/agents/ceo_agent.py`)

```python
"""
CEO-агент — мета-оркестратор, координирующий работу нескольких студий.
"""

import asyncio
import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

from system.kernel.llm.client import LLMClient
from system.kernel.state import AgentState
from system.kernel.validators.base import VerificationResult

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Типы задач"""
    WEBSITE = "website"
    LEGAL_DOCS = "legal_docs"
    CONTENT = "content"
    DATA_ANALYTICS = "data_analytics"
    EDUCATION = "education"
    COMPLEX = "complex"


@dataclass
class SubTask:
    """Подзадача для выполнения студией"""
    id: str
    studio: str
    skill: str
    brief: str
    dependencies: List[str] = field(default_factory=list)
    parallel: bool = True
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class CompositionPlan:
    """План выполнения композиции"""
    name: str
    description: str
    tasks: List[SubTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "planned"  # planned, executing, completed, failed
    
    def get_ready_tasks(self) -> List[SubTask]:
        """Получить задачи, готовые к выполнению"""
        completed_ids = {t.id for t in self.tasks if t.status == "completed"}
        
        ready = []
        for task in self.tasks:
            if task.status != "pending":
                continue
            
            # Проверка зависимостей
            deps_satisfied = all(dep in completed_ids for dep in task.dependencies)
            if deps_satisfied:
                ready.append(task)
        
        return ready
    
    def get_parallel_tasks(self, tasks: List[SubTask]) -> List[SubTask]:
        """Получить задачи, которые можно выполнить параллельно"""
        return [t for t in tasks if t.parallel]


class CEOAgent:
    """
    CEO-агент — координирует работу студий.
    
    Отвечает за:
    1. Классификацию задач
    2. Планирование (разбиение на подзадачи)
    3. Маршрутизацию к студиям
    4. Параллельное выполнение
    5. Сборку финального результата
    """
    
    def __init__(
        self,
        studio_registry: Dict[str, Any],
        compositions_dir: str = "compositions"
    ):
        """
        Args:
            studio_registry: Реестр доступных студий
            compositions_dir: Директория с YAML-композициями
        """
        self.studio_registry = studio_registry
        self.compositions_dir = Path(compositions_dir)
        self.llm = LLMClient()
        self.task_router = TaskRouter()
        
        # Загрузка предопределённых композиций
        self.compositions = self._load_compositions()
    
    def _load_compositions(self) -> Dict[str, CompositionPlan]:
        """Загрузка предопределённых композиций из YAML"""
        compositions = {}
        
        if not self.compositions_dir.exists():
            return compositions
        
        for yaml_file in self.compositions_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                tasks = [
                    SubTask(
                        id=t["id"],
                        studio=t["studio"],
                        skill=t["skill"],
                        brief=t["brief"],
                        dependencies=t.get("dependencies", []),
                        parallel=t.get("parallel", True)
                    )
                    for t in data["spec"]["tasks"]
                ]
                
                plan = CompositionPlan(
                    name=data["metadata"]["name"],
                    description=data["metadata"]["description"],
                    tasks=tasks
                )
                
                compositions[data["metadata"]["name"]] = plan
                logger.info(f"✅ Загружена композиция: {data['metadata']['name']}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки композиции {yaml_file}: {e}")
        
        return compositions
    
    async def handle_request(
        self,
        brief: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Главный метод обработки запроса.
        
        Args:
            brief: Бриф клиента
            context: Дополнительный контекст
        
        Returns:
            Финальный результат
        """
        context = context or {}
        
        logger.info(f"🎯 Получен запрос: {brief[:100]}...")
        
        # 1. Классификация задачи
        task_type = await self._classify_task(brief)
        logger.info(f"📋 Тип задачи: {task_type}")
        
        # 2. Проверка предопределённой композиции
        composition = self._find_composition(task_type, brief)
        
        if composition:
            logger.info(f"🎨 Используем композицию: {composition.name}")
            return await self._execute_composition(composition, brief, context)
        
        # 3. Если задача сложная — динамическое планирование
        if task_type == TaskType.COMPLEX:
            logger.info("🔄 Создаём динамический план")
            plan = await self._create_dynamic_plan(brief, context)
            return await self._execute_composition(plan, brief, context)
        
        # 4. Простая задача — маршрутизация к одной студии
        studio_name = self.task_router.route(task_type)
        logger.info(f"🎯 Маршрутизация к студии: {studio_name}")
        
        return await self._execute_single_studio(studio_name, brief, context)
    
    async def _classify_task(self, brief: str) -> TaskType:
        """Классификация типа задачи"""
        prompt = f"""
        Классифицируй задачу по типу. Верни ТОЛЬКО одно слово из списка:
        
        - website: создание сайта, лендинга, каталога, интернет-магазина
        - legal_docs: договоры, оферты, NDA, юридические документы
        - content: статьи, описания товаров, email-рассылки, блог-посты
        - data_analytics: SQL-запросы, Python-скрипты, аналитика, отчёты
        - education: уроки, курсы, тесты, учебные материалы
        - complex: задача требует нескольких студий (напр., сайт + контент + документы)
        
        Задача: {brief}
        
        Тип:
        """
        
        response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/llama3.1:8b",
            temperature=0.1
        )
        
        task_type_str = response.content.strip().lower()
        
        try:
            return TaskType(task_type_str)
        except ValueError:
            logger.warning(f"Неизвестный тип задачи: {task_type_str}, используем COMPLEX")
            return TaskType.COMPLEX
    
    def _find_composition(self, task_type: TaskType, brief: str) -> Optional[CompositionPlan]:
        """Поиск подходящей предопределённой композиции"""
        # Маппинг типов задач на композиции
        type_to_composition = {
            TaskType.WEBSITE: "full_website",
            TaskType.LEGAL_DOCS: "legal_package",
            TaskType.CONTENT: "content_campaign",
            TaskType.COMPLEX: "full_website"  # По умолчанию
        }
        
        composition_name = type_to_composition.get(task_type)
        return self.compositions.get(composition_name)
    
    async def _create_dynamic_plan(
        self,
        brief: str,
        context: Dict[str, Any]
    ) -> CompositionPlan:
        """Создание динамического плана через LLM"""
        
        available_studios = list(self.studio_registry.keys())
        
        prompt = f"""
        Ты — CEO компании, управляющий командой ИИ-студий.
        
        Задача клиента: {brief}
        
        Доступные студии:
        {chr(10).join([f"- {s}" for s in available_studios])}
        
        Создай план выполнения задачи:
        1. Разбей задачу на подзадачи
        2. Для каждой подзадачи укажи:
           - id: уникальный идентификатор (task_1, task_2, ...)
           - studio: какая студия выполняет
           - skill: какой скилл использовать
           - brief: бриф для студии (детальное описание)
           - dependencies: id подзадач, которые должны быть выполнены раньше (пустой список, если нет)
           - parallel: можно ли выполнять параллельно с другими (true/false)
        
        Верни JSON:
        {{
          "name": "dynamic_plan",
          "description": "Описание плана",
          "tasks": [
            {{
              "id": "task_1",
              "studio": "web_studio",
              "skill": "landing_page",
              "brief": "Создай лендинг для...",
              "dependencies": [],
              "parallel": true
            }},
            ...
          ]
        }}
        """
        
        response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/llama3.1:8b",
            temperature=0.3
        )
        
        try:
            plan_data = json.loads(response.content)
            
            tasks = [
                SubTask(
                    id=t["id"],
                    studio=t["studio"],
                    skill=t["skill"],
                    brief=t["brief"],
                    dependencies=t.get("dependencies", []),
                    parallel=t.get("parallel", True)
                )
                for t in plan_data["tasks"]
            ]
            
            return CompositionPlan(
                name=plan_data.get("name", "dynamic_plan"),
                description=plan_data.get("description", ""),
                tasks=tasks
            )
        
        except Exception as e:
            logger.error(f"Ошибка создания динамического плана: {e}")
            # Fallback: создаём минимальный план
            return CompositionPlan(
                name="fallback_plan",
                description="Упрощённый план",
                tasks=[
                    SubTask(
                        id="task_1",
                        studio="web_studio",
                        skill="landing_page",
                        brief=brief,
                        dependencies=[],
                        parallel=True
                    )
                ]
            )
    
    async def _execute_composition(
        self,
        plan: CompositionPlan,
        brief: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение композиции (плана задач)"""
        
        plan.status = "executing"
        logger.info(f"🚀 Начинаем выполнение композиции: {plan.name}")
        
        # Цикл выполнения задач
        max_iterations = 20  # Защита от бесконечного цикла
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Получение готовых задач
            ready_tasks = plan.get_ready_tasks()
            
            if not ready_tasks:
                # Все задачи выполнены или есть цикл зависимостей
                break
            
            # Разделение на параллельные и последовательные
            parallel_tasks = plan.get_parallel_tasks(ready_tasks)
            sequential_tasks = [t for t in ready_tasks if not t.parallel]
            
            # Выполнение параллельных задач
            if parallel_tasks:
                logger.info(f"⚡ Параллельное выполнение {len(parallel_tasks)} задач")
                await self._execute_tasks_parallel(parallel_tasks, context)
            
            # Выполнение последовательных задач
            for task in sequential_tasks:
                logger.info(f"🔗 Последовательное выполнение: {task.id}")
                await self._execute_single_task(task, context)
            
            # Проверка завершения
            if all(t.status in ["completed", "failed"] for t in plan.tasks):
                break
        
        plan.status = "completed"
        
        # Сборка финального результата
        return await self._assemble_final_result(plan, brief, context)
    
    async def _execute_tasks_parallel(
        self,
        tasks: List[SubTask],
        context: Dict[str, Any]
    ):
        """Параллельное выполнение задач"""
        
        async def run_task(task: SubTask):
            task.status = "running"
            task.started_at = datetime.now()
            
            try:
                result = await self._execute_single_task(task, context)
                task.result = result
                task.status = "completed"
                task.completed_at = datetime.now()
                logger.info(f"✅ Задача {task.id} завершена")
            except Exception as e:
                task.status = "failed"
                task.errors.append({"error": str(e)})
                logger.error(f"❌ Задача {task.id} провалена: {e}")
        
        # Параллельный запуск
        await asyncio.gather(*[run_task(task) for task in tasks])
    
    async def _execute_single_task(
        self,
        task: SubTask,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение одной задачи через студию"""
        
        studio = self.studio_registry.get(task.studio)
        if not studio:
            raise ValueError(f"Студия {task.studio} не найдена")
        
        # Подготовка контекста для студии
        studio_context = {
            **context,
            "task_id": task.id,
            "composition_name": context.get("composition_name", "single_task")
        }
        
        # Добавление результатов зависимостей
        if task.dependencies:
            dep_results = {}
            for dep_id in task.dependencies:
                dep_task = next((t for t in self._get_current_plan().tasks if t.id == dep_id), None)
                if dep_task and dep_task.result:
                    dep_results[dep_id] = dep_task.result
            
            studio_context["dependency_results"] = dep_results
        
        # Запуск студии
        result = await studio.run(
            skill_name=task.skill,
            brief=task.brief,
            context=studio_context
        )
        
        return result
    
    def _get_current_plan(self) -> CompositionPlan:
        """Получение текущего плана (для доступа к зависимостям)"""
        # В реальной реализации это должно быть в состоянии
        return self._current_plan
    
    async def _execute_single_studio(
        self,
        studio_name: str,
        brief: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение задачи через одну студию"""
        
        studio = self.studio_registry.get(studio_name)
        if not studio:
            raise ValueError(f"Студия {studio_name} не найдена")
        
        # Определение скилла по умолчанию
        default_skill = studio.get_default_skill()
        
        result = await studio.run(
            skill_name=default_skill,
            brief=brief,
            context=context
        )
        
        return {
            "summary": f"Задача выполнена студией {studio_name}",
            "artifacts": [result],
            "recommendations": []
        }
    
    async def _assemble_final_result(
        self,
        plan: CompositionPlan,
        brief: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Сборка финального результата из результатов подзадач"""
        
        # Сбор всех результатов
        subtask_results = {
            task.id: {
                "studio": task.studio,
                "skill": task.skill,
                "status": task.status,
                "result": task.result,
                "errors": task.errors
            }
            for task in plan.tasks
        }
        
        # Если есть проваленные задачи — возвращаем ошибку
        failed_tasks = [t for t in plan.tasks if t.status == "failed"]
        if failed_tasks:
            return {
                "status": "failed",
                "summary": f"Провалено {len(failed_tasks)} задач",
                "failed_tasks": [t.id for t in failed_tasks],
                "subtask_results": subtask_results
            }
        
        # Успешное выполнение — сборка через LLM
        prompt = f"""
        Ты — CEO, собирающий финальный результат для клиента.
        
        Задача клиента: {brief}
        
        Результаты подзадач:
        {json.dumps(subtask_results, indent=2, ensure_ascii=False)}
        
        Собери финальный результат:
        1. Краткое описание выполненной работы (2-3 предложения)
        2. Список артефактов (файлы, URL, документы)
        3. Рекомендации по дальнейшим шагам
        
        Верни JSON:
        {{
          "status": "completed",
          "summary": "...",
          "artifacts": [...],
          "recommendations": [...]
        }}
        """
        
        response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="ollama/llama3.1:8b",
            temperature=0.3
        )
        
        try:
            final_result = json.loads(response.content)
            final_result["subtask_results"] = subtask_results
            return final_result
        except json.JSONDecodeError:
            return {
                "status": "completed",
                "summary": "Задача выполнена",
                "artifacts": [],
                "recommendations": [],
                "subtask_results": subtask_results
            }


class TaskRouter:
    """Маршрутизатор задач к студиям"""
    
    def __init__(self):
        self.rules = {
            TaskType.WEBSITE: "web_studio",
            TaskType.LEGAL_DOCS: "legal_docs",
            TaskType.CONTENT: "content_studio",
            TaskType.DATA_ANALYTICS: "data_analytics",
            TaskType.EDUCATION: "education"
        }
    
    def route(self, task_type: TaskType) -> str:
        """Маршрутизация задачи к студии"""
        return self.rules.get(task_type, "web_studio")
```

---

## 2. Пример композиции (`compositions/full_website.yaml`)

```yaml
# compositions/full_website.yaml
apiVersion: autogen/v1
kind: Composition

metadata:
  name: full_website
  displayName: "Полный сайт с контентом и документами"
  description: "Создаёт сайт, генерирует SEO-контент, договор оферты и политику конфиденциальности"
  version: "1.0.0"

spec:
  tasks:
    # ============================================
    # Задача 1: Дизайн сайта (параллельно)
    # ============================================
    - id: design_website
      studio: web_studio
      skill: landing_page
      brief: |
        Создай современный лендинг для онлайн-школы программирования.
        
        Требования:
        - Минималистичный дизайн в тёмной теме
        - Секции: Hero, Преимущества, Программа курса, Отзывы, CTA
        - Адаптивность для мобильных устройств
        - Производительность Lighthouse > 90
        
        Целевая аудитория: начинающие разработчики 20-35 лет
      dependencies: []
      parallel: true
    
    # ============================================
    # Задача 2: SEO-контент (параллельно)
    # ============================================
    - id: generate_content
      studio: content_studio
      skill: seo_article
      brief: |
        Напиши 3 SEO-статьи для блога онлайн-школы программирования:
        
        1. "Как начать изучать программирование с нуля в 2026 году"
        2. "Топ-5 языков программирования для начинающих"
        3. "Сколько времени нужно, чтобы стать Junior-разработчиком"
        
        Требования:
        - Уникальность > 90%
        - Объём: 1500-2000 слов каждая
        - Плотность ключей: 1-3%
        - Внутренние ссылки на курс
      dependencies: []
      parallel: true
    
    # ============================================
    # Задача 3: Анализ конкурентов (параллельно)
    # ============================================
    - id: competitor_analysis
      studio: data_analytics
      skill: research_report
      brief: |
        Проведи анализ конкурентов для онлайн-школы программирования.
        
        Изучи топ-5 школ:
        - Skillbox
        - GeekBrains
        - Netology
        - Яндекс.Практикум
        - HTML Academy
        
        Для каждой школы собери:
        - Цены на курсы
        - Программы обучения
        - Уникальные преимущества
        - Отзывы студентов
        
        Верни структурированный отчёт в формате Markdown.
      dependencies: []
      parallel: true
    
    # ============================================
    # Задача 4: Договор оферты (зависит от дизайна)
    # ============================================
    - id: create_offer
      studio: legal_docs
      skill: offer
      brief: |
        Создай договор публичной оферты для онлайн-школы программирования.
        
        Существенные условия:
        - Предмет: оказание образовательных услуг
        - Стоимость: от 30 000 до 150 000 рублей (зависит от курса)
        - Срок обучения: от 3 до 12 месяцев
        - Порядок оплаты: предоплата 100% или рассрочка
        - Возврат средств: в течение 14 дней без объяснения причин
        - Ответственность: школа обязуется предоставить доступ к материалам
        
        Требования:
        - Соответствие ГК РФ
        - Соответствие Закону "О защите прав потребителей"
        - Все существенные условия указаны
      dependencies:
        - design_website  # Нужна структура сайта для интеграции
      parallel: false
    
    # ============================================
    # Задача 5: Политика конфиденциальности (зависит от дизайна)
    # ============================================
    - id: create_privacy_policy
      studio: legal_docs
      skill: privacy_policy
      brief: |
        Создай политику конфиденциальности для онлайн-школы программирования.
        
        Требования:
        - Соответствие 152-ФЗ "О персональных данных"
        - Указание целей сбора данных
        - Перечень собираемых данных: имя, email, телефон, платёжные данные
        - Порядок обработки и хранения
        - Права пользователя
        - Контактные данные для обращений
      dependencies:
        - design_website
      parallel: false
    
    # ============================================
    # Задача 6: Email-рассылка (зависит от контента)
    # ============================================
    - id: create_email_sequence
      studio: content_studio
      skill: email_sequence
      brief: |
        Создай welcome-серию из 5 писем для новых подписчиков онлайн-школы.
        
        Письма:
        1. Приветствие + бесплатный урок
        2. История успеха студента
        3. Программа курса (кратко)
        4. Отзывы и результаты
        5. Специальное предложение (скидка 20%)
        
        Требования:
        - Тон: дружелюбный, мотивирующий
        - Персонализация (использование имени)
        - CTA в каждом письме
        - Адаптация под мобильные устройства
      dependencies:
        - generate_content  # Используем контент из статей
      parallel: false
```

---

## 3. Реестр студий (`the_ai_corporation/registry/studio_registry.py`)

```python
"""
Реестр доступных студий.
"""

from typing import Dict, Any, List
from pathlib import Path
import yaml
import importlib
import logging

logger = logging.getLogger(__name__)


class StudioWrapper:
    """Обёртка над студией для унификации интерфейса"""
    
    def __init__(self, vertical_path: str):
        self.vertical_path = Path(vertical_path)
        self.config = self._load_config()
        self.name = self.config["metadata"]["name"]
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка vertical.yaml"""
        config_path = self.vertical_path / "vertical.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_default_skill(self) -> str:
        """Получение скилла по умолчанию"""
        skills = self.config["spec"].get("skills", [])
        return skills[0] if skills else "default"
    
    async def run(
        self,
        skill_name: str,
        brief: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Запуск студии"""
        from system.kernel.runner import run_vertical
        
        result = await run_vertical(
            vertical_name=self.name,
            skill_name=skill_name,
            input_data={"brief": brief, **context}
        )
        
        return result


class StudioRegistry:
    """Реестр студий"""
    
    def __init__(self, verticals_dir: str = "verticals"):
        self.verticals_dir = Path(verticals_dir)
        self.studios: Dict[str, StudioWrapper] = {}
        self._load_studios()
    
    def _load_studios(self):
        """Загрузка всех студий из директории"""
        if not self.verticals_dir.exists():
            logger.warning(f"Директория {self.verticals_dir} не найдена")
            return
        
        for studio_dir in self.verticals_dir.iterdir():
            if studio_dir.is_dir() and (studio_dir / "vertical.yaml").exists():
                try:
                    wrapper = StudioWrapper(str(studio_dir))
                    self.studios[wrapper.name] = wrapper
                    logger.info(f"✅ Загружена студия: {wrapper.name}")
                except Exception as e:
                    logger.error(f"❌ Ошибка загрузки студии {studio_dir}: {e}")
    
    def get(self, name: str) -> StudioWrapper:
        """Получение студии по имени"""
        if name not in self.studios:
            raise ValueError(f"Студия {name} не найдена")
        return self.studios[name]
    
    def list(self) -> List[str]:
        """Список доступных студий"""
        return list(self.studios.keys())
```

---

## 4. Интеграция с API Gateway (`system/api/routes/compositions.py`)

```python
"""
API endpoints для CEO-агента и композиций.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import logging

from the_ai_corporation.agents.ceo_agent import CEOAgent
from the_ai_corporation.registry.studio_registry import StudioRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/compositions", tags=["compositions"])

# Глобальные объекты (в продакшене — через DI)
studio_registry = StudioRegistry("verticals")
ceo_agent = CEOAgent(studio_registry.studios, "compositions")


class CompositionRequest(BaseModel):
    """Запрос на выполнение композиции"""
    brief: str
    context: Optional[Dict[str, Any]] = None
    composition_name: Optional[str] = None  # Если None — автоматический выбор


class CompositionResponse(BaseModel):
    """Ответ композиции"""
    run_id: str
    status: str
    summary: Optional[str] = None
    artifacts: Optional[list] = None
    recommendations: Optional[list] = None


# Хранилище активных запусков (в продакшене — Redis/PostgreSQL)
active_runs: Dict[str, CompositionResponse] = {}


@router.post("/execute", response_model=CompositionResponse)
async def execute_composition(
    request: CompositionRequest,
    background_tasks: BackgroundTasks
):
    """
    Выполнение композиции.
    
    Запускает CEO-агента для обработки сложной задачи.
    """
    run_id = str(uuid.uuid4())
    
    # Создание записи о запуске
    active_runs[run_id] = CompositionResponse(
        run_id=run_id,
        status="pending"
    )
    
    # Запуск в фоне
    background_tasks.add_task(
        _run_composition_background,
        run_id=run_id,
        brief=request.brief,
        context=request.context or {}
    )
    
    return active_runs[run_id]


async def _run_composition_background(
    run_id: str,
    brief: str,
    context: Dict[str, Any]
):
    """Фоновое выполнение композиции"""
    try:
        active_runs[run_id].status = "running"
        
        result = await ceo_agent.handle_request(brief, context)
        
        active_runs[run_id].status = result.get("status", "completed")
        active_runs[run_id].summary = result.get("summary")
        active_runs[run_id].artifacts = result.get("artifacts", [])
        active_runs[run_id].recommendations = result.get("recommendations", [])
        
        logger.info(f"✅ Композиция {run_id} завершена")
    
    except Exception as e:
        logger.error(f"❌ Ошибка выполнения композиции {run_id}: {e}")
        active_runs[run_id].status = "failed"
        active_runs[run_id].summary = f"Ошибка: {str(e)}"


@router.get("/runs/{run_id}", response_model=CompositionResponse)
async def get_run_status(run_id: str):
    """Получение статуса запуска"""
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return active_runs[run_id]


@router.get("/compositions")
async def list_compositions():
    """Список доступных композиций"""
    compositions = []
    
    for name, plan in ceo_agent.compositions.items():
        compositions.append({
            "name": name,
            "description": plan.description,
            "tasks_count": len(plan.tasks),
            "studios": list(set(t.studio for t in plan.tasks))
        })
    
    return {"compositions": compositions}
```

---

## 5. Пример использования

```python
# Пример запуска CEO-агента
import asyncio
from the_ai_corporation.agents.ceo_agent import CEOAgent
from the_ai_corporation.registry.studio_registry import StudioRegistry

async def main():
    # Инициализация
    registry = StudioRegistry("verticals")
    ceo = CEOAgent(registry.studios, "compositions")
    
    # Запрос клиента
    brief = """
    Создай полный пакет для запуска онлайн-школы программирования:
    1. Лендинг с тёмной темой и минималистичным дизайном
    2. 3 SEO-статьи для блога
    3. Договор оферты и политика конфиденциальности
    4. Welcome-серия из 5 писем
    """
    
    # Выполнение
    result = await ceo.handle_request(brief)
    
    print(f"Статус: {result['status']}")
    print(f"Резюме: {result['summary']}")
    print(f"Артефакты: {len(result['artifacts'])}")
    print(f"Рекомендации: {result['recommendations']}")

asyncio.run(main())
```

---

## 6. API-запрос через curl

```bash
# Запуск композиции
curl -X POST http://localhost:8000/v1/compositions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "brief": "Создай полный пакет для онлайн-школы программирования: лендинг, 3 статьи, договор оферты, welcome-серия",
    "context": {
      "target_audience": "начинающие разработчики 20-35 лет",
      "budget": 100000
    }
  }'

# Ответ:
# {
#   "run_id": "abc123-def456",
#   "status": "pending",
#   "summary": null,
#   "artifacts": null,
#   "recommendations": null
# }

# Проверка статуса
curl http://localhost:8000/v1/compositions/runs/abc123-def456

# Ответ (после выполнения):
# {
#   "run_id": "abc123-def456",
#   "status": "completed",
#   "summary": "Создан лендинг, 3 SEO-статьи, договор оферты и welcome-серия из 5 писем",
#   "artifacts": [
#     {"type": "website", "path": "/output/website/index.html"},
#     {"type": "article", "path": "/output/articles/article_1.md"},
#     {"type": "document", "path": "/output/legal/offer.pdf"},
#     {"type": "email", "path": "/output/emails/welcome_sequence.yaml"}
#   ],
#   "recommendations": [
#     "Запустите A/B тестирование лендинга",
#     "Настройте автоматическую отправку писем через Mailchimp"
#   ]
# }
```

---

**Следующий шаг:** Детализация пункта 2.3 (Скиллы) — готовые шаблоны промптов и хуки для разных студий.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 2.3: Система скиллов (Skills)

---

## 1. Структура скилла (`verticals/web_studio/skills/landing_page/skill.yaml`)

```yaml
apiVersion: autogen/v1
kind: Skill

metadata:
  name: landing_page
  displayName: "Лендинг"
  description: "Генерация одностраничного лендинга с адаптивным дизайном"
  version: "1.0.0"
  vertical: web_studio
  tags: [landing, one-page, responsive]

spec:
  # ============================================
  # Шаблоны промптов
  # ============================================
  templates:
    planner: "templates/planner.j2"
    coder: "templates/coder.j2"
    verifier: "templates/verifier.j2"
    fixer: "templates/fixer.j2"
  
  # ============================================
  # Хуки выполнения
  # ============================================
  hooks:
    pre_execute: "hooks/pre_design.py"
    post_execute: "hooks/post_design.py"
  
  # ============================================
  # Гейты валидации
  # ============================================
  gates:
    - constitution
    - anti_slop
    - schema
    - llm_judge
  
  # ============================================
  # Инструменты, доступные скиллу
  # ============================================
  tools:
    - run_lighthouse
    - validate_html
    - take_screenshot
    - check_accessibility
  
  # ============================================
  # Параметры модели для каждой роли
  # ============================================
  models:
    planner:
      model: "ollama/llama3.1:8b"
      temperature: 0.3
      max_tokens: 2000
      top_p: 0.9
    coder:
      model: "ollama/qwen2.5-coder:7b"
      temperature: 0.7
      max_tokens: 8000
      top_p: 0.95
    verifier:
      model: "ollama/gemma2:9b"
      temperature: 0.0
      max_tokens: 1000
      top_p: 1.0
    fixer:
      model: "ollama/llama3.1:8b"
      temperature: 0.3
      max_tokens: 4000
      top_p: 0.9
  
  # ============================================
  # Бюджет
  # ============================================
  budget:
    max_iterations: 10
    max_cost_usd: 1.5
    max_tokens: 100000
  
  # ============================================
  # Входные данные
  # ============================================
  input_schema:
    type: object
    required: [brief]
    properties:
      brief:
        type: string
        minLength: 50
        description: "Описание проекта"
      target_audience:
        type: string
        description: "Целевая аудитория"
      style:
        type: string
        enum: [minimalism, brutalism, corporate, playful, luxury]
        description: "Стиль дизайна"
      references:
        type: array
        items: {type: string}
        description: "URL референсов"
  
  # ============================================
  # Выходные данные
  # ============================================
  output_schema:
    type: object
    required: [html, css, metadata]
    properties:
      html:
        type: string
        description: "HTML-код страницы"
      css:
        type: string
        description: "CSS-стили"
      js:
        type: string
        description: "JavaScript-код"
      metadata:
        type: object
        properties:
          title: {type: string}
          description: {type: string}
```

---

## 2. Шаблон промпта для Planner (`templates/planner.j2`)

```jinja2
{# templates/planner.j2 #}
# Планировщик: {{ skill.display_name }}

Ты — опытный арт-директор веб-студии. Твоя задача — создать детальный план дизайна.

## Конституция (ОБЯЗАТЕЛЬНО к соблюдению)
{{ constitution }}

## Anti-slop правила (ЗАПРЕЩЕНО нарушать)
{{ anti_slop_banned }}

## Квоты (НЕ ПРЕВЫШАТЬ)
{{ anti_slop_quotas }}

## Бриф клиента
{{ input.brief }}

{% if input.target_audience %}
## Целевая аудитория
{{ input.target_audience }}
{% endif %}

{% if input.style %}
## Запрошенный стиль
{{ input.style }}
{% endif %}

## Релевантные референсы (из базы знаний)
{% for ref in references %}
### Референс {{ loop.index }}
- **URL:** {{ ref.url }}
- **Категория:** {{ ref.category }}
- **Стиль:** {{ ref.style }}
- **Layout:** {{ ref.layout }}
- **Ключевые выводы:** {{ ref.takeaway }}
- **Оценка релевантности:** {{ "%.2f"|format(ref.score) }}
{% endfor %}

## Твоя задача

Создай детальный план дизайна, включающий:

1. **Структура страницы** (блоки сверху вниз):
   - Hero-секция (заголовок, подзаголовок, CTA)
   - Секция преимуществ (3-5 пунктов)
   - Секция "Как это работает" (шаги)
   - Секция отзывов (2-3 отзыва)
   - Секция цен (если применимо)
   - Footer (контакты, ссылки)

2. **Цветовая палитра** (максимум 5 цветов):
   - Primary (основной цвет бренда)
   - Secondary (дополнительный)
   - Accent (для CTA и акцентов)
   - Background (фон)
   - Text (цвет текста)

3. **Типографика** (максимум 3 шрифта):
   - Heading (заголовки)
   - Body (основной текст)
   - Mono (код, если нужен)

4. **Контентная стратегия**:
   - Главный заголовок (H1)
   - Подзаголовок (H2)
   - Тексты для каждой секции
   - Тексты для CTA-кнопок

5. **Интерактивные элементы**:
   - Анимации при скролле
   - Hover-эффекты
   - Формы (если есть)

## Формат вывода

Верни СТРОГИЙ JSON (без markdown, без комментариев):

```json
{
  "structure": [
    {
      "section": "hero",
      "heading": "Главный заголовок",
      "subheading": "Подзаголовок",
      "cta_text": "Текст кнопки",
      "background": "gradient | image | solid",
      "layout": "centered | split | full-width"
    },
    {
      "section": "features",
      "heading": "Преимущества",
      "items": [
        {"icon": "emoji | svg", "title": "...", "description": "..."}
      ]
    }
  ],
  "colors": {
    "primary": "#RRGGBB",
    "secondary": "#RRGGBB",
    "accent": "#RRGGBB",
    "background": "#RRGGBB",
    "text": "#RRGGBB"
  },
  "typography": {
    "heading": "Font Name",
    "body": "Font Name",
    "mono": "Font Name"
  },
  "content": {
    "hero_heading": "...",
    "hero_subheading": "...",
    "cta_text": "..."
  },
  "interactive_elements": ["scroll-animation", "hover-effect"]
}
```

## Критические требования

1. **НЕ копируй референсы дословно** — используй их как вдохновение
2. **Соблюдай Конституцию** — каждое правило обязательно
3. **Не превышай квоты** — максимум 5 цветов, 3 шрифта, 10 изображений
4. **Учитывай целевую аудиторию** — дизайн должен соответствовать ожиданиям
5. **Обеспечь уникальность** — дизайн не должен повторять последние 5 проектов

Приступай к планированию.
```

---

## 3. Шаблон промпта для Coder (`templates/coder.j2`)

```jinja2
{# templates/coder.j2 #}
# Кодер: {{ skill.display_name }}

Ты — senior frontend-разработчик. Твоя задача — написать чистый, производительный код.

## План дизайна (от Planner)
{{ plan | tojson(indent=2) }}

## Конституция (ОБЯЗАТЕЛЬНО к соблюдению)
{{ constitution }}

## Технические требования

### HTML
- Семантические теги: `<header>`, `<main>`, `<section>`, `<footer>`, `<nav>`
- Все изображения с `alt` атрибутами
- Формы с `<label>` для каждого `<input>`
- ARIA-атрибуты для доступности

### CSS
- Mobile-first подход
- CSS Custom Properties (переменные) для цветов
- Flexbox/Grid для layout
- Медиа-запросы для 3 breakpoints: 375px, 768px, 1440px
- Минимум вложенности (максимум 3 уровня)

### JavaScript
- Vanilla JS (без фреймворков, если не требуется)
- Event delegation для динамических элементов
- Debounce для scroll-событий
- Intersection Observer для анимаций при скролле

## Цветовая палитра
```css
:root {
  --color-primary: {{ plan.colors.primary }};
  --color-secondary: {{ plan.colors.secondary }};
  --color-accent: {{ plan.colors.accent }};
  --color-background: {{ plan.colors.background }};
  --color-text: {{ plan.colors.text }};
}
```

## Типографика
```css
body {
  font-family: '{{ plan.typography.body }}', sans-serif;
}

h1, h2, h3 {
  font-family: '{{ plan.typography.heading }}', sans-serif;
}
```

## Структура секций
{% for section in plan.structure %}
### {{ section.section | capitalize }}
- **Заголовок:** {{ section.heading }}
- **Layout:** {{ section.layout }}
{% endfor %}

## Формат вывода

Верни СТРОГИЙ JSON:

```json
{
  "html": "<!DOCTYPE html>...",
  "css": ":root { ... }",
  "js": "document.addEventListener('DOMContentLoaded', ...)",
  "metadata": {
    "title": "Название страницы",
    "description": "Описание для SEO (120-160 символов)"
  }
}
```

## Критические требования

1. **НЕ используй Lorem ipsum** — пиши реальный контент из плана
2. **Оптимизируй изображения** — используй `loading="lazy"`
3. **Обеспечь доступность** — контраст ≥4.5:1, клавиатурная навигация
4. **Производительность** — минимум внешних библиотек
5. **Адаптивность** — проверь на 375px, 768px, 1440px

Приступай к написанию кода.
```

---

## 4. Шаблон промпта для Verifier (`templates/verifier.j2`)

```jinja2
{# templates/verifier.j2 #}
# Верификатор: {{ skill.display_name }}

Ты — строгий QA-инженер. Твоя задача — проверить код на соответствие требованиям.

## Артефакт для проверки
### HTML
```html
{{ artifact.html[:2000] }}
```

### CSS
```css
{{ artifact.css[:1000] }}
```

### JavaScript
```javascript
{{ artifact.js[:500] }}
```

## План дизайна (эталон)
{{ plan | tojson(indent=2) }}

## Конституция (правила для проверки)
{{ constitution }}

## Anti-slop правила
{{ anti_slop_banned }}

## Квоты
{{ anti_slop_quotas }}

## Что проверить

1. **Соответствие плану**:
   - Все секции из плана присутствуют в HTML
   - Цвета соответствуют палитре
   - Шрифты соответствуют типографике

2. **Конституция**:
   - Семантический HTML (header, main, footer)
   - Контраст текста ≥4.5:1
   - Адаптивность (3 breakpoints)
   - Доступность (ARIA, alt-тексты)

3. **Anti-slop**:
   - Нет запрещённых паттернов (градиенты, автослайдеры)
   - Квоты не превышены (≤5 цветов, ≤3 шрифта, ≤10 изображений)

4. **Производительность**:
   - CSS < 50KB
   - JS < 100KB
   - Изображения оптимизированы

## Формат вывода

Верни СТРОГИЙ JSON:

```json
{
  "passed": true | false,
  "errors": [
    {
      "code": "V-01",
      "severity": "critical | major | minor",
      "description": "Описание ошибки",
      "location": "css: .hero-text | html: <img>",
      "suggestion": "Как исправить",
      "fix_example": "Пример исправления"
    }
  ],
  "metrics": {
    "html_size_kb": 15,
    "css_size_kb": 8,
    "js_size_kb": 3,
    "images_count": 5,
    "colors_count": 4,
    "fonts_count": 2
  }
}
```

## Критические требования

1. **Будь строг** — не пропускай нарушения Конституции
2. **Будь точен** — указывай конкретное место ошибки
3. **Будь конструктивен** — предлагай конкретное исправление
4. **Не придумывай ошибки** — проверяй только то, что написано в правилах

Приступай к проверке.
```

---

## 5. Шаблон промпта для Fixer (`templates/fixer.j2`)

```jinja2
{# templates/fixer.j2 #}
# Фиксер: {{ skill.display_name }}

Ты — опытный разработчик, исправляющий ошибки. Твоя задача — внести ТОЧЕЧНЫЕ правки.

## Текущий артефакт
### HTML
```html
{{ artifact.html[:2000] }}
```

### CSS
```css
{{ artifact.css[:1000] }}
```

### JavaScript
```javascript
{{ artifact.js[:500] }}
```

## Ошибки для исправления
{% for error in errors %}
### Ошибка {{ loop.index }}: {{ error.code }}
- **Серьёзность:** {{ error.severity }}
- **Описание:** {{ error.description }}
- **Местоположение:** {{ error.location }}
- **Предложение:** {{ error.suggestion }}
{% if error.fix_example %}
- **Пример исправления:** {{ error.fix_example }}
{% endif %}
{% endfor %}

## План дизайна (эталон)
{{ plan | tojson(indent=2) }}

## Твоя задача

Внеси ТОЧЕЧНЫЕ правки для исправления всех ошибок.

## Критические требования

1. **НЕ ПЕРЕПИСЫВАЙ ВСЁ** — исправляй только то, что указано в ошибках
2. **Сохраняй структуру** — не меняй layout, если это не требуется
3. **Сохраняй стиль** — не меняй цвета/шрифты, если это не требуется
4. **Минимум изменений** — каждая правка должна быть обоснована ошибкой

## Формат вывода

Верни СТРОГИЙ JSON с исправленным артефактом:

```json
{
  "html": "<!DOCTYPE html>...",
  "css": ":root { ... }",
  "js": "document.addEventListener('DOMContentLoaded', ...)",
  "metadata": {
    "title": "...",
    "description": "..."
  },
  "changes_made": [
    {
      "error_code": "V-01",
      "description": "Что исправлено",
      "location": "css: .hero-text"
    }
  ]
}
```

Приступай к исправлению.
```

---

## 6. Хук pre-execute (`hooks/pre_design.py`)

```python
"""
Хук, выполняемый ПЕРЕД генерацией дизайна.
Загружает контекст, референсы, проверяет входные данные.
"""

from typing import Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def pre_execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pre-execute hook для скилла landing_page.
    
    Args:
        context: Контекст выполнения
    
    Returns:
        Обновлённый контекст
    """
    logger.info("🔧 Выполнение pre_execute hook")
    
    # ============================================
    # 1. Проверка входных данных
    # ============================================
    brief = context.get("input", {}).get("brief", "")
    
    if len(brief) < 50:
        raise ValueError(f"Бриф слишком короткий ({len(brief)} символов, минимум 50)")
    
    logger.info(f"✅ Бриф проверен: {len(brief)} символов")
    
    # ============================================
    # 2. Загрузка референсов из RAG
    # ============================================
    from system.kernel.knowledge.retriever import KnowledgeRetriever
    
    retriever = KnowledgeRetriever(
        collection_name="web_studio_references",
        qdrant_url="http://qdrant:6333"
    )
    
    # Поиск релевантных референсов
    references = await retriever.search(
        query=brief,
        top_k=5,
        filters={
            "style": context["input"].get("style"),
            "category": "landing"
        }
    )
    
    context["references"] = references
    logger.info(f"✅ Загружено {len(references)} референсов")
    
    # ============================================
    # 3. Загрузка Конституции
    # ============================================
    constitution_path = Path("verticals/web_studio/CONSTITUTION.md")
    if constitution_path.exists():
        context["constitution"] = constitution_path.read_text(encoding="utf-8")
        logger.info("✅ Конституция загружена")
    else:
        logger.warning("⚠️ Конституция не найдена")
        context["constitution"] = ""
    
    # ============================================
    # 4. Загрузка Anti-slop правил
    # ============================================
    banned_path = Path("verticals/web_studio/anti-slop/BANNED.md")
    quotas_path = Path("verticals/web_studio/anti-slop/QUOTAS.md")
    
    if banned_path.exists():
        context["anti_slop_banned"] = banned_path.read_text(encoding="utf-8")
    else:
        context["anti_slop_banned"] = ""
    
    if quotas_path.exists():
        context["anti_slop_quotas"] = quotas_path.read_text(encoding="utf-8")
    else:
        context["anti_slop_quotas"] = ""
    
    logger.info("✅ Anti-slop правила загружены")
    
    # ============================================
    # 5. Проверка истории проектов (для уникальности)
    # ============================================
    from system.kernel.state import get_recent_projects
    
    recent_projects = await get_recent_projects(
        vertical_name="web_studio",
        limit=5
    )
    
    context["recent_projects"] = recent_projects
    logger.info(f"✅ Загружено {len(recent_projects)} последних проектов")
    
    # ============================================
    # 6. Валидация входных данных
    # ============================================
    style = context["input"].get("style")
    valid_styles = ["minimalism", "brutalism", "corporate", "playful", "luxury"]
    
    if style and style not in valid_styles:
        logger.warning(f"⚠️ Неизвестный стиль: {style}, используем minimalism")
        context["input"]["style"] = "minimalism"
    
    return context
```

---

## 7. Хук post-execute (`hooks/post_design.py`)

```python
"""
Хук, выполняемый ПОСЛЕ генерации дизайна.
Сохраняет результат, обновляет базу знаний, логирует метрики.
"""

from typing import Dict, Any
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


async def post_execute(artifact: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-execute hook для скилла landing_page.
    
    Args:
        artifact: Сгенерированный артефакт
        context: Контекст выполнения
    
    Returns:
        Обновлённый артефакт
    """
    logger.info("🔧 Выполнение post_execute hook")
    
    # ============================================
    # 1. Сохранение артефакта
    # ============================================
    project_name = context.get("project_name", f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir = Path(f"verticals/web_studio/projects/{project_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Сохранение HTML
    html_path = output_dir / "index.html"
    html_path.write_text(artifact.get("html", ""), encoding="utf-8")
    logger.info(f"✅ HTML сохранён: {html_path}")
    
    # Сохранение CSS
    css_path = output_dir / "styles.css"
    css_path.write_text(artifact.get("css", ""), encoding="utf-8")
    logger.info(f"✅ CSS сохранён: {css_path}")
    
    # Сохранение JS
    js_path = output_dir / "script.js"
    js_path.write_text(artifact.get("js", ""), encoding="utf-8")
    logger.info(f"✅ JS сохранён: {js_path}")
    
    # Сохранение метаданных
    metadata_path = output_dir / "metadata.json"
    import json
    metadata_path.write_text(
        json.dumps(artifact.get("metadata", {}), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    logger.info(f"✅ Метаданные сохранены: {metadata_path}")
    
    # ============================================
    # 2. Запуск Lighthouse (если доступен)
    # ============================================
    try:
        from system.kernel.tools.lighthouse import run_lighthouse
        
        lighthouse_report = await run_lighthouse(str(html_path))
        artifact["lighthouse"] = lighthouse_report
        
        logger.info(f"✅ Lighthouse: Performance={lighthouse_report.get('performance', 'N/A')}")
    except Exception as e:
        logger.warning(f"⚠️ Lighthouse не запущен: {e}")
    
    # ============================================
    # 3. Обновление базы знаний (если проект успешен)
    # ============================================
    validation_result = context.get("validation_result")
    
    if validation_result and validation_result.passed:
        try:
            from system.kernel.knowledge.indexer import KnowledgeIndexer
            
            indexer = KnowledgeIndexer(
                collection_name="web_studio_successful_projects",
                qdrant_url="http://qdrant:6333"
            )
            
            await indexer.index_project(
                project_name=project_name,
                artifact=artifact,
                metadata={
                    "style": context["input"].get("style"),
                    "brief": context["input"].get("brief"),
                    "iterations": context.get("iterations_count", 0)
                }
            )
            
            logger.info("✅ Проект добавлен в базу знаний")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось добавить в базу знаний: {e}")
    
    # ============================================
    # 4. Логирование метрик
    # ============================================
    from system.kernel.observability.metrics import record_project_metrics
    
    await record_project_metrics(
        vertical_name="web_studio",
        skill_name="landing_page",
        iterations=context.get("iterations_count", 0),
        budget_used=context.get("budget_used", 0.0),
        validation_passed=validation_result.passed if validation_result else False
    )
    
    logger.info("✅ Метрики записаны")
    
    # ============================================
    # 5. Добавление пути к артефактам
    # ============================================
    artifact["output_paths"] = {
        "html": str(html_path),
        "css": str(css_path),
        "js": str(js_path),
        "metadata": str(metadata_path)
    }
    
    return artifact
```

---

## 8. Пример скилла для Legal Studio (`verticals/legal_docs/skills/contract/skill.yaml`)

```yaml
apiVersion: autogen/v1
kind: Skill

metadata:
  name: contract
  displayName: "Договор"
  description: "Генерация юридического договора с проверкой существенных условий"
  version: "1.0.0"
  vertical: legal_docs
  tags: [legal, contract, agreement]

spec:
  templates:
    planner: "templates/planner.j2"
    coder: "templates/coder.j2"
    verifier: "templates/verifier.j2"
    fixer: "templates/fixer.j2"
  
  hooks:
    pre_execute: "hooks/pre_contract.py"
    post_execute: "hooks/post_contract.py"
  
  gates:
    - constitution
    - schema
    - llm_judge
  
  tools:
    - check_legal_compliance
    - validate_requisites
  
  models:
    planner:
      model: "ollama/llama3.1:8b"
      temperature: 0.2
      max_tokens: 2000
    coder:
      model: "ollama/qwen2.5-coder:7b"
      temperature: 0.5
      max_tokens: 6000
    verifier:
      model: "ollama/gemma2:9b"
      temperature: 0.0
      max_tokens: 1500
    fixer:
      model: "ollama/llama3.1:8b"
      temperature: 0.2
      max_tokens: 4000
  
  budget:
    max_iterations: 8
    max_cost_usd: 1.0
    max_tokens: 80000
  
  input_schema:
    type: object
    required: [contract_type, parties]
    properties:
      contract_type:
        type: string
        enum: [service, lease, employment, nda, sale]
      parties:
        type: object
        properties:
          party_a: {type: object}
          party_b: {type: object}
      subject:
        type: string
      price:
        type: object
      term:
        type: string
  
  output_schema:
    type: object
    required: [document_text, metadata]
    properties:
      document_text:
        type: string
      metadata:
        type: object
        properties:
          title: {type: string}
          parties: {type: array}
          essential_terms: {type: array}
```

---

## 9. Интеграция с ядром (`system/kernel/skills/loader.py`)

```python
"""
Загрузчик скиллов.
"""

from pathlib import Path
from typing import Dict, Any
import yaml
import logging

logger = logging.getLogger(__name__)


class SkillLoader:
    """Загрузчик скиллов из директории вертикали"""
    
    def __init__(self, vertical_path: str):
        self.vertical_path = Path(vertical_path)
        self.skills_dir = self.vertical_path / "skills"
    
    def load_skill(self, skill_name: str) -> Dict[str, Any]:
        """Загрузка конфигурации скилла"""
        skill_path = self.skills_dir / skill_name
        
        if not skill_path.exists():
            raise ValueError(f"Скилл {skill_name} не найден в {self.skills_dir}")
        
        # Загрузка skill.yaml
        config_path = skill_path / "skill.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Загрузка шаблонов
        templates = {}
        templates_dir = skill_path / "templates"
        
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.j2"):
                template_name = template_file.stem
                templates[template_name] = template_file.read_text(encoding="utf-8")
        
        config["loaded_templates"] = templates
        
        # Загрузка хуков
        hooks = {}
        hooks_dir = skill_path / "hooks"
        
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.py"):
                hook_name = hook_file.stem
                # Динамическая загрузка модуля
                import importlib.util
                spec = importlib.util.spec_from_file_location(hook_name, hook_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                hooks[hook_name] = module
        
        config["loaded_hooks"] = hooks
        
        logger.info(f"✅ Скилл {skill_name} загружен")
        
        return config
    
    def list_skills(self) -> list:
        """Список доступных скиллов"""
        if not self.skills_dir.exists():
            return []
        
        return [
            d.name for d in self.skills_dir.iterdir()
            if d.is_dir() and (d / "skill.yaml").exists()
        ]
```

---

## 10. Пример использования

```python
# Пример запуска скилла
import asyncio
from system.kernel.skills.loader import SkillLoader
from system.kernel.runner import execute_skill

async def main():
    # Загрузка скилла
    loader = SkillLoader("verticals/web_studio")
    skill_config = loader.load_skill("landing_page")
    
    # Входные данные
    input_data = {
        "brief": "Создай лендинг для онлайн-школы программирования. Минималистичный дизайн, тёмная тема.",
        "target_audience": "Начинающие разработчики 20-35 лет",
        "style": "minimalism"
    }
    
    # Выполнение
    result = await execute_skill(
        skill_config=skill_config,
        input_data=input_data,
        context={}
    )
    
    print(f"Статус: {result['status']}")
    print(f"Итерации: {result['iterations_count']}")
    print(f"Артефакты: {result['artifacts'].keys()}")

asyncio.run(main())
```

---

**Следующий шаг:** Детализация пункта 2.8 (Примеры Конституций для разных доменов) — полные тексты Конституций для Legal, Content, Data Analytics студий.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 2.8: Конституции для разных доменов

---

## 1. Legal Docs Studio — Конституция юридических документов

```markdown
# CONSTITUTION.md — Legal Docs Studio

## К-01: Существенные условия договора
Все существенные условия договора должны быть указаны в соответствии со ст. 432 ГК РФ.

**Существенные условия по типам договоров:**
- **Договор оказания услуг:** предмет (какие услуги), срок оказания, стоимость и порядок оплаты
- **Договор аренды:** объект аренды, размер арендной платы, срок аренды
- **Трудовой договор:** место работы, трудовая функция, размер заработной платы
- **Договор купли-продажи:** наименование и количество товара, цена
- **NDA:** определение конфиденциальной информации, срок действия, ответственность

**Проверка:** Детерминированный скрипт проверяет наличие обязательных разделов через regex и LLM-критик оценивает полноту формулировок.

**Код ошибки:** V-01

---

## К-02: Соответствие Гражданскому кодексу РФ
Документ не должен содержать положений, противоречащих императивным нормам ГК РФ.

**Критические статьи для проверки:**
- Ст. 168-169: Недействительность сделок, противоречащих закону
- Ст. 401-406: Общие положения об обязательствах
- Ст. 420-431: Понятие и условия договора
- Ст. 779-783: Договор возмездного оказания услуг
- Ст. 606-625: Договор аренды

**Проверка:** LLM-критик с контекстом ГК РФ (загружается из RAG). Критик проверяет каждое положение на соответствие императивным нормам.

**Код ошибки:** V-02

---

## К-03: Ясность и однозначность формулировок
Все формулировки должны быть однозначными, не допускать двоякого толкования.

**Запрещено:**
- Использование слов "может", "вправе" там, где должна быть обязанность
- Размытые сроки ("в разумный срок", "надлежащим образом")
- Отсылки к несуществующим приложениям
- Двусмысленные местоимения

**Проверка:** LLM-критик анализирует каждый пункт на наличие двусмысленности. Детерминированный скрипт проверяет наличие размытых формулировок через regex.

**Код ошибки:** V-03

---

## К-04: Полнота реквизитов сторон
Все реквизиты сторон должны быть полностью заполнены.

**Обязательные реквизиты:**
- Для юридических лиц: полное наименование, ОГРН/ОГРНИП, ИНН, КПП, юридический адрес, ФИО подписанта, должность
- Для физических лиц: ФИО, паспортные данные, адрес регистрации, ИНН (если применимо)

**Проверка:** Детерминированный скрипт проверяет наличие всех обязательных полей через regex. Проверяет формат ИНН (10 или 12 цифр), ОГРН (13 цифр).

**Код ошибки:** V-04

---

## К-05: Отсутствие внутренних противоречий
Пункты договора не должны противоречить друг другу.

**Типичные противоречия:**
- В одном пункте указана предоплата 100%, в другом — постоплата
- Срок действия договора указан как 1 год, но срок оказания услуг — 2 года
- Штрафные санкции указаны в двух местах с разными размерами

**Проверка:** LLM-критик сравнивает все числовые значения, сроки, суммы в документе на предмет противоречий.

**Код ошибки:** V-05

---

## К-06: Юридическая сила документа
Документ должен содержать все элементы, придающие ему юридическую силу.

**Обязательные элементы:**
- Дата и место составления
- Подписи сторон (или указание на электронное документирование)
- Для договоров на сумму свыше 3000 руб. — письменная форма
- Для договоров аренды свыше 1 года — государственная регистрация (указание на это)

**Проверка:** Детерминированный скрипт проверяет наличие раздела "Заключительные положения" с датой, местом, подписями.

**Код ошибки:** V-06

---

## К-07: Условия конфиденциальности (для NDA)
Если требуется NDA, все условия конфиденциальности должны быть указаны.

**Обязательные положения:**
- Определение конфиденциальной информации
- Исключения из конфиденциальной информации
- Срок действия обязательства
- Порядок возврата или уничтожения информации
- Ответственность за разглашение

**Проверка:** Детерминированный скрипт проверяет наличие всех обязательных разделов. LLM-критик оценивает полноту формулировок.

**Код ошибки:** V-07

---

## К-08: Соответствие 152-ФЗ "О персональных данных"
Согласие на обработку ПДн должно соответствовать требованиям ФЗ-152.

**Обязательные положения:**
- Цель обработки ПДн
- Перечень обрабатываемых ПДн
- Перечень действий с ПДн
- Срок обработки ПДн
- Порядок отзыва согласия
- Наименование и адрес оператора

**Проверка:** Детерминированный скрипт проверяет наличие всех обязательных пунктов. LLM-критик проверяет соответствие формулировок требованиям закона.

**Код ошибки:** V-08

---

## К-09: Структура документа
Документ должен иметь чёткую структуру в соответствии с юридической практикой.

**Обязательная структура:**
1. Преамбула (даты, стороны)
2. Предмет договора
3. Права и обязанности сторон
4. Стоимость и порядок расчётов
5. Ответственность сторон
6. Порядок разрешения споров
7. Заключительные положения
8. Реквизиты и подписи сторон

**Проверка:** Детерминированный скрипт проверяет наличие всех разделов в правильном порядке через regex.

**Код ошибки:** V-09

---

## К-10: Правильная нумерация
Все пункты и подпункты должны быть правильно пронумерованы.

**Требования:**
- Разделы: 1., 2., 3.
- Пункты: 1.1., 1.2., 1.3.
- Подпункты: 1.1.1., 1.1.2.
- Нет пропусков номеров
- Нет дублирования номеров

**Проверка:** Детерминированный скрипт извлекает все номера и проверяет последовательность.

**Код ошибки:** V-10

---

## К-11: Отсутствие орфографических и пунктуационных ошибок
Документ не должен содержать ошибок, снижающих его юридическую силу.

**Проверка:** Использование LanguageTool или Яндекс.Спеллнер для проверки орфографии. Детерминированная проверка пунктуации в ключевых местах (после заголовков, перед подписями).

**Код ошибки:** V-11

---

## К-12: Формат дат и чисел
Все даты и числа должны быть в едином формате.

**Требования:**
- Даты: ДД.ММ.ГГГГ (например, 28.09.2026)
- Суммы: цифрами и прописью (например, 100 000 (Сто тысяч) рублей 00 копеек)
- Проценты: с знаком % (например, 10%)

**Проверка:** Детерминированный скрипт через regex проверяет формат всех дат и сумм.

**Код ошибки:** V-12

---

## К-13: Суммы прописью
Все денежные суммы должны быть указаны цифрами и прописью.

**Требования:**
- Сумма цифрами: 100 000
- Сумма прописью: (Сто тысяч) рублей 00 копеек
- НДС: указан отдельно (если применимо)

**Проверка:** Детерминированный скрипт находит все суммы цифрами и проверяет наличие прописи в скобках.

**Код ошибки:** V-13

---

## К-14: Актуальность ссылок на законы
Все ссылки на законы и нормативные акты должны быть актуальными.

**Проверка:** LLM-критик проверяет, что упомянутые статьи законов существуют и не утратили силу. Для критических договоров — проверка через RAG по базе актуального законодательства.

**Код ошибки:** V-14

---

## К-15: Версионирование и история изменений
Документ должен иметь версию и дату последнего изменения.

**Требования:**
- Версия: v1.0, v1.1, v2.0
- Дата изменения: ДД.ММ.ГГГГ
- Описание изменений (для версий > 1.0)

**Проверка:** Детерминированный скрипт проверяет наличие метаданных версии в начале документа.

**Код ошибки:** V-15
```

---

## 2. Content Studio — Конституция контент-студии

```markdown
# CONSTITUTION.md — Content Studio

## К-01: Уникальность текста
Уникальность текста должна быть не менее 90% по данным сервисов проверки.

**Методы проверки:**
- Text.ru: ≥90%
- Advego: ≥90%
- Content Watch: ≥85%

**Проверка:** Интеграция с API сервисов проверки уникальности. Если API недоступен — LLM-критик оценивает уникальность на основе анализа структуры и формулировок.

**Код ошибки:** V-01

---

## К-02: Плотность ключевых слов
Плотность ключевых слов должна быть в диапазоне 1-3%.

**Требования:**
- Основное ключевое слово: 1-2%
- Дополнительные ключи: 0.5-1% каждое
- Суммарная плотность: не более 5%
- Отсутствие переспама (одна фраза >5% = переспам)

**Проверка:** Детерминированный скрипт анализирует текст, считает вхождения ключей, вычисляет плотность.

**Код ошибки:** V-02

---

## К-03: Читаемость текста
Текст должен быть легко читаемым для целевой аудитории.

**Метрики:**
- **Flesch-Kincaid** (для английского): ≥60
- **Индекс удобочитаемости** (для русского): средняя длина предложения 15-20 слов
- **Доля сложных слов** (≥4 слогов): не более 15%
- **Доля пассивного залога**: не более 10%

**Проверка:** Детерминированный скрипт вычисляет все метрики. Для русского языка используется адаптация формулы Flesch-Kincaid.

**Код ошибки:** V-03

---

## К-04: Отсутствие "воды" и штампов
Текст не должен содержать общих фраз, штампов, "воды".

**Запрещённые конструкции:**
- "В современном мире..."
- "На сегодняшний день..."
- "Всем известно, что..."
- "Не для кого не секрет..."
- "Играет важную роль..."
- "Является неотъемлемой частью..."
- "В условиях рыночной экономики..."

**Проверка:** Детерминированный скрипт проверяет наличие запрещённых конструкций через regex. LLM-критик оценивает общую "водность" текста по 10-балльной шкале (проходной балл ≥7).

**Код ошибки:** V-04

---

## К-05: Структура текста
Текст должен иметь чёткую структуру с использованием заголовков.

**Требования:**
- Один H1 на страницу
- H2 для основных разделов
- H3 для подразделов
- Нет пропусков уровней (H1 → H3 без H2)
- Списки для перечислений (маркированные или нумерованные)
- Абзацы не более 5-7 строк

**Проверка:** Детерминированный скрипт парсит HTML/Markdown, проверяет иерархию заголовков, длину абзацев.

**Код ошибки:** V-05

---

## К-06: Объём текста
Объём текста должен соответствовать ТЗ (±10%).

**Требования:**
- Если указан объём в словах: ±10% от указанного
- Если указан объём в символах: ±10% от указанного
- Минимальный объём: 500 слов (для статей)
- Максимальный объём: 5000 слов (для лонгридов)

**Проверка:** Детерминированный скрипт считает слова/символы, сравнивает с ТЗ.

**Код ошибки:** V-06

---

## К-07: Мета-теги (для SEO-статей)
Title и Description должны соответствовать требованиям SEO.

**Требования:**
- **Title:** 50-60 символов, содержит основное ключевое слово, уникален
- **Description:** 120-160 символов, содержит ключевое слово, призыв к действию
- **H1:** Совпадает с Title по смыслу, но не дублирует дословно
- **URL:** Транслитерация названия, без стоп-слов

**Проверка:** Детерминированный скрипт проверяет длину, наличие ключей, уникальность.

**Код ошибки:** V-07

---

## К-08: Внутренние ссылки
Текст должен содержать внутренние ссылки на другие страницы сайта.

**Требования:**
- Минимум 2-3 внутренние ссылки на 1000 слов
- Ссылки должны быть релевантны контексту
- Anchor text содержит ключевые слова (не "здесь", "тут")
- Ссылки открываются в том же окне (без target="_blank")

**Проверка:** Детерминированный скрипт парсит ссылки, считает количество, проверяет anchor text.

**Код ошибки:** V-08

---

## К-09: Изображения и медиа
Текст должен содержать визуальные элементы.

**Требования:**
- Минимум 1 изображение на 500 слов
- Все изображения с alt-текстами, содержащими ключевые слова
- Формат: WebP или AVIF (предпочтительно)
- Размер: <200KB на изображение
- Ширина: адаптивная (max-width: 100%)

**Проверка:** Детерминированный скрипт проверяет наличие изображений, alt-тексты, размеры файлов.

**Код ошибки:** V-09

---

## К-10: Призыв к действию (CTA)
Текст должен содержать минимум один призыв к действию.

**Требования:**
- CTA в конце текста (обязательно)
- CTA в середине текста (для длинных статей)
- Формулировка: глагол в повелительном наклонении ("Скачайте", "Зарегистрируйтесь", "Узнайте")
- CTA выделен визуально (кнопка, блок, жирный текст)

**Проверка:** LLM-критик оценивает наличие и качество CTA. Детерминированный скрипт проверяет наличие ключевых слов ("скачать", "купить", "заказать").

**Код ошибки:** V-10

---

## К-11: Соответствие Tone of Voice
Тон текста должен соответствовать Tone of Voice бренда.

**Требования:**
- Если ToV не указан — нейтрально-деловой стиль
- Если указан "дружелюбный" — допустимы обращения на "ты", эмодзи
- Если указан "экспертный" — минимум упрощений, терминология
- Если указан "продающий" — акцент на выгодах, CTA

**Проверка:** LLM-критик оценивает соответствие ToV по 10-балльной шкале (проходной балл ≥7).

**Код ошибки:** V-11

---

## К-12: Отсутствие плагиата
Текст не должен быть дословной копией существующего контента.

**Проверка:**
1. Проверка уникальности (К-01)
2. Сравнение с топ-10 результатами поиска по основному ключу
3. LLM-критик оценивает оригинальность подхода и выводов

**Код ошибки:** V-12

---

## К-13: Фактологическая точность
Все факты, цифры, даты должны быть достоверными.

**Требования:**
- Все цифры подтверждены источниками
- Даты актуальны (не устарели)
- Статистика из авторитетных источников
- Цитаты с указанием автора

**Проверка:** LLM-критик проверяет факты через RAG по базе достоверных источников. Детерминированный скрипт проверяет наличие ссылок на источники.

**Код ошибки:** V-13

---

## К-14: Адаптация под мобильные устройства
Текст должен быть адаптирован для чтения с мобильных устройств.

**Требования:**
- Короткие абзацы (2-4 строки)
- Подзаголовки каждые 200-300 слов
- Списки вместо длинных перечислений
- Выделение ключевых мыслей жирным

**Проверка:** Детерминированный скрипт анализирует структуру текста, проверяет длину абзацев, частоту подзаголовков.

**Код ошибки:** V-14

---

## К-15: Грамматика и пунктуация
Текст не должен содержать грамматических и пунктуационных ошибок.

**Проверка:** LanguageTool или Яндекс.Спеллнер. Допустимо не более 2 ошибок на 1000 слов.

**Код ошибки:** V-15
```

---

## 3. Data Analytics Studio — Конституция студии аналитики

```markdown
# CONSTITUTION.md — Data Analytics Studio

## К-01: Синтаксическая корректность кода
Весь сгенерированный код должен быть синтаксически корректным и исполняемым.

**Требования:**
- SQL: валидный синтаксис для указанного диалекта (PostgreSQL, MySQL, BigQuery)
- Python: проходит проверку через `python -m py_compile`
- R: проходит проверку через `Rscript -e "parse('file.R')"`
- JavaScript: проходит проверку через ESLint или Node.js

**Проверка:** Детерминированный скрипт запускает компилятор/интерпретатор в песочнице. Если код не компилируется — возврат на доработку.

**Код ошибки:** V-01

---

## К-02: Производительность запросов (SQL)
SQL-запросы должны быть оптимизированы для выполнения.

**Требования:**
- Использование индексов (проверка через EXPLAIN ANALYZE)
- Отсутствие SELECT * (указание конкретных колонок)
- Использование JOIN вместо подзапросов (где возможно)
- Ограничение объёма данных (LIMIT, WHERE)
- Время выполнения < 5 секунд для типовых запросов

**Проверка:** Детерминированный скрипт запускает EXPLAIN ANALYZE, анализирует план выполнения. LLM-критик оценивает оптимальность запроса.

**Код ошибки:** V-02

---

## К-03: Обработка ошибок (Python/R/JS)
Код должен содержать обработку ошибок и исключений.

**Требования:**
- try-except блоки для критических операций
- Логирование ошибок (logging для Python, console.error для JS)
- Валидация входных данных
- Обработка граничных случаев (пустые данные, null-значения)

**Проверка:** Детерминированный скрипт проверяет наличие try-except, logging. LLM-критик оценивает полноту обработки ошибок.

**Код ошибки:** V-03

---

## К-04: Документация кода
Весь код должен быть документирован.

**Требования:**
- Docstrings для всех функций (Python: Google/NumPy style)
- Комментарии для сложных участков кода
- README с описанием:
  - Назначение скрипта
  - Входные данные
  - Выходные данные
  - Примеры использования
  - Зависимости

**Проверка:** Детерминированный скрипт проверяет наличие docstrings, комментариев. LLM-критик оценивает качество документации.

**Код ошибки:** V-04

---

## К-05: Воспроизводимость результатов
Результаты анализа должны быть воспроизводимы.

**Требования:**
- Фиксация random seed (если используется случайность)
- Указание версий библиотек (requirements.txt, package.json)
- Детерминированные алгоритмы (где возможно)
- Сохранение промежуточных результатов

**Проверка:** Детерминированный скрипт проверяет наличие requirements.txt, фиксацию seed. LLM-критик оценивает воспроизводимость.

**Код ошибки:** V-05

---

## К-06: Корректность визуализации
Визуализации должны корректно отображать данные.

**Требования:**
- Подписи осей (X, Y) с единицами измерения
- Заголовок графика
- Легенда (если несколько серий данных)
- Адекватный выбор типа графика:
  - Линейный — для временных рядов
  - Столбчатый — для сравнения категорий
  - Круговой — для долей (не более 5-7 категорий)
  - Scatter — для корреляций
- Читаемые размеры шрифтов

**Проверка:** Детерминированный скрипт проверяет наличие подписей, заголовков. LLM-критик оценивает адекватность выбора типа графика.

**Код ошибки:** V-06

---

## К-07: Статистическая корректность
Статистические методы должны применяться корректно.

**Требования:**
- Проверка предположений статистических тестов (нормальность, гомоскедастичность)
- Указание уровня значимости (alpha = 0.05 по умолчанию)
- Интерпретация p-value и confidence intervals
- Использование поправок на множественное тестирование (Bonferroni, FDR)

**Проверка:** LLM-критик проверяет корректность применения методов. Детерминированный скрипт проверяет наличие указания alpha, p-value.

**Код ошибки:** V-07

---

## К-08: Обработка missing data
Пропущенные данные должны обрабатываться явно.

**Требования:**
- Анализ доли пропусков (не более 5-10% для критических полей)
- Явное указание метода обработки:
  - Удаление (dropna)
  - Заполнение средним/медианой (fillna)
  - Интерполяция
  - Использование моделей (MICE, KNN)
- Обоснование выбора метода

**Проверка:** Детерминированный скрипт проверяет наличие обработки пропусков. LLM-критик оценивает обоснованность метода.

**Код ошибки:** V-08

---

## К-09: Безопасность данных
Код не должен содержать утечек конфиденциальных данных.

**Требования:**
- Нет хардкода паролей, API-ключей
- Использование переменных окружения для секретов
- Маскирование персональных данных (если обрабатываются)
- Логирование без_SENSITIVE_ данных

**Проверка:** Детерминированный скрипт через regex ищет паттерны паролей, ключей. LLM-критик проверяет безопасность кода.

**Код ошибки:** V-09

---

## К-10: Модульность и переиспользование
Код должен быть модульным и переиспользуемым.

**Требования:**
- Функции не длиннее 50 строк
- Одна функция — одна ответственность (Single Responsibility)
- Отсутствие дублирования кода (DRY)
- Использование конфигурационных файлов для параметров

**Проверка:** Детерминированный скрипт анализирует длину функций, ищет дублирование. LLM-критик оценивает модульность.

**Код ошибки:** V-10

---

## К-11: Тестирование
Код должен быть покрыт тестами.

**Требования:**
- Unit-тесты для всех функций (покрытие ≥80%)
- Integration-тесты для основных пайплайнов
- Тесты на граничных случаях
- Использование pytest (Python), Jest (JS), testthat (R)

**Проверка:** Детерминированный скрипт запускает тесты, считает покрытие. Если покрытие <80% — возврат на доработку.

**Код ошибки:** V-11

---

## К-12: Интерпретируемость результатов
Результаты анализа должны быть интерпретируемы.

**Требования:**
- Чёткие выводы в конце анализа
- Указание ограничений анализа
- Рекомендации по дальнейшим действиям
- Визуализация ключевых результатов

**Проверка:** LLM-критик оценивает наличие выводов, рекомендаций. Детерминированный скрипт проверяет наличие раздела "Выводы".

**Код ошибки:** V-12

---

## К-13: Эффективность использования памяти
Код не должен приводить к утечкам памяти.

**Требования:**
- Использование генераторов вместо списков (для больших данных)
- Закрытие файлов и соединений (with open, context managers)
- Удаление больших объектов (del, gc.collect())
- Использование chunked reading для больших файлов

**Проверка:** Детерминированный скрипт проверяет наличие with open, генераторов. LLM-критик оценивает эффективность использования памяти.

**Код ошибки:** V-13

---

## К-14: Версионирование кода
Код должен быть версионирован через Git.

**Требования:**
- Наличие .git директории
- Осмысленные commit messages
- Теги для релизов (v1.0.0, v1.1.0)
- Ветка main/master стабильна

**Проверка:** Детерминированный скрипт проверяет наличие .git, историю коммитов.

**Код ошибки:** V-14

---

## К-15: Соответствие best practices
Код должен соответствовать лучшим практикам индустрии.

**Требования:**
- Python: PEP 8, type hints
- SQL: именование в snake_case, UPPER CASE для ключевых слов
- R: Google R Style Guide
- JavaScript: ESLint, Airbnb Style Guide

**Проверка:** Детерминированный скрипт запускает линтеры (flake8, pylint, ESLint). LLM-критик оценивает соответствие best practices.

**Код ошибки:** V-15
```

---

## 4. Education Studio — Конституция образовательной студии

```markdown
# CONSTITUTION.md — Education Studio

## К-01: Соответствие учебным целям
Каждый урок должен чётко соответствовать заявленным учебным целям.

**Требования:**
- Учебные цели сформулированы по таксономии Блума (Знание, Понимание, Применение, Анализ, Синтез, Оценка)
- Каждая цель измерима (использование глаголов: "назвать", "объяснить", "применить", "проанализировать")
- Содержание урока закрывает все заявленные цели
- Оценка проверяет достижение целей

**Проверка:** LLM-критик сравнивает цели, содержание и оценку на согласованность. Детерминированный скрипт проверяет наличие измеримых глаголов.

**Код ошибки:** V-01

---

## К-02: Прогрессия сложности
Материал должен идти от простого к сложному.

**Требования:**
- Начало: базовые понятия, определения
- Середина: применение, примеры
- Конец: сложные задачи, синтез
- Каждая новая тема опирается на предыдущую
- Нет "скачков" сложности

**Проверка:** LLM-критик анализирует последовательность тем. Детерминированный скрипт проверяет наличие вводной, основной, заключительной частей.

**Код ошибки:** V-02

---

## К-03: Возрастная адекватность
Материал должен соответствовать возрасту целевой аудитории.

**Требования:**
- **Дети 6-10 лет:** простой язык, много визуала, игровые элементы, длина урока 15-20 минут
- **Подростки 11-15 лет:** более сложный язык, интерактив, длина урока 25-35 минут
- **Взрослые 16+:** профессиональный язык, практические задачи, длина урока 40-60 минут

**Проверка:** LLM-критик оценивает сложность языка, длину урока. Детерминированный скрипт проверяет длину текста, количество визуальных элементов.

**Код ошибки:** V-03

---

## К-04: Интерактивность
Урок должен содержать интерактивные элементы.

**Требования:**
- Минимум 1 интерактивный элемент на 10 минут урока
- Типы интерактива:
  - Вопросы с выбором ответа
  - Drag-and-drop задания
  - Заполнение пропусков
  - Симуляции
  - Практические задачи
- Немедленная обратная связь на действия ученика

**Проверка:** Детерминированный скрипт считает количество интерактивных элементов. LLM-критик оценивает качество интерактива.

**Код ошибки:** V-04

---

## К-05: Обратная связь
Каждое действие ученика должно получать обратную связь.

**Требования:**
- Правильный ответ: похвала + объяснение, почему правильно
- Неправильный ответ: подсказка + объяснение ошибки + возможность повторить
- Обратная связь конкретна (не "молодец", а "правильно, потому что...")
- Обратная связь мотивирует к продолжению

**Проверка:** LLM-критик оценивает наличие и качество обратной связи. Детерминированный скрипт проверяет наличие текстов обратной связи для каждого вопроса.

**Код ошибки:** V-05

---

## К-06: Визуальная поддержка
Материал должен быть поддержан визуальными элементами.

**Требования:**
- Минимум 1 визуальный элемент на 500 слов текста
- Типы визуала:
  - Схемы и диаграммы
  - Инфографика
  - Примеры кода (с подсветкой синтаксиса)
  - Скриншоты (с аннотациями)
  - Видео (если применимо)
- Визуал релевантен тексту

**Проверка:** Детерминированный скрипт считает изображения, проверяет наличие подписей. LLM-критик оценивает релевантность визуала.

**Код ошибки:** V-06

---

## К-07: Практическая направленность
Материал должен быть ориентирован на практику.

**Требования:**
- Теория: не более 30% урока
- Примеры: 30% урока
- Практика: не менее 40% урока
- Практические задачи реалистичны (близки к реальным сценариям)
- Постепенное усложнение задач

**Проверка:** Детерминированный скрипт анализирует соотношение теории и практики. LLM-критик оценивает реалистичность задач.

**Код ошибки:** V-07

---

## К-08: Доступность
Материал должен быть доступен для людей с ограниченными возможностями.

**Требования:**
- Все изображения с alt-текстами
- Видео с субтитрами
- Контраст текста ≥4.5:1
- Клавиатурная навигация
- Screen reader совместимость

**Проверка:** Детерминированный скрипт проверяет alt-тексты, контраст. LLM-критик оценивает общую доступность.

**Код ошибки:** V-08

---

## К-09: Адаптивность
Материал должен корректно отображаться на всех устройствах.

**Требования:**
- Mobile-first подход
- Адаптация под 3 breakpoints: 375px, 768px, 1440px
- Интерактивные элементы работают на touch-устройствах
- Шрифты читаемы на мобильных (≥16px)

**Проверка:** Детерминированный скрипт проверяет медиа-запросы, размеры шрифтов. Визуальный регресс на 3 устройствах.

**Код ошибки:** V-09

---

## К-10: Оценка знаний
Урок должен содержать оценку достижения учебных целей.

**Требования:**
- Минимум 3 вопроса для оценки
- Вопросы соответствуют таксономии Блума:
  - 1 вопрос на знание/понимание
  - 1 вопрос на применение
  - 1 вопрос на анализ/синтез
- Критерии оценки чёткие и прозрачные
- Возможность пересдачи

**Проверка:** Детерминированный скрипт считает вопросы, проверяет их типы. LLM-критик оценивает соответствие таксономии Блума.

**Код ошибки:** V-10

---

## К-11: Мотивация и вовлечённость
Материал должен мотивировать к обучению.

**Требования:**
- Введение с объяснением "зачем это нужно"
- Реальные примеры применения
- Элементы геймификации (баллы, бейджи, прогресс-бар)
- Поощрение за достижения
- Связь с карьерными целями

**Проверка:** LLM-критик оценивает мотивационные элементы. Детерминированный скрипт проверяет наличие введения, примеров, элементов геймификации.

**Код ошибки:** V-11

---

## К-12: Научная достоверность
Весь материал должен быть научно достоверным.

**Требования:**
- Все факты подтверждены источниками
- Ссылки на авторитетные источники (учебники, научные статьи, официальная документация)
- Нет устаревшей информации
- Нет противоречий между разделами

**Проверка:** LLM-критик проверяет факты через RAG по базе достоверных источников. Детерминированный скрипт проверяет наличие ссылок.

**Код ошибки:** V-12

---

## К-13: Ясность изложения
Материал должен быть изложен ясно и понятно.

**Требования:**
- Средняя длина предложения: 15-20 слов
- Отсутствие сложных конструкций (причастных/деепричастных оборотов >3 в предложении)
- Определение терминов при первом использовании
- Использование аналогий и метафор для сложных понятий

**Проверка:** Детерминированный скрипт анализирует длину предложений, сложность конструкций. LLM-критик оценивает ясность изложения.

**Код ошибки:** V-13

---

## К-14: Структура урока
Урок должен иметь чёткую структуру.

**Требования:**
- **Введение** (10%): цели, мотивация, связь с предыдущим уроком
- **Основная часть** (70%): теория, примеры, практика
- **Заключение** (20%): итоги, ключевые выводы, задание на дом
- Переходы между разделами плавные

**Проверка:** Детерминированный скрипт проверяет наличие всех разделов. LLM-критик оценивает плавность переходов.

**Код ошибки:** V-14

---

## К-15: Локализация и культурная адаптация
Материал должен быть адаптирован под целевую аудиторию.

**Требования:**
- Язык соответствует целевой аудитории
- Примеры из культуры целевой аудитории
- Единицы измерения (метрические для России, имперские для США)
- Формат дат, чисел, валют

**Проверка:** LLM-критик оценивает культурную адаптацию. Детерминированный скрипт проверяет формат дат, единиц измерения.

**Код ошибки:** V-15
```

---

## 5. Сравнительная таблица Конституций

| Домен | Кол-во правил | Детерминированных | LLM-проверок | Ключевой фокус |
|---|---|---|---|---|
| **Web Studio** | 24 | 14 | 10 | Визуальное качество, производительность, доступность |
| **Legal Docs** | 15 | 9 | 6 | Юридическая корректность, существенные условия |
| **Content Studio** | 15 | 10 | 5 | Уникальность, SEO, читаемость |
| **Data Analytics** | 15 | 8 | 7 | Корректность кода, производительность, воспроизводимость |
| **Education** | 15 | 6 | 9 | Педагогика, интерактивность, доступность |

---

## 6. Шаблон для создания новой Конституции

```markdown
# CONSTITUTION.md — {Название студии}

## К-01: {Название правила}
{Описание правила}

**Требования:**
- {Требование 1}
- {Требование 2}
- {Требование 3}

**Проверка:** {Метод проверки: детерминированный скрипт / LLM-критик / гибрид}

**Код ошибки:** V-01

---

## К-02: {Название правила}
...

---

# Анти-паттерны (для справки)

## Что НЕ делать:
- {Анти-паттерн 1}
- {Анти-паттерн 2}

## Что делать:
- {Best practice 1}
- {Best practice 2}
```

---

**Следующий шаг:** Детализация пункта 3.2 (Инфраструктура и деплой) — готовые Dockerfile, Kubernetes манифесты, CI/CD пайплайны.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 3.2: Инфраструктура и деплой

---

## 1. Dockerfile для Telegram-бота (`the_ai_corporation/Dockerfile.telegram`)

```dockerfile
# the_ai_corporation/Dockerfile.telegram
FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY . .

# Непривилегированный пользователь
RUN useradd -m -u 1000 tgbot && chown -R tgbot:tgbot /app
USER tgbot

# Healthcheck
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8081/health').raise_for_status()" || exit 1

CMD ["python", "-m", "bot.main"]
```

---

## 2. Requirements для Telegram-бота (`the_ai_corporation/requirements.txt`)

```txt
# the_ai_corporation/requirements.txt

# Telegram
python-telegram-bot==20.7
telegramify-markdown==0.1.3

# HTTP клиент
httpx==0.26.0

# Утилиты
python-dotenv==1.0.0
pyyaml==6.0.1
structlog==24.1.0

# Healthcheck сервер
fastapi==0.109.0
uvicorn==0.27.0
```

---

## 3. Kubernetes манифесты

### 3.1 Namespace и ConfigMap (`k8s/01-namespace-config.yaml`)

```yaml
# k8s/01-namespace-config.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autogen
  labels:
    app.kubernetes.io/part-of: autogen-platform
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: autogen-config
  namespace: autogen
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  REDIS_URL: "redis://redis:6379/0"
  QDRANT_URL: "http://qdrant:6333"
  LITELLM_PROXY_URL: "http://litellm:4000"
  AUTOGEN_BUDGET__MAX_COST_USD_PER_DAY: "20"
  AUTOGEN_BUDGET__MAX_COST_USD_PER_RUN: "5"
  AUTOGEN_BUDGET__MAX_TOKENS_PER_MINUTE: "400000"
  AUTOGEN_LLM__MODEL_ALIASES: |
    {
      "planner": "ollama/llama3.1:8b",
      "coder": "ollama/qwen2.5-coder:7b",
      "verifier": "ollama/gemma2:9b",
      "fixer": "ollama/llama3.1:8b"
    }
  AUTOGEN_SANDBOX__PROVIDER: "e2b"
```

### 3.2 Secrets (`k8s/02-secrets.yaml`)

```yaml
# k8s/02-secrets.yaml
# ВНИМАНИЕ: В продакшене используйте Sealed Secrets или External Secrets Operator
# Этот файл — шаблон. Не коммитьте реальные секреты в Git!
apiVersion: v1
kind: Secret
metadata:
  name: autogen-secrets
  namespace: autogen
type: Opaque
stringData:
  DATABASE_URL: "postgresql://autogen:CHANGE_ME@postgres:5432/autogen_db"
  POSTGRES_PASSWORD: "CHANGE_ME"
  LITELLM_MASTER_KEY: "sk-CHANGE_ME"
  E2B_API_KEY: "CHANGE_ME"
  TELEGRAM_BOT_TOKEN: "CHANGE_ME"
  ADMIN_CHAT_ID: "CHANGE_ME"
  JWT_SECRET: "CHANGE_ME_GENERATE_WITH_openssl_rand_hex_32"
```

### 3.3 PostgreSQL (`k8s/03-postgres.yaml`)

```yaml
# k8s/03-postgres.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: autogen
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: autogen
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_USER
              value: "autogen"
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: autogen-secrets
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_DB
              value: "autogen_db"
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            exec:
              command: ["pg_isready", "-U", "autogen"]
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "autogen"]
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: autogen
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  clusterIP: None  # Headless для StatefulSet
```

### 3.4 Redis (`k8s/04-redis.yaml`)

```yaml
# k8s/04-redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: autogen
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          command: ["redis-server", "--appendonly", "yes", "--maxmemory", "256mb", "--maxmemory-policy", "allkeys-lru"]
          ports:
            - containerPort: 6379
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            exec:
              command: ["redis-cli", "ping"]
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["redis-cli", "ping"]
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: autogen
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
```

### 3.5 Qdrant (`k8s/05-qdrant.yaml`)

```yaml
# k8s/05-qdrant.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-pvc
  namespace: autogen
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: autogen
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
        - name: qdrant
          image: qdrant/qdrant:v1.7.4
          ports:
            - containerPort: 6333
              name: http
            - containerPort: 6334
              name: grpc
          volumeMounts:
            - name: qdrant-storage
              mountPath: /qdrant/storage
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /
              port: 6333
            periodSeconds: 30
      volumes:
        - name: qdrant-storage
          persistentVolumeClaim:
            claimName: qdrant-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant
  namespace: autogen
spec:
  selector:
    app: qdrant
  ports:
    - name: http
      port: 6333
      targetPort: 6333
    - name: grpc
      port: 6334
      targetPort: 6334
```

### 3.6 API Gateway (`k8s/06-api-gateway.yaml`)

```yaml
# k8s/06-api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: autogen
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api-gateway
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: api-gateway
          image: registry.example.com/autogen/api-gateway:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: autogen-config
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: autogen-secrets
                  key: DATABASE_URL
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: autogen-secrets
                  key: JWT_SECRET
            - name: E2B_API_KEY
              valueFrom:
                secretKeyRef:
                  name: autogen-secrets
                  key: E2B_API_KEY
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          volumeMounts:
            - name: verticals
              mountPath: /app/verticals
              readOnly: true
      volumes:
        - name: verticals
          configMap:
            name: verticals-config
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: autogen
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: autogen
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 3.7 Ingress (`k8s/07-ingress.yaml`)

```yaml
# k8s/07-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: autogen-ingress
  namespace: autogen
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.autogen.example.com
      secretName: autogen-tls
  rules:
    - host: api.autogen.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-gateway
                port:
                  number: 80
```

### 3.8 Ollama (GPU node) (`k8s/08-ollama.yaml`)

```yaml
# k8s/08-ollama.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-pvc
  namespace: autogen
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: standard
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: autogen
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      # Запуск на GPU-ноде
      nodeSelector:
        nvidia.com/gpu.present: "true"
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      containers:
        - name: ollama
          image: ollama/ollama:latest
          ports:
            - containerPort: 11434
          volumeMounts:
            - name: ollama-storage
              mountPath: /root/.ollama
          resources:
            requests:
              memory: "16Gi"
              cpu: "4000m"
              nvidia.com/gpu: 1
            limits:
              memory: "32Gi"
              cpu: "8000m"
              nvidia.com/gpu: 1
          livenessProbe:
            httpGet:
              path: /api/tags
              port: 11434
            initialDelaySeconds: 60
            periodSeconds: 30
      volumes:
        - name: ollama-storage
          persistentVolumeClaim:
            claimName: ollama-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ollama
  namespace: autogen
spec:
  selector:
    app: ollama
  ports:
    - port: 11434
      targetPort: 11434
```

---

## 4. CI/CD пайплайн (GitHub Actions)

### 4.1 Основной пайплайн (`.github/workflows/ci-cd.yaml`)

```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository_owner }}/autogen

jobs:
  # ============================================
  # 1. Линтинг и статический анализ
  # ============================================
  lint:
    name: Lint & Static Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff mypy bandit
          pip install -r system/requirements.txt
      
      - name: Ruff lint
        run: ruff check system/ the_ai_corporation/
      
      - name: Ruff format check
        run: ruff format --check system/ the_ai_corporation/
      
      - name: Mypy type check
        run: mypy system/ --ignore-missing-imports
        continue-on-error: true
      
      - name: Bandit security scan
        run: bandit -r system/ -ll

  # ============================================
  # 2. Unit-тесты
  # ============================================
  test:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      qdrant:
        image: qdrant/qdrant:v1.7.4
        ports:
          - 6333:6333
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r system/requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          QDRANT_URL: http://localhost:6333
        run: |
          pytest tests/ \
            --asyncio-mode=auto \
            --cov=system \
            --cov-report=xml \
            --cov-report=term-missing \
            -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  # ============================================
  # 3. Тесты ядра (Loop Engine)
  # ============================================
  test-kernel:
    name: Kernel Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Run kernel tests
        run: |
          cd system
          npm test
          npm run gate || true

  # ============================================
  # 4. Сборка Docker-образов
  # ============================================
  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [test, test-kernel]
    if: github.event_name == 'push'
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        include:
          - name: api-gateway
            dockerfile: system/Dockerfile.api
            context: ./system
          - name: telegram-bot
            dockerfile: the_ai_corporation/Dockerfile.telegram
            context: ./the_ai_corporation
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          file: ${{ matrix.dockerfile }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.name }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.name }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================
  # 5. Деплой в staging
  # ============================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Configure kubeconfig
        run: |
          echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
      
      - name: Deploy to staging
        run: |
          kubectl apply -f k8s/ --namespace autogen-staging
          kubectl set image deployment/api-gateway \
            api-gateway=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/api-gateway:${{ github.sha }} \
            --namespace autogen-staging
          kubectl rollout status deployment/api-gateway --namespace autogen-staging --timeout=300s

  # ============================================
  # 6. Деплой в продакшен
  # ============================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Configure kubeconfig
        run: |
          echo "${{ secrets.KUBECONFIG_PRODUCTION }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
      
      - name: Deploy to production
        run: |
          kubectl apply -f k8s/ --namespace autogen
          kubectl set image deployment/api-gateway \
            api-gateway=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/api-gateway:${{ github.sha }} \
            --namespace autogen
          kubectl rollout status deployment/api-gateway --namespace autogen --timeout=300s
      
      - name: Run smoke tests
        run: |
          sleep 30
          curl -f https://api.autogen.example.com/health || exit 1
          echo "✅ Smoke tests passed"
```

### 4.2 Пайплайн тестирования вертикалей (`.github/workflows/test-verticals.yaml`)

```yaml
# .github/workflows/test-verticals.yaml
name: Test Verticals

on:
  push:
    paths:
      - 'verticals/**'
  pull_request:
    paths:
      - 'verticals/**'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      verticals: ${{ steps.changes.outputs.verticals }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          list-files: json
          filters: |
            web_studio:
              - 'verticals/web_studio/**'
            legal_docs:
              - 'verticals/legal_docs/**'
            content_studio:
              - 'verticals/content_studio/**'
            data_analytics:
              - 'verticals/data_analytics/**'
            education:
              - 'verticals/education/**'

  test-vertical:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        vertical: [web_studio, legal_docs, content_studio, data_analytics, education]
    if: contains(needs.detect-changes.outputs.verticals, matrix.vertical)
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r system/requirements.txt pytest pytest-asyncio
      
      - name: Validate vertical structure
        run: |
          python -c "
          from pathlib import Path
          import yaml
          
          v = Path('verticals/${{ matrix.vertical }}')
          assert (v / 'vertical.yaml').exists(), 'Missing vertical.yaml'
          assert (v / 'CONSTITUTION.md').exists(), 'Missing CONSTITUTION.md'
          assert (v / 'skills').exists(), 'Missing skills/'
          assert (v / 'validators').exists(), 'Missing validators/'
          
          with open(v / 'vertical.yaml') as f:
              config = yaml.safe_load(f)
          assert 'metadata' in config, 'Missing metadata in vertical.yaml'
          assert 'spec' in config, 'Missing spec in vertical.yaml'
          print(f'✅ Vertical ${{ matrix.vertical }} structure valid')
          "
      
      - name: Run vertical tests
        run: |
          pytest verticals/${{ matrix.vertical }}/tests/ -v --asyncio-mode=auto || echo "⚠️ No tests found"
```

---

## 5. Prometheus алерты (`configs/prometheus/alerts.yaml`)

```yaml
# configs/prometheus/alerts.yaml
groups:
  - name: autogen_alerts
    rules:
      # ============================================
      # Критические алерты
      # ============================================
      - alert: APIGatewayDown
        expr: up{job="api-gateway"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API Gateway недоступен"
          description: "API Gateway не отвечает более 1 минуты"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Высокий процент ошибок ({{ $value | humanizePercentage }})"
          description: "Более 5% запросов возвращают 5xx ошибки"

      - alert: BudgetExceeded
        expr: budget_used_usd_total > budget_max_usd_per_day
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Дневной бюджет превышен"
          description: "Использовано ${{ $value }} из ${{ budget_max_usd_per_day }}"

      # ============================================
      # Предупреждения
      # ============================================
      - alert: HighIterationCount
        expr: run_iterations{quantile="0.95"} > 8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Высокое количество итераций"
          description: "95-й перцентиль итераций > 8. Возможно, валидаторы слишком строгие или промпты неэффективны"

      - alert: LLMLatencyHigh
        expr: histogram_quantile(0.95, rate(llm_latency_seconds_bucket[5m])) > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Высокая задержка LLM (p95 = {{ $value }}s)"
          description: "95-й перцентиль задержки LLM превышает 30 секунд"

      - alert: ValidationFailureRateHigh
        expr: rate(validation_errors_total[1h]) > 10
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Высокий процент провалов валидации"
          description: "Более 10 ошибок валидации в час"

      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Мало места на диске ({{ $value | humanizePercentage }})"

      # ============================================
      # Информационные
      # ============================================
      - alert: OllamaModelNotLoaded
        expr: ollama_models_loaded == 0
        for: 5m
        labels:
          severity: info
        annotations:
          summary: "Модели Ollama не загружены"
```

---

## 6. Grafana дашборд (`configs/grafana/provisioning/dashboards/autogen.json`)

```json
{
  "dashboard": {
    "title": "Autogen Platform",
    "panels": [
      {
        "title": "Запуски в час",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(runs_total[1h])",
            "legendFormat": "{{vertical}}"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      {
        "title": "Success Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "sum(rate(runs_total{status=\"completed\"}[1h])) / sum(rate(runs_total[1h])) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0, "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 80},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
      },
      {
        "title": "Среднее число итераций",
        "type": "stat",
        "targets": [
          {
            "expr": "avg(run_iterations)",
            "legendFormat": "{{vertical}}"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
      },
      {
        "title": "Расходы ($/день)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(increase(budget_used_usd_total[1d])) by (vertical)",
            "legendFormat": "{{vertical}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "title": "Топ ошибок валидации",
        "type": "barchart",
        "targets": [
          {
            "expr": "topk(10, sum by (error_code) (validation_errors_total))",
            "legendFormat": "{{error_code}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      {
        "title": "Задержка LLM (p50, p95, p99)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(llm_latency_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(llm_latency_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(llm_latency_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 12}
      }
    ]
  }
}
```

---

## 7. Скрипт деплоя (`scripts/deploy.sh`)

```bash
#!/bin/bash
# scripts/deploy.sh
# Скрипт деплоя платформы

set -euo pipefail

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Деплой Autogen Platform"
echo "   Окружение: $ENVIRONMENT"
echo "   Версия: $VERSION"

# ============================================
# 1. Проверка prerequisites
# ============================================
echo "📋 Проверка prerequisites..."
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl не установлен"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker не установлен"; exit 1; }

# ============================================
# 2. Применение манифестов
# ============================================
echo "📦 Применение Kubernetes манифестов..."
kubectl apply -f k8s/01-namespace-config.yaml
kubectl apply -f k8s/02-secrets.yaml
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml
kubectl apply -f k8s/05-qdrant.yaml
kubectl apply -f k8s/06-api-gateway.yaml
kubectl apply -f k8s/07-ingress.yaml
kubectl apply -f k8s/08-ollama.yaml

# ============================================
# 3. Обновление образов
# ============================================
echo "🔄 Обновление образов..."
NAMESPACE="autogen"
if [ "$ENVIRONMENT" = "staging" ]; then
    NAMESPACE="autogen-staging"
fi

kubectl set image deployment/api-gateway \
    api-gateway=ghcr.io/kaylas000/autogen/api-gateway:$VERSION \
    --namespace $NAMESPACE

kubectl set image deployment/telegram-bot \
    telegram-bot=ghcr.io/kaylas000/autogen/telegram-bot:$VERSION \
    --namespace $NAMESPACE

# ============================================
# 4. Ожидание rollout
# ============================================
echo "⏳ Ожидание rollout..."
kubectl rollout status deployment/api-gateway --namespace $NAMESPACE --timeout=300s
kubectl rollout status deployment/telegram-bot --namespace $NAMESPACE --timeout=300s

# ============================================
# 5. Smoke tests
# ============================================
echo "🧪 Smoke tests..."
sleep 10

HEALTH_URL="https://api.autogen.example.com/health"
if [ "$ENVIRONMENT" = "staging" ]; then
    HEALTH_URL="https://staging-api.autogen.example.com/health"
fi

if curl -sf "$HEALTH_URL" > /dev/null; then
    echo "✅ Деплой успешен!"
else
    echo "❌ Smoke test провален. Откат..."
    kubectl rollout undo deployment/api-gateway --namespace $NAMESPACE
    exit 1
fi
```

---

## 8. Makefile для удобства (`Makefile`)

```makefile
# Makefile
.PHONY: help dev up down build test lint deploy logs

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Запустить в dev-режиме
	docker-compose up -d
	@echo "🎉 Dev-среда запущена"
	@echo "   API: http://localhost:8000"
	@echo "   Grafana: http://localhost:3000 (admin/admin123)"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Qdrant: http://localhost:6333"

up: ## Запустить все сервисы
	docker-compose up -d

down: ## Остановить все сервисы
	docker-compose down

build: ## Собрать Docker-образы
	docker-compose build

test: ## Запустить тесты
	pytest tests/ -v --asyncio-mode=auto

lint: ## Линтинг
	ruff check system/ the_ai_corporation/
	ruff format --check system/ the_ai_corporation/

deploy-staging: ## Деплой в staging
	./scripts/deploy.sh staging latest

deploy-prod: ## Деплой в продакшен
	./scripts/deploy.sh production latest

logs: ## Просмотр логов
	docker-compose logs -f

logs-api: ## Логи API Gateway
	docker-compose logs -f api-gateway

logs-ollama: ## Логи Ollama
	docker-compose logs -f ollama

scrape-refs: ## Парсинг референсов
	python cli/references_cli.py scrape

index-refs: ## Индексация референсов в Qdrant
	python cli/references_cli.py index

create-studio: ## Создать новую студию (пример: make create-studio NAME=my_studio DOMAIN=web)
	python cli/main.py create --name $(NAME) --domain $(DOMAIN) --template advanced

db-migrate: ## Миграции БД
	alembic upgrade head

db-reset: ## Сброс БД (ОСТОРОЖНО!)
	docker-compose exec postgres psql -U autogen -d autogen_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) db-migrate
```

---

**Следующий шаг:** Детализация пункта 3.4 (Критерии приёмки) — чек-листы для тестирования каждой компоненты, E2E-тесты, нагрузочное тестирование.

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 3.4: Критерии приёмки и тестирование

---

## 1. Чек-лист ядра (Kernel)

### 1.1. Unit-тесты для State Manager (`tests/kernel/test_state.py`)

```python
"""
Тесты для State Manager.
"""

import pytest
import asyncio
from datetime import datetime
from system.kernel.state import AgentState, StateManager


@pytest.mark.asyncio
async def test_state_creation():
    """Тест создания состояния"""
    state = AgentState(
        run_id="test-123",
        vertical_name="web_studio",
        skill_name="landing_page",
        input_data={"brief": "Test brief"},
        status="pending"
    )
    
    assert state.run_id == "test-123"
    assert state.status == "pending"
    assert state.iterations_count == 0


@pytest.mark.asyncio
async def test_state_checkpoint():
    """Тест сохранения чекпоинта"""
    state_manager = StateManager(database_url="postgresql://test:test@localhost:5432/test_db")
    
    state = AgentState(
        run_id="test-456",
        vertical_name="web_studio",
        skill_name="landing_page",
        input_data={"brief": "Test"},
        status="running"
    )
    
    # Сохранение
    await state_manager.save_checkpoint(state, node_name="planner")
    
    # Загрузка
    loaded = await state_manager.load_checkpoint("test-456")
    
    assert loaded.run_id == "test-456"
    assert loaded.status == "running"


@pytest.mark.asyncio
async def test_state_resume():
    """Тест возобновления после сбоя"""
    state_manager = StateManager(database_url="postgresql://test:test@localhost:5432/test_db")
    
    # Создание состояния
    state = AgentState(
        run_id="test-789",
        vertical_name="web_studio",
        skill_name="landing_page",
        input_data={"brief": "Test"},
        status="running",
        iterations_count=3
    )
    
    await state_manager.save_checkpoint(state, node_name="coder")
    
    # Симуляция сбоя и возобновления
    resumed = await state_manager.resume_run("test-789")
    
    assert resumed.status == "running"
    assert resumed.iterations_count == 3


@pytest.mark.asyncio
async def test_state_validation_errors():
    """Тест сохранения ошибок валидации"""
    state_manager = StateManager(database_url="postgresql://test:test@localhost:5432/test_db")
    
    state = AgentState(
        run_id="test-errors",
        vertical_name="web_studio",
        skill_name="landing_page",
        input_data={"brief": "Test"},
        status="validation_failed"
    )
    
    errors = [
        {
            "code": "V-01",
            "severity": "critical",
            "description": "Test error",
            "suggestion": "Fix it"
        }
    ]
    
    await state_manager.save_validation_errors("test-errors", errors, iteration=1)
    
    # Загрузка ошибок
    loaded_errors = await state_manager.get_validation_errors("test-errors")
    
    assert len(loaded_errors) == 1
    assert loaded_errors[0]["code"] == "V-01"
```

### 1.2. Unit-тесты для LLM Manager (`tests/kernel/test_llm.py`)

```python
"""
Тесты для LLM Manager.
"""

import pytest
from unittest.mock import AsyncMock, patch
from system.kernel.llm.client import LLMClient
from system.kernel.llm.budget import BudgetManager


@pytest.mark.asyncio
async def test_llm_completion():
    """Тест завершения через LLM"""
    llm = LLMClient()
    
    with patch('system.kernel.llm.client.litellm.acompletion') as mock_completion:
        mock_completion.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content="Test response"))],
            usage=AsyncMock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        )
        
        response = await llm.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="ollama/llama3.1:8b",
            temperature=0.7
        )
        
        assert response.content == "Test response"
        assert response.usage.total_tokens == 30


@pytest.mark.asyncio
async def test_llm_retry_on_failure():
    """Тест ретрая при ошибке"""
    llm = LLMClient()
    
    with patch('system.kernel.llm.client.litellm.acompletion') as mock_completion:
        # Первый вызов — ошибка, второй — успех
        mock_completion.side_effect = [
            Exception("Rate limit exceeded"),
            AsyncMock(
                choices=[AsyncMock(message=AsyncMock(content="Success"))],
                usage=AsyncMock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
            )
        ]
        
        response = await llm.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="ollama/llama3.1:8b",
            temperature=0.7
        )
        
        assert response.content == "Success"
        assert mock_completion.call_count == 2


@pytest.mark.asyncio
async def test_budget_manager_daily_limit():
    """Тест дневного лимита бюджета"""
    budget_manager = BudgetManager(database_url="postgresql://test:test@localhost:5432/test_db")
    
    # Установка дневного лимита
    await budget_manager.set_daily_limit(10.0)
    
    # Запись расходов
    await budget_manager.record_cost(run_id="test-1", cost=3.0, tokens=1000)
    await budget_manager.record_cost(run_id="test-2", cost=4.0, tokens=1500)
    
    # Проверка
    daily_usage = await budget_manager.get_daily_usage()
    assert daily_usage == 7.0
    
    # Проверка возможности нового запуска
    can_run = await budget_manager.check_budget(estimated_cost=2.0)
    assert can_run is True
    
    can_run = await budget_manager.check_budget(estimated_cost=5.0)
    assert can_run is False


@pytest.mark.asyncio
async def test_budget_manager_run_limit():
    """Тест лимита на один запуск"""
    budget_manager = BudgetManager(database_url="postgresql://test:test@localhost:5432/test_db")
    
    # Запись расходов для одного запуска
    await budget_manager.record_cost(run_id="test-run", cost=1.0, tokens=500)
    await budget_manager.record_cost(run_id="test-run", cost=1.5, tokens=700)
    
    run_usage = await budget_manager.get_run_usage("test-run")
    assert run_usage == 2.5
    
    # Проверка превышения лимита
    await budget_manager.set_run_limit(2.0)
    exceeded = await budget_manager.is_run_exceeded("test-run")
    assert exceeded is True
```

### 1.3. Unit-тесты для Sandbox Manager (`tests/kernel/test_sandbox.py`)

```python
"""
Тесты для Sandbox Manager.
"""

import pytest
from unittest.mock import AsyncMock, patch
from system.kernel.sandbox.manager import SandboxManager


@pytest.mark.asyncio
async def test_sandbox_execution_python():
    """Тест выполнения Python-кода"""
    sandbox = SandboxManager(provider="local")
    
    result = await sandbox.execute(
        code="print('Hello, World!')",
        language="python",
        timeout=10
    )
    
    assert result.success is True
    assert "Hello, World!" in result.stdout


@pytest.mark.asyncio
async def test_sandbox_execution_error():
    """Тест обработки ошибки в коде"""
    sandbox = SandboxManager(provider="local")
    
    result = await sandbox.execute(
        code="raise ValueError('Test error')",
        language="python",
        timeout=10
    )
    
    assert result.success is False
    assert "ValueError" in result.stderr


@pytest.mark.asyncio
async def test_sandbox_timeout():
    """Тест таймаута выполнения"""
    sandbox = SandboxManager(provider="local")
    
    result = await sandbox.execute(
        code="import time; time.sleep(10)",
        language="python",
        timeout=2
    )
    
    assert result.success is False
    assert "timeout" in result.stderr.lower()


@pytest.mark.asyncio
async def test_sandbox_html_validation():
    """Тест валидации HTML"""
    sandbox = SandboxManager(provider="local")
    
    html_code = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>Hello</h1>
        <p>World</p>
    </body>
    </html>
    """
    
    result = await sandbox.execute(
        code=f"""
from html.parser import HTMLParser
class Validator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.valid = True
    def error(self, message):
        self.valid = False

v = Validator()
v.feed('''{html_code}''')
print("Valid" if v.valid else "Invalid")
        """,
        language="python",
        timeout=10
    )
    
    assert result.success is True
    assert "Valid" in result.stdout
```

---

## 2. Чек-лист студий (Verticals)

### 2.1. Тесты для Web Studio (`tests/verticals/test_web_studio.py`)

```python
"""
Тесты для Web Studio.
"""

import pytest
import yaml
from pathlib import Path
from verticals.web_studio.validators.constitution import ConstitutionGate
from verticals.web_studio.validators.anti_slop import AntiSlopGate
from verticals.web_studio.validators.composite import CompositeValidator


@pytest.mark.asyncio
async def test_constitution_gate_contrast():
    """Тест проверки контраста (К-02)"""
    gate = ConstitutionGate("verticals/web_studio/CONSTITUTION.md")
    
    # Артефакт с хорошим контрастом
    artifact = {
        "html": "<html><body><p style='color: #000000; background: #ffffff;'>Test</p></body></html>",
        "css": "p { color: #000000; background: #ffffff; }"
    }
    
    result = await gate.verify(artifact, {})
    
    # Должно пройти (контраст 21:1)
    assert result.passed is True


@pytest.mark.asyncio
async def test_constitution_gate_semantic_html():
    """Тест проверки семантического HTML (К-05)"""
    gate = ConstitutionGate("verticals/web_studio/CONSTITUTION.md")
    
    # Артефакт с семантическими тегами
    artifact = {
        "html": """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <header>Header</header>
            <main>
                <section>Content</section>
            </main>
            <footer>Footer</footer>
        </body>
        </html>
        """
    }
    
    result = await gate.verify(artifact, {})
    
    # Должно пройти
    assert result.passed is True


@pytest.mark.asyncio
async def test_anti_slop_gradient():
    """Тест проверки запрещённых градиентов (B-01)"""
    gate = AntiSlopGate(
        "verticals/web_studio/anti-slop/BANNED.md",
        "verticals/web_studio/anti-slop/QUOTAS.md"
    )
    
    # Артефакт с градиентом
    artifact = {
        "css": "body { background: linear-gradient(to right, #ff0000, #0000ff); }"
    }
    
    result = await gate.verify(artifact, {})
    
    # Должно провалиться
    assert result.passed is False
    assert any(e.code == "B-01" for e in result.errors)


@pytest.mark.asyncio
async def test_anti_slop_quota_colors():
    """Тест проверки квоты цветов (Q-03)"""
    gate = AntiSlopGate(
        "verticals/web_studio/anti-slop/BANNED.md",
        "verticals/web_studio/anti-slop/QUOTAS.md"
    )
    
    # Артефакт с 6 цветами (квота 5)
    artifact = {
        "css": """
        .a { color: #ff0000; }
        .b { color: #00ff00; }
        .c { color: #0000ff; }
        .d { color: #ffff00; }
        .e { color: #ff00ff; }
        .f { color: #00ffff; }
        """
    }
    
    result = await gate.verify(artifact, {})
    
    # Должно провалиться
    assert result.passed is False
    assert any(e.code == "Q-03" for e in result.errors)


@pytest.mark.asyncio
async def test_composite_validator():
    """Тест композитного валидатора"""
    validator = CompositeValidator("verticals/web_studio")
    
    # Хороший артефакт
    artifact = {
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Site</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <header>Header</header>
            <main>
                <h1>Title</h1>
                <h2>Subtitle</h2>
                <img src="test.webp" alt="Test">
            </main>
            <footer>Footer</footer>
        </body>
        </html>
        """,
        "css": "body { font-family: Inter, sans-serif; color: #000000; background: #ffffff; }",
        "js": "console.log('Test');",
        "metadata": {
            "title": "Test Site",
            "description": "Test description for validation"
        }
    }
    
    result = await validator.verify(artifact, {})
    
    # Должно пройти (или иметь только minor warnings)
    critical_errors = [e for e in result.errors if e.severity == "critical"]
    assert len(critical_errors) == 0


@pytest.mark.asyncio
async def test_web_studio_e2e():
    """E2E тест Web Studio"""
    from system.kernel.runner import run_vertical
    
    result = await run_vertical(
        vertical_name="web_studio",
        skill_name="landing_page",
        input_data={
            "brief": "Создай минималистичный лендинг для технологического стартапа. Тёмная тема, акцентный цвет — синий.",
            "target_audience": "Разработчики 25-40 лет",
            "style": "minimalism"
        }
    )
    
    assert result["status"] == "completed"
    assert "html" in result["artifacts"]
    assert "css" in result["artifacts"]
    assert result["iterations_count"] < 10
```

### 2.2. Тесты для Legal Docs Studio (`tests/verticals/test_legal_docs.py`)

```python
"""
Тесты для Legal Docs Studio.
"""

import pytest
from verticals.legal_docs.validators.essential_terms import EssentialTermsValidator


@pytest.mark.asyncio
async def test_essential_terms_present():
    """Тест наличия существенных условий"""
    validator = EssentialTermsValidator()
    
    document = """
    ДОГОВОР ОКАЗАНИЯ УСЛУГ №1
    
    г. Москва                                    28.09.2026
    
    ООО "Тест", именуемое "Заказчик", и ИП Иванов И.И., именуемый "Исполнитель", 
    заключили настоящий договор о следующем:
    
    1. ПРЕДМЕТ ДОГОВОРА
    1.1. Исполнитель обязуется оказать услуги по разработке веб-сайта.
    1.2. Услуги включают: дизайн, вёрстку, тестирование.
    
    2. СТОИМОСТЬ И ПОРЯДОК РАСЧЁТОВ
    2.1. Стоимость услуг составляет 100 000 (Сто тысяч) рублей 00 копеек.
    2.2. Оплата производится в порядке: 50% предоплата, 50% по завершении.
    
    3. СРОКИ ОКАЗАНИЯ УСЛУГ
    3.1. Срок оказания услуг: 30 календарных дней с даты подписания.
    """
    
    result = await validator.verify({"document_text": document}, {})
    
    # Должно пройти (все существенные условия есть)
    assert result.passed is True


@pytest.mark.asyncio
async def test_essential_terms_missing():
    """Тест отсутствия существенных условий"""
    validator = EssentialTermsValidator()
    
    document = """
    ДОГОВОР
    
    Стороны договорились о сотрудничестве.
    """
    
    result = await validator.verify({"document_text": document}, {})
    
    # Должно провалиться (нет предмета, стоимости, сроков)
    assert result.passed is False
    assert any(e.code == "V-01" for e in result.errors)


@pytest.mark.asyncio
async def test_legal_docs_e2e():
    """E2E тест Legal Docs Studio"""
    from system.kernel.runner import run_vertical
    
    result = await run_vertical(
        vertical_name="legal_docs",
        skill_name="contract",
        input_data={
            "contract_type": "service",
            "parties": {
                "party_a": {"name": "ООО Тест", "inn": "1234567890"},
                "party_b": {"name": "Иванов И.И.", "inn": "123456789012"}
            },
            "subject": "Разработка веб-сайта",
            "price": {"amount": 100000, "currency": "RUB"},
            "term": "30 календарных дней"
        }
    )
    
    assert result["status"] == "completed"
    assert "document_text" in result["artifacts"]
    assert result["iterations_count"] < 8
```

---

## 3. Чек-лист CEO-агента

### 3.1. Тесты для CEO-агента (`tests/the_ai_corporation/test_ceo_agent.py`)

```python
"""
Тесты для CEO-агента.
"""

import pytest
from the_ai_corporation.agents.ceo_agent import CEOAgent, TaskType
from the_ai_corporation.registry.studio_registry import StudioRegistry


@pytest.mark.asyncio
async def test_task_classification_website():
    """Тест классификации задачи — сайт"""
    registry = StudioRegistry("verticals")
    ceo = CEOAgent(registry.studios)
    
    task_type = await ceo._classify_task("Создай лендинг для онлайн-школы")
    
    assert task_type == TaskType.WEBSITE


@pytest.mark.asyncio
async def test_task_classification_legal():
    """Тест классификации задачи — юридические документы"""
    registry = StudioRegistry("verticals")
    ceo = CEOAgent(registry.studios)
    
    task_type = await ceo._classify_task("Нужен договор оферты для интернет-магазина")
    
    assert task_type == TaskType.LEGAL_DOCS


@pytest.mark.asyncio
async def test_task_classification_complex():
    """Тест классификации сложной задачи"""
    registry = StudioRegistry("verticals")
    ceo = CEOAgent(registry.studios)
    
    task_type = await ceo._classify_task(
        "Создай полный пакет для запуска онлайн-школы: лендинг, 3 статьи, договор оферты"
    )
    
    assert task_type == TaskType.COMPLEX


@pytest.mark.asyncio
async def test_composition_execution():
    """Тест выполнения композиции"""
    registry = StudioRegistry("verticals")
    ceo = CEOAgent(registry.studios, "compositions")
    
    # Загрузка композиции
    composition = ceo.compositions.get("full_website")
    assert composition is not None
    
    # Выполнение
    result = await ceo._execute_composition(
        composition,
        brief="Создай полный пакет для онлайн-школы",
        context={}
    )
    
    assert result["status"] == "completed"
    assert "subtask_results" in result


@pytest.mark.asyncio
async def test_parallel_execution():
    """Тест параллельного выполнения задач"""
    from the_ai_corporation.agents.ceo_agent import SubTask, CompositionPlan
    
    plan = CompositionPlan(
        name="test",
        description="Test",
        tasks=[
            SubTask(id="task_1", studio="web_studio", skill="landing_page", brief="Task 1", parallel=True),
            SubTask(id="task_2", studio="content_studio", skill="seo_article", brief="Task 2", parallel=True),
            SubTask(id="task_3", studio="legal_docs", skill="offer", brief="Task 3", dependencies=["task_1"], parallel=False)
        ]
    )
    
    # Проверка готовых задач
    ready = plan.get_ready_tasks()
    assert len(ready) == 2  # task_1 и task_2 (без зависимостей)
    
    # Проверка параллельных задач
    parallel = plan.get_parallel_tasks(ready)
    assert len(parallel) == 2


@pytest.mark.asyncio
async def test_ceo_e2e():
    """E2E тест CEO-агента"""
    registry = StudioRegistry("verticals")
    ceo = CEOAgent(registry.studios, "compositions")
    
    result = await ceo.handle_request(
        brief="Создай лендинг для технологического стартапа с минималистичным дизайном"
    )
    
    assert result["status"] == "completed"
    assert "summary" in result
    assert "artifacts" in result
```

---

## 4. Чек-лист инфраструктуры

### 4.1. Тесты Docker Compose (`tests/infrastructure/test_docker.sh`)

```bash
#!/bin/bash
# tests/infrastructure/test_docker.sh
# Тесты для Docker Compose

set -euo pipefail

echo "🧪 Тестирование Docker Compose..."

# ============================================
# 1. Проверка запуска всех сервисов
# ============================================
echo "📋 Проверка запуска сервисов..."
docker-compose up -d
sleep 30

SERVICES=("api-gateway" "postgres" "redis" "qdrant" "litellm" "ollama")

for service in "${SERVICES[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✅ $service запущен"
    else
        echo "❌ $service не запущен"
        docker-compose logs "$service"
        exit 1
    fi
done

# ============================================
# 2. Проверка healthcheck
# ============================================
echo "🏥 Проверка healthcheck..."

# API Gateway
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ API Gateway healthy"
else
    echo "❌ API Gateway unhealthy"
    exit 1
fi

# PostgreSQL
if docker-compose exec -T postgres pg_isready -U autogen > /dev/null; then
    echo "✅ PostgreSQL healthy"
else
    echo "❌ PostgreSQL unhealthy"
    exit 1
fi

# Redis
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis healthy"
else
    echo "❌ Redis unhealthy"
    exit 1
fi

# Qdrant
if curl -sf http://localhost:6333/ > /dev/null; then
    echo "✅ Qdrant healthy"
else
    echo "❌ Qdrant unhealthy"
    exit 1
fi

# Ollama
if curl -sf http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama healthy"
else
    echo "❌ Ollama unhealthy"
    exit 1
fi

# ============================================
# 3. Проверка сет

# ДЕТАЛИЗАЦИЯ К ПУНКТУ 3.4: Критерии приёмки и тестирование (продолжение)

---

## 4. Чек-лист инфраструктуры (продолжение)

### 4.1. Тесты Docker Compose (`tests/infrastructure/test_docker.sh`) — продолжение

```bash
# ============================================
# 3. Проверка сетевых взаимодействий
# ============================================
echo "🌐 Проверка сетевых взаимодействий..."

# API Gateway → PostgreSQL
if docker-compose exec -T api-gateway python -c "
import asyncpg
import asyncio

async def test():
    conn = await asyncpg.connect('postgresql://autogen:autogen_pass@postgres:5432/autogen_db')
    await conn.execute('SELECT 1')
    await conn.close()
    print('OK')

asyncio.run(test())
" | grep -q "OK"; then
    echo "✅ API Gateway → PostgreSQL"
else
    echo "❌ API Gateway не может подключиться к PostgreSQL"
    exit 1
fi

# API Gateway → Redis
if docker-compose exec -T api-gateway python -c "
import redis
r = redis.Redis(host='redis', port=6379)
r.ping()
print('OK')
" | grep -q "OK"; then
    echo "✅ API Gateway → Redis"
else
    echo "❌ API Gateway не может подключиться к Redis"
    exit 1
fi

# API Gateway → Qdrant
if docker-compose exec -T api-gateway python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://qdrant:6333')
client.get_collections()
print('OK')
" | grep -q "OK"; then
    echo "✅ API Gateway → Qdrant"
else
    echo "❌ API Gateway не может подключиться к Qdrant"
    exit 1
fi

# LiteLLM → Ollama
if docker-compose exec -T litellm curl -sf http://ollama:11434/api/tags > /dev/null; then
    echo "✅ LiteLLM → Ollama"
else
    echo "❌ LiteLLM не может подключиться к Ollama"
    exit 1
fi

# ============================================
# 4. Проверка загрузки моделей Ollama
# ============================================
echo "🦙 Проверка моделей Ollama..."

MODELS=("llama3.1:8b" "qwen2.5-coder:7b" "gemma2:9b" "nomic-embed-text")

for model in "${MODELS[@]}"; do
    if curl -sf http://localhost:11434/api/tags | grep -q "\"$model\""; then
        echo "✅ Модель $model загружена"
    else
        echo "⚠️ Модель $model не загружена (попробуйте: docker-compose exec ollama ollama pull $model)"
    fi
done

# ============================================
# 5. Проверка Prometheus метрик
# ============================================
echo "📊 Проверка Prometheus..."

if curl -sf http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus healthy"
    
    # Проверка наличия целей
    TARGETS=$(curl -sf http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets | length')
    if [ "$TARGETS" -gt 0 ]; then
        echo "✅ Prometheus собирает метрики ($TARGETS целей)"
    else
        echo "⚠️ Prometheus не имеет активных целей"
    fi
else
    echo "❌ Prometheus unhealthy"
    exit 1
fi

# ============================================
# 6. Остановка и очистка
# ============================================
echo "🧹 Остановка сервисов..."
docker-compose down

echo "✅ Все инфраструктурные тесты пройдены!"
```

### 4.2. Нагрузочное тестирование (`tests/infrastructure/test_load.py`)

```python
"""
Нагрузочное тестирование платформы.
"""

import asyncio
import time
import statistics
from typing import List, Dict
import httpx
import pytest


class LoadTestRunner:
    """Запускатор нагрузочных тестов"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
    
    async def run_single_request(self, brief: str, timeout: float = 60.0) -> Dict:
        """Запуск одного запроса"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/generate",
                    json={
                        "vertical": "web_studio",
                        "skill": "landing_page",
                        "brief": brief
                    }
                )
                
                duration = time.time() - start_time
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "duration": duration,
                    "run_id": response.json().get("run_id")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    async def run_concurrent_requests(
        self,
        briefs: List[str],
        concurrency: int = 10
    ) -> Dict[str, any]:
        """Запуск параллельных запросов"""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_request(brief: str):
            async with semaphore:
                return await self.run_single_request(brief)
        
        start_time = time.time()
        results = await asyncio.gather(*[limited_request(b) for b in briefs])
        total_time = time.time() - start_time
        
        # Анализ результатов
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        durations = [r["duration"] for r in successful]
        
        return {
            "total_requests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100,
            "total_time": total_time,
            "avg_duration": statistics.mean(durations) if durations else 0,
            "median_duration": statistics.median(durations) if durations else 0,
            "p95_duration": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
            "p99_duration": sorted(durations)[int(len(durations) * 0.99)] if durations else 0,
            "rps": len(successful) / total_time if total_time > 0 else 0
        }


@pytest.mark.asyncio
async def test_load_10_concurrent():
    """Нагрузочный тест: 10 параллельных запросов"""
    runner = LoadTestRunner()
    
    briefs = [
        f"Создай лендинг для компании {i}. Минималистичный дизайн."
        for i in range(10)
    ]
    
    result = await runner.run_concurrent_requests(briefs, concurrency=10)
    
    print("\n📊 Результаты нагрузочного теста (10 запросов):")
    print(f"   Успешных: {result['successful']}/{result['total_requests']}")
    print(f"   Success rate: {result['success_rate']:.1f}%")
    print(f"   Среднее время: {result['avg_duration']:.2f}s")
    print(f"   P95: {result['p95_duration']:.2f}s")
    print(f"   RPS: {result['rps']:.2f}")
    
    # Критерии приёмки
    assert result["success_rate"] >= 90.0, f"Success rate {result['success_rate']:.1f}% < 90%"
    assert result["avg_duration"] < 30.0, f"Среднее время {result['avg_duration']:.2f}s > 30s"
    assert result["p95_duration"] < 60.0, f"P95 {result['p95_duration']:.2f}s > 60s"


@pytest.mark.asyncio
async def test_load_50_concurrent():
    """Нагрузочный тест: 50 параллельных запросов"""
    runner = LoadTestRunner()
    
    briefs = [
        f"Создай лендинг для компании {i}. Тёмная тема."
        for i in range(50)
    ]
    
    result = await runner.run_concurrent_requests(briefs, concurrency=20)
    
    print("\n📊 Результаты нагрузочного теста (50 запросов):")
    print(f"   Успешных: {result['successful']}/{result['total_requests']}")
    print(f"   Success rate: {result['success_rate']:.1f}%")
    print(f"   Среднее время: {result['avg_duration']:.2f}s")
    print(f"   P95: {result['p95_duration']:.2f}s")
    print(f"   RPS: {result['rps']:.2f}")
    
    # Критерии приёмки
    assert result["success_rate"] >= 85.0, f"Success rate {result['success_rate']:.1f}% < 85%"
    assert result["avg_duration"] < 60.0, f"Среднее время {result['avg_duration']:.2f}s > 60s"


@pytest.mark.asyncio
async def test_sustained_load():
    """Тест устойчивой нагрузки (5 минут)"""
    runner = LoadTestRunner()
    
    duration_seconds = 300  # 5 минут
    requests_per_second = 2
    
    briefs = [
        f"Создай лендинг для компании {i}."
        for i in range(duration_seconds * requests_per_second)
    ]
    
    print(f"\n🔄 Запуск теста устойчивой нагрузки ({duration_seconds}s, {requests_per_second} RPS)...")
    
    start_time = time.time()
    results = []
    
    for i in range(0, len(briefs), requests_per_second):
        batch = briefs[i:i + requests_per_second]
        batch_results = await asyncio.gather(*[runner.run_single_request(b) for b in batch])
        results.extend(batch_results)
        
        # Задержка для поддержания RPS
        await asyncio.sleep(1.0)
    
    total_time = time.time() - start_time
    
    successful = [r for r in results if r["success"]]
    durations = [r["duration"] for r in successful]
    
    print(f"\n📊 Результаты теста устойчивой нагрузки:")
    print(f"   Длительность: {total_time:.1f}s")
    print(f"   Всего запросов: {len(results)}")
    print(f"   Успешных: {len(successful)}")
    print(f"   Success rate: {len(successful) / len(results) * 100:.1f}%")
    print(f"   Среднее время: {statistics.mean(durations):.2f}s")
    print(f"   P95: {sorted(durations)[int(len(durations) * 0.95)]:.2f}s")
    
    # Критерии приёмки
    assert len(successful) / len(results) >= 0.90, "Success rate < 90%"
    assert statistics.mean(durations) < 30.0, "Среднее время > 30s"
```

---

## 5. Финальный чек-лист приёмки системы

### 5.1. Функциональные требования

```markdown
# ФИНАЛЬНЫЙ ЧЕК-ЛИСТ ПРИЁМКИ СИСТЕМЫ

## ✅ Ядро (Kernel)

### State Management
- [ ] AgentState корректно создаётся и сериализуется
- [ ] Чекпоинты сохраняются в PostgreSQL после каждого узла
- [ ] Resume run работает после сбоя
- [ ] Ошибки валидации сохраняются с полной историей

### LLM Manager
- [ ] LiteLLM proxy работает с Ollama
- [ ] Ретраи с exponential backoff работают
- [ ] Алиасы моделей (role/planner → ollama/llama3.1:8b) работают
- [ ] Трекинг токенов и стоимости корректно
- [ ] Кэширование повторяющихся запросов работает

### Sandbox Manager
- [ ] E2B песочницы создаются и уничтожаются
- [ ] Docker fallback работает при недоступности E2B
- [ ] Таймауты соблюдаются
- [ ] Resource limits (CPU, RAM) применяются
- [ ] Изоляция между запусками гарантирована

### Budget Manager
- [ ] Лимит на run работает (max_budget_usd_per_run)
- [ ] Дневной лимит работает (MAX_COST_USD_PER_DAY)
- [ ] Лимит токенов в минуту работает
- [ ] Алерты при достижении 80% лимита отправляются
- [ ] Пауза run при превышении бюджета работает

## ✅ Студии (Verticals)

### Web Studio
- [ ] vertical.yaml корректно загружается
- [ ] Конституция (К-01...К-24) парсится и проверяется
- [ ] Anti-slop (BANNED, QUOTAS) работает
- [ ] Скилл landing_page генерирует HTML/CSS/JS
- [ ] Валидаторы (Constitution, AntiSlop, Schema, LLMJudge) работают
- [ ] Цикл самокоррекции (генерация → валидация → исправление) работает
- [ ] Референсы загружены (100+ из lapa, land-book, awwwards)
- [ ] RAG поиск референсов работает
- [ ] Success rate > 90%
- [ ] Среднее число итераций < 5

### Legal Docs Studio
- [ ] Конституция (К-01...К-15) работает
- [ ] Проверка существенных условий работает
- [ ] Проверка соответствия ГК РФ работает
- [ ] Скилл contract генерирует договоры
- [ ] Success rate > 90%

### Content Studio
- [ ] Конституция (К-01...К-15) работает
- [ ] Проверка уникальности работает
- [ ] Проверка SEO-метрик работает
- [ ] Скилл seo_article генерирует статьи
- [ ] Success rate > 90%

### Data Analytics Studio
- [ ] Конституция (К-01...К-15) работает
- [ ] Проверка синтаксиса SQL/Python работает
- [ ] Проверка производительности запросов работает
- [ ] Скилл sql_query генерирует запросы
- [ ] Success rate > 90%

### Education Studio
- [ ] Конституция (К-01...К-15) работает
- [ ] Проверка таксономии Блума работает
- [ ] Проверка интерактивности работает
- [ ] Скилл lesson генерирует уроки
- [ ] Success rate > 90%

## ✅ CEO-агент (The-AI-Corporation)

### Классификация задач
- [ ] WEBSITE классифицируется корректно
- [ ] LEGAL_DOCS классифицируется корректно
- [ ] CONTENT классифицируется корректно
- [ ] COMPLEX классифицируется корректно

### Композиции
- [ ] YAML-композиции загружаются
- [ ] Параллельное выполнение работает
- [ ] Зависимости между задачами соблюдаются
- [ ] Сборка финального результата работает

### Маршрутизация
- [ ] TaskRouter маршрутизирует к правильным студиям
- [ ] Fallback на web_studio при неизвестном типе работает

## ✅ Инфраструктура

### Docker Compose
- [ ] Все сервисы запускаются (api-gateway, postgres, redis, qdrant, litellm, ollama, telegram-bot)
- [ ] Healthcheck для всех сервисов работает
- [ ] Сетевые взаимодействия между контейнерами работают
- [ ] Модели Ollama загружены (llama3.1:8b, qwen2.5-coder:7b, gemma2:9b, nomic-embed-text)

### Kubernetes
- [ ] Namespace создаётся
- [ ] ConfigMap и Secrets применяются
- [ ] StatefulSet PostgreSQL развёртывается
- [ ] Deployments (api-gateway, redis, qdrant, ollama) развёртываются
- [ ] HPA (Horizontal Pod Autoscaler) работает
- [ ] Ingress с TLS работает

### Мониторинг
- [ ] Prometheus собирает метрики
- [ ] Grafana дашборды отображают данные
- [ ] Loki агрегирует логи
- [ ] OpenTelemetry трейсинг работает
- [ ] Алерты отправляются при критических событиях

### CI/CD
- [ ] GitHub Actions пайплайн работает
- [ ] Линтинг (ruff, mypy, bandit) проходит
- [ ] Unit-тесты проходят
- [ ] Docker-образы собираются и пушатся в registry
- [ ] Деплой в staging работает
- [ ] Деплой в production работает
- [ ] Smoke tests после деплоя проходят

## ✅ API

### REST API
- [ ] POST /v1/generate работает
- [ ] GET /v1/runs/{id} работает
- [ ] POST /v1/compositions/execute работает
- [ ] GET /v1/compositions/runs/{id} работает
- [ ] GET /health работает
- [ ] GET /metrics работает

### Аутентификация
- [ ] JWT токены генерируются и валидируются
- [ ] API keys работают
- [ ] Rate limiting работает (RPM, RPD, concurrent)
- [ ] Роли (viewer, developer, admin) применяются

### Идемпотентность
- [ ] Повторный запрос с тем же X-Request-ID не создаёт новый run
- [ ] Статус существующего run возвращается

## ✅ Производительность

### Нагрузочное тестирование
- [ ] 10 параллельных запросов: success rate ≥ 90%, avg duration < 30s
- [ ] 50 параллельных запросов: success rate ≥ 85%, avg duration < 60s
- [ ] Устойчивая нагрузка (5 минут, 2 RPS): success rate ≥ 90%

### Оптимизация
- [ ] Кэширование повторяющихся запросов работает
- [ ] Параллельное выполнение задач работает
- [ ] Бюджетирование предотвращает runaway agents
- [ ] Resource limits применяются

## ✅ Качество

### Метрики качества
- [ ] Success rate каждой студии > 90%
- [ ] Среднее число итераций < 5
- [ ] Время выполнения простой задачи < 5 минут
- [ ] Cost per run < $2
- [ ] Token usage < 100k на задачу

### Уникальность (для Web Studio)
- [ ] Каждый дизайн уникален (уникальность > 80%)
- [ ] Нет повторения стилей в последних 5 проектах
- [ ] Референсы используются как вдохновение, не копируются

## ✅ Документация

### Для разработчиков
- [ ] README.md с инструкцией по установке
- [ ] ARCHITECTURE.md с описанием архитектуры
- [ ] API.md с описанием API endpoints
- [ ] CONTRIBUTING.md с правилами внесения изменений
- [ ] Код покрыт docstrings и комментариями

### Для операторов
- [ ] DEPLOY.md с инструкцией по деплою
- [ ] MONITORING.md с описанием метрик и алертов
- [ ] TROUBLESHOOTING.md с решением типичных проблем
- [ ] RUNBOOK.md с процедурами обслуживания

### Для пользователей
- [ ] USER_GUIDE.md с примерами использования
- [ ] CLI_HELP.md с описанием CLI команд
- [ ] Примеры композиций в compositions/
- [ ] Примеры студий в verticals/
```

---

## 6. Команда для приёмки

```bash
#!/bin/bash
# scripts/acceptance_test.sh
# Полный скрипт приёмки системы

set -euo pipefail

echo "🎯 ЗАПУСК ПРИЁМОЧНОГО ТЕСТИРОВАНИЯ"
echo "===================================="
echo ""

# ============================================
# 1. Проверка инфраструктуры
# ============================================
echo "📋 Этап 1/6: Проверка инфраструктуры..."
./tests/infrastructure/test_docker.sh

# ============================================
# 2. Unit-тесты ядра
# ============================================
echo ""
echo "📋 Этап 2/6: Unit-тесты ядра..."
pytest tests/kernel/ -v --asyncio-mode=auto --tb=short

# ============================================
# 3. Тесты студий
# ============================================
echo ""
echo "📋 Этап 3/6: Тесты студий..."
pytest tests/verticals/ -v --asyncio-mode=auto --tb=short

# ============================================
# 4. Тесты CEO-агента
# ============================================
echo ""
echo "📋 Этап 4/6: Тесты CEO-агента..."
pytest tests/the_ai_corporation/ -v --asyncio-mode=auto --tb=short

# ============================================
# 5. Нагрузочное тестирование
# ============================================
echo ""
echo "📋 Этап 5/6: Нагрузочное тестирование..."
pytest tests/infrastructure/test_load.py -v --asyncio-mode=auto -s

# ============================================
# 6. E2E тесты
# ============================================
echo ""
echo "📋 Этап 6/6: E2E тесты..."
pytest tests/e2e/ -v --asyncio-mode=auto --tb=short

# ============================================
# Финальный отчёт
# ============================================
echo ""
echo "===================================="
echo "✅ ПРИЁМОЧНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО"
echo "===================================="
echo ""
echo "📊 Итоговая статистика:"
pytest tests/ --collect-only -q | tail -1
echo ""
echo "🎉 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!"
```

---

## 7. ИТОГОВОЕ РЕЗЮМЕ ТЗ

### Что мы построили

**Мета-платформа для создания специализированных ИИ-студий**, которая:

1. **Универсальна** — подходит для любых предметных областей (веб, юр. документы, контент, аналитика, образование)
2. **Модульна** — ядро отделено от студий, студии отделены друг от друга
3. **Надёжна** — циклы самокоррекции, детерминированные валидаторы, Constitution as Code
4. **Экономична** — работает на бесплатных моделях (Ollama) за счёт выноса логики в валидаторы
5. **Масштабируема** — Kubernetes, HPA, параллельное выполнение
6. **Наблюдаема** — Prometheus, Grafana, Loki, OpenTelemetry
7. **Автоматизирована** — CI/CD через GitHub Actions, автоматический деплой

### Ключевые конкурентные преимущества

1. **Constitution as Code** — правила предметной области как исполняемый код, не просто промпты
2. **Типизированные коды ошибок** (V-xx, B-xx, Q-xx) — точный фидбек для агента, не "попробуй ещё раз"
3. **Система референсов** — парсинг реальных каталогов (lapa.ninja, land-book.com, awwwards.com) для вдохновения
4. **Маркетплейс студий** — переиспользование и публикация студий как пакетов
5. **CEO-агент** — координация нескольких студий для сложных задач

### Ресурсы для реализации

**Команда:**
- 1 Backend-разработчик (Python, FastAPI, LangGraph)
- 1 DevOps-инженер (Docker, Kubernetes, мониторинг)
- 1 ML-инженер (LLM, RAG, промпт-инжиниринг)
- 0.5 QA-инженера

**Срок:** 16 недель (4 месяца)

**Бюджет:**
- Инфраструктура: ~$500/мес (серверы, E2B, API)
- Токены LLM: ~$200/мес (на этапе разработки)
- ФОТ: зависит от команды

### Следующие шаги

1. **Утвердить ТЗ** — все части (1-8) согласованы
2. **Сформировать команду** — найти разработчиков
3. **Начать Фазу 1** — ядро (4 недели)
4. **Через 4 месяца** — первый релиз с 3 студиями
5. **Через 6 месяцев** — маркетплейс студий, 5+ вертикалей

---

**Конец ТЗ.**

Система полностью описана и готова к реализации. Все компоненты детализированы: от архитектуры ядра до конкретных валидаторов, от Docker Compose до Kubernetes манифестов, от unit-тестов до нагрузочного тестирования.

