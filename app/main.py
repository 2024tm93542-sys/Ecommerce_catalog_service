from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from . import crud, schemas

app = FastAPI(title="Catalog Service", version="1.0.0")

@app.get("/v1/products", response_model=schemas.PaginatedProducts)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
    category: Optional[str] = None,
    price_gt: Optional[float] = None,
    price_lt: Optional[float] = None,
    sort_by_price: Optional[str] = Query(None, regex="^(asc|desc)$"),
    substring: Optional[str] = None
):
    items, total = crud.fetch_products(page, per_page, category, price_gt, price_lt, sort_by_price, substring)
    return {"items": items, "page": page, "per_page": per_page, "total": total}

@app.post("/v1/products", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate):
    product_id = crud.create_product(product)
    prod = crud.fetch_product_by_sku(product.sku)
    return prod

@app.put("/v1/products/{sku}", response_model=schemas.ProductOut)
def update_product(sku: str, payload: schemas.ProductUpdate):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = crud.update_product(sku, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.fetch_product_by_sku(sku)

@app.delete("/v1/products/{sku}", response_model=schemas.ProductOut)
def delete_product(sku: str):
    deleted = crud.soft_delete_product(sku)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.fetch_product_by_sku(sku)
