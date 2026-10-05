# Конституция Web Studio (К-01 … К-24)

Каждое правило проверяемо; нарушение порождает код V-xx (номер = номер правила).
Правила с маркером `check_regex:` проверяются автоматически generic-валидатором.

## К-01. Валидный HTML5
Артефакт — полный HTML-документ: `<!DOCTYPE html>`, `<html lang=...>`, `<head>`, `<body>`.
check_regex: (?s)^(?!.*<!doctype\s+html).*$, message: Отсутствует <!DOCTYPE html>, severity: critical

## К-02. Семантическая разметка
Используются семантические теги header/main/section/footer вместо div-заглушек.
check_regex: <(div|span)[^>]*class="[^"]*(header|footer)[^"]*"(?![\s\S]*<(header|footer)\b), message: Блоки header/footer свёрстаны div-ами вместо семантических тегов, severity: major

## К-03. Обязательные секции лендинга
Страница содержит hero, блок преимуществ (features) и финальный CTA.

## К-04. Уникальный контент
Запрещён placeholder-текст.
check_regex: lorem\s+ipsum, message: Обнаружен lorem ipsum, severity: critical

## К-05. Alt у изображений
У каждого `<img>` есть непустой alt.
check_regex: <img(?![^>]*alt="[^"]+")[^>]*>, message: Изображение без alt, severity: major

## К-06. Meta description и title
В `<head>` присутствуют title и meta[name=description].

## К-07. Один CTA на экран
Финальных call-to-action кнопок не больше трёх на первый экран (проверяется квотой Q-01).

## К-08. Мобильная адаптивность
Есть viewport-meta и media query или flex/grid раскладка.
check_regex: (?s)^(?!.*name="viewport").*$, message: Нет viewport meta, severity: critical

## К-09. Палитра из референсов
Цвета артефакта соответствуют палитре выбранного референса (не более 4 акцентных цветов).

## К-10. Типографика
Подключены заголовочный и базовый шрифты из metadata референса; размер base >= 16px.

## К-11. Контраст WCAG
Контраст текста к фону не ниже 4.5:1 для основного текста.

## К-12. Формы доступны
Каждое поле input имеет label или aria-label.
check_regex: <input(?![^>]*(aria-label|id=))[^>]*type="(text|email|tel)", message: Поле формы без подписи, severity: major

## К-13. Отсутствие шаблона-клона
Два проекта студии не должны совпадать хешем структуры >90%.

## К-14. Производительность
Размер HTML ≤ 200 КБ, инлайновых стилей-повторов ≤ 10.

## К-15. Ссылки живые
Все href ведут на якоря/# или полные URL; запрещены пустые href="#".
check_regex: href="#"(?![^<]*>), message: Пустая ссылка href="#", severity: minor

## К-16. Язык страницы
Атрибут lang у `<html>` соответствует языку брифа.

## К-17. Заголовок H1 ровно один
check_regex: (?s)(<h1[\s>][\s\S]*?<\/h1>[\s\S]*){2,}, message: Более одного H1, severity: major

## К-18. Favicon и social meta
Есть link rel=icon и og:title.

## К-19. Без console-мусора
Финальный JS не содержит debug-вызовов.
check_regex: console\.log\(|debugger\b, message: Debug-код в финальном артефакте, severity: major

## К-20. Доступность навигации
Навигация имеет aria-label="Основная навигация" или role=navigation.

## К-21. Читаемость копирайта
Заглавные предложения без CAPS-простыней.

## К-22. Структура секций
Секции идут в порядке hero → features → (catalog/pricing) → cta → footer.

## К-23. Единый источник истины по бюджету
Комментарий с ценой run'а присутствует в отчёте, не в HTML.

## К-24. Версия студии
В футере указан шаблон/версия студии для трассируемости.
