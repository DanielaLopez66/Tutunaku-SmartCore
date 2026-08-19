# Script de Reestructuración de Proyecto Tutunaku
$ErrorActionPreference = "Stop"

$workspace = "d:\Descargas\tutunaku"
Set-Location $workspace

# 1. Crear la nueva estructura de carpetas base
$folders = @(
    "DataBases/NoSQL/Backups",
    "DataBases/NoSQL/DD",
    "DataBases/NoSQL/Schemas",
    "DataBases/SQL/Backups",
    "DataBases/SQL/DD",
    "DataBases/SQL/ERD",
    "DataBases/SQL/RM",
    "DataModels/Supervised_LMs",
    "DataModels/Unsupervised_LMs",
    "Deliverables/API/build",
    "Deliverables/API/DeployManual",
    "Deliverables/API/source",
    "Deliverables/WearableApp/build",
    "Deliverables/WearableApp/DeployManual",
    "Deliverables/WearableApp/source/backend",
    "Deliverables/WearableApp/source/frontend",
    "Deliverables/WebApp/build",
    "Deliverables/WebApp/DeployManual",
    "Deliverables/WebApp/source",
    "Docs/BRs",
    "Docs/FRs",
    "Docs/GUIs/WearableApp",
    "Docs/GUIs/WebApp",
    "Docs/NFRs",
    "Docs/UHs",
    "Docs/URs"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
}

# Crear readme vacío en DataBases
New-Item -ItemType File -Path "DataBases/readme.md" -Force | Out-Null

# 2. Mover la Aplicación Web
if (Test-Path "backend") {
    Move-Item -Path "backend" -Destination "Deliverables/WebApp/source/backend" -Force
}
if (Test-Path "frontend") {
    Move-Item -Path "frontend" -Destination "Deliverables/WebApp/source/frontend" -Force
}

# 3. Mover Bases de Datos
if (Test-Path "database/mysql") {
    Move-Item -Path "database/mysql/*" -Destination "DataBases/SQL/DD/" -Force
}
if (Test-Path "database/mongodb") {
    Move-Item -Path "database/mongodb/*" -Destination "DataBases/NoSQL/Schemas/" -Force
}
if (Test-Path "database") {
    Remove-Item -Path "database" -Recurse -Force
}

# 4. Mover Documentación
if (Test-Path "docs") {
    Move-Item -Path "docs/*" -Destination "Docs/" -Force
    Remove-Item -Path "docs" -Recurse -Force
}

Write-Output "Reestructuración completada exitosamente."
