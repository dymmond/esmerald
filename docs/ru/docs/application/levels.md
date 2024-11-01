# Уровни приложения

Приложение Esmerald состоит из уровней, и эти уровни могут быть [Gateway](../routing/routes.md#gateway),
[WebSocketGateway](../routing/routes.md#websocketgateway), [Include](../routing/routes.md#include),
[handlers](../routing/handlers.md) или даже **другое приложение Esmerald** или
[ChildEsmerald](../routing/router.md#child-esmerald-application).

Существуют различные уровни в приложении, давайте рассмотрим пример.
```python
{!> ../../../docs_src/application/app/levels.py !}
```

**Уровни**:

1. [Esmerald](./applications.md) — экземпляр приложения.
2. [Include](../routing/routes.md#include) — второй уровень.
3. [Gateway](../routing/routes.md#gateway) — третий уровень, внутри Include.
4. [Handler](../routing/handlers.md) — четвертый уровень, обработчик Gateway.

Вы можете создавать столько уровней, сколько захотите, включая вложенные Include и
[ChildEsmerald](../routing/router.md#child-esmerald-application), создавая собственную архитектуру.

## С использованием ChildEsmerald:

```python hl_lines="50 59"
{!> ../../../docs_src/application/app/child_esmerald_level.py !}
```

**Уровни**:

1. [Esmerald](./applications.md) — Основной экземпляр приложения. **Первый уровень**.
2. [Gateway](../routing/routes.md#gateway) — **Второй уровень**, внутри маршрутов приложения.
    1. [Handler](../routing/handlers.md) — **Третий уровень**, внутри Gateway.
3. [WebSocketGateway](../routing/routes.md#websocketgateway) — **Второй уровень**, внутри маршрутов приложения.
    1. [Handler](../routing/handlers.md) — **Третий уровень**, внутри WebSocketGateway.
4. [Include](../routing/routes.md#include) — **Второй уровень**, внутри маршрутов приложения.
    1. [ChildEsmerald](../routing/router.md#child-esmerald-application) — **Третий уровень** внутри Include и также **первый уровень** как независимый экземпляр.
        1. [Gateway](../routing/routes.md#gateway) — **Второй уровень**, внутри `ChildEsmerald`.
            1. [Handler](../routing/handlers.md) — **Третий уровень**, внутри Gateway.

!!! Warning
    `ChildEsmerald` — это независимый экземпляр, подключаемый к основному приложению `Esmerald`.
    Поскольку он ведет себя как другой объект `Esmerald`, `ChildEsmerald` не имеет приоритета над
    верхним уровнем приложения. Вместо этого он обрабатывает свои собственные
    [Gateway](../routing/routes.md#gateway), [WebSocketGateway](../routing/routes.md#websocketgateway),
    [Include](../routing/routes.md#include), [handlers](../routing/handlers.md) или даже другой `Esmerald`
    или [ChildEsmerald](../routing/router.md#child-esmerald-application) и параметры **в изоляции**.

## Исключения

`ChildEsmerald`, как указано в **предупреждении** выше, действует по своим собственным правилам,
но у каждого правила есть исключения. Хотя это независимый экземпляр с собственными правилами,
они не применяются ко **всем** параметрам.

[Middleware](../middleware/middleware.md) и [Permissions](../permissions.md) являются глобальными,
и правила приоритета могут применяться между экземпляром `Esmerald` и соответствующими приложениями
`ChildEsmerald`.

Другими словами, **нет необходимости** создавать или дублировать одни и те же permissions и middleware
(общие для обоих) для каждого экземпляра. Они могут быть применены **глобально** из основного объекта `Esmerald`.

```python hl_lines="99-101 108 115 119-120"
{!> ../../../docs_src/application/app/permissions_and_middlewares.py !}
```

### Заметки

Приведенный пример намеренно показан большим и "сложным", чтобы продемонстрировать, что, даже
несмотря на такую сложность, `middleware` и `permissions` остаются глобальными для всего
приложения без необходимости реализовывать их как в `Esmerald`, так и в `ChildEsmerald`.
