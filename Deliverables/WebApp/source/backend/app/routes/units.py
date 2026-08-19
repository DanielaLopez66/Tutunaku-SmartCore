"""Tutunaku - Rutas de Unidades"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import require_admin
from app.core.exceptions import NotFoundError
from app.models.mysql_models import Lesson, Unit
from app.schemas.schemas import UnitCreate, UnitUpdate, UnitResponse, StandardResponse

router = APIRouter()

@router.get("/course/{course_id}", response_model=list[UnitResponse])
async def get_units_by_course(course_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Unit).where(Unit.course_id == course_id).order_by(Unit.order_index))
    units = result.scalars().all()

    counts_result = await db.execute(
        select(Lesson.unit_id, func.count(Lesson.id))
        .where(Lesson.is_published == True)
        .group_by(Lesson.unit_id)
    )
    lessons_count_by_unit = dict(counts_result.all())

    return [
        UnitResponse(
            id=u.id, course_id=u.course_id, title=u.title, description=u.description,
            icon_emoji=u.icon_emoji, color_hex=u.color_hex, order_index=u.order_index,
            is_locked=u.is_locked, xp_reward=u.xp_reward, created_at=u.created_at,
            lessons_count=lessons_count_by_unit.get(u.id, 0),
        )
        for u in units
    ]

@router.post("", response_model=StandardResponse, status_code=201)
async def create_unit(data: UnitCreate, db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    unit = Unit(**data.model_dump())
    db.add(unit)
    await db.commit()
    return StandardResponse(message="Unidad creada", data={"id": unit.id})

@router.patch("/{unit_id}", response_model=StandardResponse)
async def update_unit(unit_id: str, data: UnitUpdate, db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(Unit).where(Unit.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit:
        raise NotFoundError("Unidad")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(unit, k, v)
    
    await db.commit()
    return StandardResponse(message="Unidad actualizada")

@router.delete("/{unit_id}", response_model=StandardResponse)
async def delete_unit(unit_id: str, db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(Unit).where(Unit.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit:
        raise NotFoundError("Unidad")
    
    await db.delete(unit)
    await db.commit()
    return StandardResponse(message="Unidad eliminada")
