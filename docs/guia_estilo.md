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

---

## 2. Tipografía

### 2.1 Fuente

Se usa la fuente **sans-serif del sistema** que trae Tailwind (`font-sans`):
Segoe UI en Windows, San Francisco en Mac y Roboto en Android.
No se cargan fuentes externas, así la página carga más rápido.

### 2.2 Tamaños

| Elemento | Clases | Ejemplo en el proyecto |
|---|---|---|
| Título de la sección (encabezado del panel) | `text-xl md:text-2xl font-bold text-gray-900 dark:text-white` | "Gestión de usuarios" |
| Título de tarjeta o modal | `text-xl font-bold text-gray-900 dark:text-white` | "Nuevo administrador", "Detalle de usuario" |
| Subtítulo o descripción | `text-sm text-gray-500 dark:text-gray-400` | "Crea una cuenta interna y asigna su rol" |
| Texto normal | `text-sm text-gray-600 dark:text-gray-300` | Celdas de las tablas |
| Etiqueta de formulario | `text-xs font-semibold text-gray-600 dark:text-gray-400` | "Nombre *", "Correo electrónico *" |
| Texto pequeño (ayudas, errores) | `text-xs` | "El correo no se puede modificar." |

### 2.3 Mayúsculas

Solo la **primera letra** del texto va en mayúscula, en títulos, botones y etiquetas:
"Agregar administrador", "Precio normal", "Estado de la cuenta".
No se escribe "Agregar Administrador" ni "PRECIO NORMAL".

---

## 3. Componentes

### 3.1 Botones

| Tipo | Cuándo se usa | Clases |
|---|---|---|
| Principal | La acción principal de la pantalla (Guardar, Crear) | `px-4 py-2.5 rounded-xl bg-[#F2AE30] hover:bg-[#d99b28] text-black text-sm font-bold transition-colors` |
| Secundario | Cancelar, Volver | `px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors` |
| Peligro | Acciones irreversibles (Inactivar, Restaurar) | `px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-bold transition-colors` |
| Solo icono | Acciones de las tablas (editar, ver) | `p-2 rounded-lg transition-colors` + `title="..."` y `aria-label="..."` |

**Reglas:**
- Una pantalla tiene **un solo botón principal**.
- Los botones de peligro de un formulario llevan `data-confirmar="¿Pregunta?"`
  para que aparezca el modal de confirmación (historia G1-1193).
- Un botón que solo tiene icono **siempre** lleva `title` y `aria-label` (historia G1-1194).

### 3.2 Tarjetas y modales

```html
<div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
  ...
</div>
```

Los formularios centrados (crear, editar) usan `shadow-2xl w-full max-w-md`.

### 3.3 Formularios

Todos los campos usan la misma clase. En los formularios de Django se pone en el `__init__`
(ver `Usuarios/forms.py`):

```
w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900
text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#F2AE30] outline-none
```

- La etiqueta va encima del campo con la clase de "Etiqueta de formulario" (sección 2.2).
- Los campos obligatorios llevan un asterisco en la etiqueta: "Nombre *".
- El error va debajo del campo: `<p class="text-xs text-red-500 mt-1">`.

### 3.4 Tablas

| Parte | Clases |
|---|---|
| Encabezado | `bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-sm` |
| Celda | `p-4` |
| Fila al pasar el mouse | `hover:bg-gray-50/50 dark:hover:bg-gray-800/50` |
| Sin resultados | Una fila con `colspan` y el texto "No se encontraron ..." |

### 3.5 Iconos

- Se usan iconos SVG de línea (estilo *Lucide*), de `w-4 h-4` a `w-6 h-6`, con `stroke="currentColor"`
  para que tomen el color del texto.
- **Todo** `<svg>` lleva `aria-hidden="true"`: el significado lo da el texto o el `aria-label` del botón.
- La prueba `IconosConDescripcionTests` (en `Usuarios/tests.py`) revisa esto en todas las plantillas.

### 3.6 Mensajes y confirmaciones

- Mensajes: `{% include 'partials/mensajes.html' %}` (ya está en `base.html` y `admin_base.html`).
  En la vista se usa `messages.success`, `messages.error`, `messages.warning` o `messages.info`
  según la tabla de la sección 1.4.
- Confirmación: agrega `data-confirmar="¿Seguro que...?"` al `<form>`.
  El modal está en `partials/modal_confirmacion.html` y su lógica en `static/js/confirmar.js`.

### 3.7 Logo

- Archivo: `static/img/logo_tecniled.png` (bombillo naranja con la palabra "LED", fondo transparente).
- Se ve bien en modo claro y en modo oscuro, por eso no necesita otra versión.
- Va siempre acompañado del nombre **TECNILED** en texto, en negrita (`font-black` o `font-bold`).
- No se deforma: usar `object-contain` y no cambiar sus colores.

### 3.8 Variables y clases de `static/css/style.css`

Los colores principales también están como **variables CSS**, para usarlos en CSS propio:

| Variable | Valor |
|---|---|
| `--color-primario` | `#F2AE30` |
| `--color-primario-hover` | `#d99b28` |
| `--color-texto-sobre-primario` | `#000000` |
| `--color-texto` / `--color-texto-secundario` | Cambian solos en modo oscuro |
| `--color-fondo` / `--color-fondo-suave` / `--color-borde` | Cambian solos en modo oscuro |
| `--color-exito` / `--color-error` / `--color-advertencia` / `--color-informacion` | Colores de alerta |
| `--color-peligro` | `#DC2626` (`red-600`) |

Uso: `color: var(--color-primario);`

**Clases reutilizables de botones** (equivalen a las de la sección 3.1):
`btn-principal`, `btn-secundario` y `btn-peligro`.

```html
<button type="submit" class="btn-principal">Guardar cambios</button>
```