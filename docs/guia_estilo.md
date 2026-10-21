# Guía de estilo TECNILED

Esta guía define cómo se ven todas las pantallas del proyecto: colores,
tipografía, botones, tarjetas, formularios e iconos. Antes de crear una
pantalla nueva, revisa esta guía y copia las clases de Tailwind que aparecen aquí.

> Historia de Jira: G1-1191 — Guía de estilo corporativa TECNILED.

---

## 1. Paleta de colores

### 1.1 Color principal (identidad TECNILED)

| Uso | Color | Clase de Tailwind |
|---|---|---|
| Principal: botones, menú activo, enlaces destacados, foco | `#F2AE30` | `bg-[#F2AE30]` · `text-[#F2AE30]` · `focus:ring-[#F2AE30]` |
| Principal al pasar el mouse (*hover*) | `#d99b28` | `hover:bg-[#d99b28]` |
| Texto encima del color principal | `#000000` (negro) | `text-black` |

**Regla:** sobre el amarillo `#F2AE30` el texto va **siempre en negro**, nunca en blanco
(ver la tabla de contraste en la sección 4).

### 1.2 Fondos

| Uso | Modo claro | Modo oscuro |
|---|---|---|
| Fondo de la página (tienda) | `bg-white` (`#FFFFFF`) | `dark:bg-gray-950` (`#030712`) |
| Fondo de la página (panel) | `bg-gray-50` (`#F9FAFB`) | `dark:bg-gray-900` (`#111827`) |
| Tarjetas, modales y menú lateral | `bg-white` (`#FFFFFF`) | `dark:bg-gray-800` (`#1F2937`) |
| Campos de formulario y cajas internas | `bg-gray-50` (`#F9FAFB`) | `dark:bg-gray-900` (`#111827`) |
| Bordes | `border-gray-100` / `border-gray-200` | `dark:border-gray-700` |

### 1.3 Textos

| Uso | Modo claro | Modo oscuro |
|---|---|---|
| Títulos y texto principal | `text-gray-900` (`#111827`) | `dark:text-white` |
| Texto normal y etiquetas | `text-gray-600` / `text-gray-700` | `dark:text-gray-300` |
| Texto secundario (ayudas, fechas) | `text-gray-500` (`#6B7280`) | `dark:text-gray-400` |
| Texto desactivado o decorativo | `text-gray-400` (`#9CA3AF`) | `dark:text-gray-500` |

**Regla:** `text-gray-400` no cumple el contraste mínimo sobre fondo blanco.
Úsalo solo para iconos decorativos, textos de ejemplo (*placeholder*) o elementos desactivados.

### 1.4 Colores de alerta

Los usa el componente `template/partials/mensajes.html` (historia G1-1193).

| Tipo | Cuándo se usa | Fondo | Texto | Borde |
|---|---|---|---|---|
| Éxito (`messages.success`) | La acción salió bien | `bg-emerald-50` | `text-emerald-700` | `border-emerald-200` |
| Error (`messages.error`) | La acción falló o no está permitida | `bg-red-50` | `text-red-700` | `border-red-200` |
| Advertencia (`messages.warning`) | No falló, pero el usuario debe revisar algo | `bg-amber-50` | `text-amber-800` | `border-amber-200` |
| Información (`messages.info`) | Aviso neutral | `bg-blue-50` | `text-blue-700` | `border-blue-200` |

### 1.5 Colores de estado (etiquetas pequeñas)

| Estado | Clases |
|---|---|
| Activa / disponible | `bg-emerald-100 text-emerald-700` |
| Suspendida / inactiva | `bg-red-100 text-red-700` |
| Rol Administrador | `bg-purple-100 text-purple-700` |
| Rol Control de inventario | `bg-emerald-100 text-emerald-700` |
| Rol Cliente | `bg-gray-100 text-gray-700` |

### 1.6 Botones de peligro

Para acciones irreversibles (inactivar, restaurar, eliminar):
`bg-red-600 hover:bg-red-700 text-white`.

**Regla:** no usar `bg-red-500` con texto blanco: no cumple el contraste mínimo.