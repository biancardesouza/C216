from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status

from app.api.dependencies import get_item_service
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])

Service = Annotated[ItemService, Depends(get_item_service)]
ItemId = Annotated[int, Path(gt=0, description="Identificador do item")]


@router.get("/", response_model=list[Item])
def list_items(service: Service):
    return service.list()


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: ItemId, service: Service):
    return service.get(item_id)


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, service: Service):
    return service.create(payload)


@router.put("/{item_id}", response_model=Item)
def update_item(item_id: ItemId, payload: ItemUpdate, service: Service):
    return service.update(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: ItemId, service: Service):
    service.delete(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
