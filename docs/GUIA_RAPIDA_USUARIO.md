# Guía rápida de usuario · Portal de Atención Vecinal

Municipalidad Provincial de Huancayo · Green AI Municipal

Esta guía explica en pocos pasos cómo presentar y seguir un reclamo, y cómo lo atiende el personal municipal en el Sistema de Gestión Interna (SIGEM). También está disponible dentro del portal, en el botón **❓ ¿Cómo usar?** de la página de inicio (`#/guia`).

Portal: <https://taller-de-proyectos-software.vercel.app/>

---

## 1. Para vecinos: presentar y seguir un reclamo

| Paso | Qué hacer |
|---|---|
| 1 | En la página de inicio elija **Registrar un reclamo** (Módulo A). No necesita crear una cuenta. |
| 2 | Escriba su nombre, DNI, un teléfono o correo y su domicilio. Luego indique un **título**, la **ubicación exacta** del problema (calle, cuadra y una referencia) y **qué ocurre**, desde cuándo y cómo afecta a los vecinos. |
| 3 | Presione **Enviar Reclamo a la IA Municipal**. La inteligencia artificial corrige la redacción, protege sus datos personales y asigna la categoría (Vías Públicas, Limpieza Pública, Parques y Jardines o Alumbrado). Tarda unos segundos. |
| 4 | ⚠️ **Guarde su número de ticket y su código secreto.** El código se muestra una sola vez: cópielo, anótelo o use **Imprimir constancia**. Sin el código nadie puede ver su reclamo, ni siquiera usted. |
| 5 | Cuando quiera ver el avance, entre a **Consultar mi trámite** (Módulo C) y escriba el número de ticket y el código. |

### ¿Qué significa cada estado?

| Estado | Significado |
|---|---|
| ● Pendiente | El reclamo fue recibido y espera ser atendido. |
| ◐ En proceso | El área responsable ya está trabajando en él. |
| ✓ Resuelto | El área dio por atendido el reclamo. |
| ⚠ Pendiente de auditoría HITL | Solo lo ve el personal: un especialista confirma la categoría antes de derivarlo. |

---

## 2. Para personal municipal: atender reclamos en el SIGEM

| Paso | Qué hacer |
|---|---|
| 1 | En la página de inicio elija **Acceso Personal Municipal** (Módulo B) e ingrese el correo y la contraseña que le asignó el administrador. La sesión se cierra sola al vencer. |
| 2 | En el **Panel de Control** los contadores muestran cuántos reclamos hay en cada estado. La tabla lista **25 reclamos por página**, del más reciente al más antiguo. Use **Ver completo** para leer todo el texto y **Actualizar datos** para traer los reclamos nuevos. |
| 3 | ⚠️ Atienda los reclamos **Pendiente de auditoría HITL**: la IA tuvo una confianza menor al 70 %. Lea el texto, elija la categoría correcta y presione **Confirmar y derivar** (o **Corregir y derivar** si la cambió). El reclamo pasa a **En proceso** en su gerencia. |
| 4 | En la columna **Estado** elija **En proceso** cuando el área empiece a atender el reclamo y **Resuelto** al terminar. El vecino ve el cambio al consultar su trámite. |
| 5 | En **Búsqueda y Filtrado** escriba una palabra del reclamo (por ejemplo «poste» o «basura») y filtre por categoría o estado. |
| 6 | En **Dashboard Green AI** vea la energía y las emisiones de CO₂ de la IA y los reclamos por categoría. Con **Descargar CSV (Excel)** obtiene el detalle de cada reclamo y con **Reporte PDF** un resumen listo para imprimir o guardar como PDF. |

---

## 3. Protección de datos

El nombre, el DNI, el contacto y el domicilio del vecino se reemplazan por etiquetas como `[DNI_PROTEGIDO]` antes de guardarse y no se envían al servicio de inteligencia artificial (Ley N° 29733). La ubicación del problema sí es pública, porque es el lugar donde se debe atender.

## 4. Preguntas frecuentes

- **Perdí mi código secreto.** No se puede recuperar: la base solo guarda una huella irreversible (hash) del código, no el código. Registre el reclamo nuevamente o acérquese a la Municipalidad con su número de ticket.
- **El envío tarda casi un minuto.** El servidor gratuito se apaga cuando no hay uso; la primera solicitud lo vuelve a encender. Las siguientes son rápidas.
- **El personal no puede cambiar un estado.** La sesión venció: presione **Cerrar sesión** e ingrese de nuevo.
