# Backend (WearableApp)

No existe un backend propio para el wearable: la app de Kotlin (`../app`)
consume directamente la misma API REST y Socket.IO del backend de
`Deliverables/WebApp/source/backend`. Ver `../architecture_wearable.md` para
el detalle de qué endpoints reutiliza.

Esta carpeta se conserva vacía por si en el futuro se necesita un servicio
intermediario propio del wearable (ej. cache local, proxy de sincronización).
