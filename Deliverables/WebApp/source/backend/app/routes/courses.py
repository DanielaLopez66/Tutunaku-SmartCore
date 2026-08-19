"""Tutunaku - Rutas de Cursos"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user_id, require_admin
from app.core.exceptions import NotFoundError
from app.models.mysql_models import Course, Unit, Lesson
from app.schemas.schemas import CourseCreate, CourseUpdate, CourseResponse, StandardResponse

router = APIRouter()


@router.get("", response_model=list[CourseResponse])
async def list_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(Course.is_published == True).order_by(Course.order_index)
    )
    courses = result.scalars().all()

    counts_result = await db.execute(select(Unit.course_id, func.count(Unit.id)).group_by(Unit.course_id))
    units_count_by_course = dict(counts_result.all())

    return [CourseResponse(
        id=c.id, title=c.title, description=c.description,
        cover_image_url=c.cover_image_url, color_hex=c.color_hex, difficulty=c.difficulty.value,
        is_published=c.is_published, order_index=c.order_index,
        created_at=c.created_at, units_count=units_count_by_course.get(c.id, 0),
    ) for c in courses]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise NotFoundError("Curso")
    units_count = (await db.execute(
        select(func.count(Unit.id)).where(Unit.course_id == course_id)
    )).scalar_one()
    return CourseResponse(
        id=course.id, title=course.title, description=course.description,
        cover_image_url=course.cover_image_url, color_hex=course.color_hex, difficulty=course.difficulty.value,
        is_published=course.is_published, order_index=course.order_index,
        created_at=course.created_at, units_count=units_count,
    )


@router.post("", response_model=StandardResponse, status_code=201)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    course = Course(**data.model_dump())
    db.add(course)
    await db.commit()
    return StandardResponse(message="Curso creado", data={"id": course.id})


@router.patch("/{course_id}", response_model=StandardResponse)
async def update_course(
    course_id: str,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise NotFoundError("Curso")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(course, key, value)
    await db.commit()
    return StandardResponse(message="Curso actualizado")


@router.delete("/{course_id}", response_model=StandardResponse)
async def delete_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise NotFoundError("Curso")
    await db.delete(course)
    await db.commit()
    return StandardResponse(message="Curso eliminado")
