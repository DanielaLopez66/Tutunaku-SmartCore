# Backend (WearableApp)

No existe un backend propio para el wearable: la app de Kotlin (`../app`)
consume directamente la misma API REST y Socket.IO del backend de
`Deliverables/WebApp/source/backend`. Ver `../architecture_wearable.md` para
el detalle de qué endpoints reutiliza.

Esta carpeta se conserva vacía por si en el futuro se necesita un servicio
intermediario propio del wearable (ej. cache local, proxy de sincronización).

## Equipo de Desarrollo

| Integrante | Contacto | Rol |
| --- | --- | --- |
| Ana Daniela López Neri | [@DanielaLopez66](https://github.com/DanielaLopez66) | Encargada de Documentación y Líder de Equipo |
| Brandon León Cabrera | [@bleon26](https://github.com/bleon26) | Encargado de Base de Datos |
| Tania Ibarra Salgado | [@ibarra-tania](https://github.com/ibarra-tania) | Encargada del Desarrollo |
