# ADR-011: Area y Project como entidades PARA opcionales

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

SIGMA integra el método PARA (Projects, Areas, Resources,
Archives) para clasificar el trabajo. Las Cards necesitan
poder asociarse a esta estructura para dar contexto y
facilitar la navegación, pero no toda Card tiene contexto
suficiente en el momento de su creación.

## Decisión

`Area` y `Project` son entidades de dominio independientes.
Una Card puede referenciarlas opcionalmente. La jerarquía
es: Area → Project → Card (todo opcional).

```
Area
  id: AreaId
  name: str

Project
  id: ProjectId
  name: str
  area_id: AreaId       ← un Project siempre pertenece a un Area
  status: ProjectStatus (ACTIVE | COMPLETED | ON_HOLD)

Card
  area_id: AreaId | None
  project_id: ProjectId | None
```

Un Card puede tener: ninguno, solo Area, o Area + Project.
No puede tener Project sin Area — si se asigna un Project,
su Area se infiere.

## Razonamiento

El método PARA clasifica el trabajo en responsabilidades
continuas (Areas) y esfuerzos finitos con resultado
(Projects). Esta distinción es útil para filtrado y
navegación pero no es una precondición para el trabajo —
las ideas capturadas en Inbox típicamente no tienen
clasificación aún.

Hacer Area/Project obligatorios bloquearía la captura
rápida, que es uno de los valores principales de SIGMA.

`Resources` y `Archives` del método PARA se omiten en v1
— Resources es un concepto de gestión del conocimiento
(corresponde a Obsidian en el ecosistema del autor) y
Archives se cubre con el estado terminal del workflow.

## Alternativas consideradas

- **Area y Project obligatorios**: bloquea la captura rápida
  en Inbox. Contradice el flujo Inbox → Refinement → Backlog
  donde la clasificación ocurre en Refinement. Descartado.
- **Tags libres en lugar de Area/Project**: más flexible pero
  pierde la semántica estructurada del método PARA y dificulta
  consultas por área o proyecto. Descartado.
- **Implementar los cuatro elementos de PARA**: Resources y
  Archives no aportan valor en v1 dado el ecosistema existente
  (Obsidian para knowledge, estado End del workflow para
  archivado). Descartado — YAGNI.

## Consecuencias

- `AreaRepository` y `ProjectRepository` son puertos separados
- Al asignar un `project_id` a un Card, el caso de uso verifica
  que el Project exista y extrae su `area_id` automáticamente
- Las consultas `GetCardsByArea` y `GetCardsByProject` se
  añaden como casos de uso de lectura
- La eliminación de un Area o Project requiere decisión sobre
  las Cards huérfanas — definido en los casos de uso
  correspondientes
