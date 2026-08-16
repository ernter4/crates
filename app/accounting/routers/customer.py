from fastapi import Depends, HTTPException, APIRouter

from app.accounting.models import CustomerWithID,CustomerCreate, get_customer_filter_query,Customer
from app.accounting.services.models.customerService import CustomerService
from app.shared.dependencies import SessionDep


router = APIRouter()


resource_name = "Customer"
@router.post("/",operation_id=f"{resource_name}_post")
def create(data: CustomerCreate, session: SessionDep):
    return CustomerService(session).create(data)

@router.get("/{item_id}", operation_id=f"{resource_name}_get_by_id")
def get( item_id: int, session: SessionDep) ->  CustomerWithID:
    customer =CustomerService(session).get(item_id)
    if customer: return  customer
    raise HTTPException(status_code=404, detail="Customer not found")

@router.put("/{item_id}", operation_id=f"{resource_name}_put",response_model=CustomerWithID)
def update( item_id:int,data: CustomerWithID, session: SessionDep):
    try:
        return CustomerService(session).update(data,item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/",operation_id=f"{resource_name}_list")
def get_filtered(  session: SessionDep,filter = Depends(get_customer_filter_query))-> list [CustomerWithID]:
    return CustomerService(session).get_filtered(filter)
