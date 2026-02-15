from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import User, Organization, UserOrganization
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.api.deps import get_current_user, get_organization_membership

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.post("", response_model=OrganizationResponse)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org = Organization(name=data.name)
    db.add(org)
    await db.flush()
    membership = UserOrganization(
        user_id=current_user.id,
        organization_id=org.id,
        role="owner",
    )
    db.add(membership)
    await db.refresh(org)
    return org


@router.get("", response_model=list[OrganizationResponse])
async def list_my_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Organization)
        .join(UserOrganization, UserOrganization.organization_id == Organization.id)
        .where(UserOrganization.user_id == current_user.id)
    )
    orgs = result.scalars().all()
    return list(orgs)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    membership: UserOrganization = Depends(get_organization_membership),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return org
