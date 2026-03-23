# ADR-003: Base de datos — Firestore con modelado documental estructurado

**Estado:** Aceptado
**Fecha:** 2026-03-21

## Contexto

SIGMA gestiona tareas con estados, fechas, bloques de tiempo
y relaciones entre entidades (columnas, tarjetas, filtros).
Necesita una base de datos dentro del free tier de GCP con
soporte para consultas flexibles.

## Decisión

Firestore con modelado documental estructurado mediante
desnormalización controlada.

Estructura de colecciones:
```
/cards/{cardId}           ← entidad principal
/columns/{columnId}       ← columnas del flujo SIGMA
/columns_cards/{columnId}/cards/{cardId}  ← relación columna-tarjeta
/filters/by_month/{yyyy_mm}/cards/{cardId} ← acceso por mes
```

## Razonamiento

El modelo documental no es ausencia de modelo — es un modelo
optimizado para patrones de lectura. La desnormalización
controlada prepara las relaciones en write time evitando
joins en query time.

Las limitaciones típicas de Firestore en queries relacionales
se resuelven con diseño correcto de colecciones. Las escrituras
multi-colección se gestionan con transacciones atómicas,
incluidas en el free tier.

## Alternativas consideradas

- **Cloud SQL (PostgreSQL)**: potente para queries complejas
  pero sin free tier permanente. Descartado.
- **SQLite en Cloud Run**: filesystem efímero en Cloud Run
  provoca divergencia de datos entre instancias. Descartado.
- **Supabase**: sale del ecosistema GCP. Descartado.

## Consecuencias

- Free tier de 50K reads y 20K writes diarios — más que
  suficiente para uso personal
- Escrituras multi-colección requieren transacciones atómicas
- Si se renombra una colección de acceso frecuente hay que
  actualizar los índices en Firestore
- Para analytics avanzados en el futuro se puede exportar
  a BigQuery (también con free tier)