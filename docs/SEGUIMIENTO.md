# Seguimiento IPES2


> Actualizado: 2025-08-30


## Estado por Fase
- [ ] F0 Fundaciones — notas:
- [ ] F1 Horarios — notas:
- [ ] F2 Inscripción — notas:
- [ ] F3 Comisiones — notas:
- [ ] F4 Docentes — notas:
- [ ] F5 Notas — notas:
- [ ] F6 Paneles — notas:
- [ ] F7 KPIs — notas:
- [ ] F8 Endurecimiento — notas:


## Cambios Recientes (30 de Agosto de 2025)

### 1. Refactorización de Gestión de Horarios (Comisiones)
- **API Backend para Bloques Horarios:**
  - Implementada `timeslots_api` en `views.py` para proveer bloques horarios filtrados por día/turno.
  - Añadido patrón de URL para `timeslots_api` en `urls.py`.
  - Mejoradas funciones `_norm_dia` y `_norm_turno` para manejo robusto de entradas.
  - Corregidas claves del diccionario `TURNOS` en `views.py` para coincidir con valores del frontend.
  - Solucionado problema de enrutamiento (`panel/panel/` duplicado) que causaba errores 404.
- **Refactorización de Formulario (`HorarioInlineForm`):**
  - Reemplazado `HorarioClaseForm` (ModelForm) por `HorarioInlineForm` (forms.Form) en `forms.py`.
  - Implementados métodos `__init__`, `clean` y `save` personalizados en `HorarioInlineForm`.
  - Actualizadas definiciones de campos (`turno`, `dia`, `bloque`, `aula`, `docentes`).
  - Añadido `DIA_CHOICES` al modelo `TimeSlot` en `models.py`.
- **Refactorización de Vista (`ComisionDetailView`):**
  - Convertida `ComisionDetailView` (basada en clase) a `comision_detail` (basada en función) en `views.py`.
  - Integrado el procesamiento de formularios (GET/POST) directamente en `comision_detail`.
  - Actualizado `urls.py` para apuntar a la nueva vista basada en función.
  - Eliminadas `HorarioCreateView` y `HorarioUpdateView` (y sus URLs asociadas).

### 2. Control de Tope de Horas por Materia
- Añadido campo `horas_catedra` a `MateriaEnPlan` en `models.py`.
- Implementadas propiedades `horas_catedra_tope`, `horas_asignadas_en_periodo` y `horas_restantes_en_periodo` en el modelo `Comision` en `models.py`.
- Actualizado método `HorarioClase.clean` en `models.py` para aplicar el límite de horas.
- Actualizada vista `comision_detail` para pasar datos de tope de horas al template.

### 3. Validación de Conflicto de Docentes
- Implementado método `clean` en `HorarioInlineForm` para prevenir conflictos de docentes (mismo bloque/período).
- Añadido método `get_dia_semana_display` al modelo `TimeSlot` en `models.py`.
- Implementado `m2m_changed` signal en `signals.py` para prevenir conflictos fuera del formulario.
- Registradas señales en `apps.py` y `__init__.py`.

### 4. Mejoras de UX en Frontend
- Añadido resumen de docentes seleccionados (chips y contador) en `comision_detail.html` y `panel.js`.
- Añadido texto de ayuda para multiselección de docentes en `comision_detail.html`.
- Eliminado campo "Observaciones" del formulario y template.
- Actualizada visualización de errores del formulario en `comision_detail.html`.
- Deshabilitado botón "Agregar" cuando se alcanza el límite de horas.

### 5. Importación de Docentes
- Corregidos múltiples errores de sintaxis y lógica en `scripts/import_docentes.py`.
- Corregida ruta de archivo en `import_docentes.py`.
- Añadido campo `dni` al modelo `Docente` en `models.py` y ejecutadas migraciones para soportar importación por DNI.
- Importados exitosamente 184 docentes.

### 6. Corrección de Errores Críticos
- Solucionado `SyntaxError` en `views.py` (`def_rango_por_turno`).
- Solucionado `SyntaxError` en `forms.py` (f-string en `msgs.append`).
- Solucionado `ImportError` para `hc_asignadas` y `hc_requeridas` reintroduciéndolas como funciones independientes en `models.py`.
- Solucionado `NoReverseMatch` para `panel_horario_edit` eliminando el enlace.
- Solucionado `TemplateSyntaxError` simplificando la visualización de errores en el template.
- Solucionado `AttributeError` para `HorarioClase.Turno` y `HorarioClase.Dia` usando `Turno.choices` y `DIAS_CHOICES`.


## Tareas abiertas
- [ ] ...


## Bloqueos
- [ ] ...


## Problemas conocidos
- [ ] ...