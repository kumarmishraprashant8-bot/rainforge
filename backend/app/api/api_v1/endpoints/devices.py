from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.pki_service import get_pki_service

router = APIRouter()

class DeviceProvisionRequest(BaseModel):
    device_id: str
    mac_address: str
    installer_id: str

class DeviceProvisionResponse(BaseModel):
    device_id: str
    cert_pem: str
    key_pem: str
    expires: str
    status: str = "provisioned"

@router.post("/provision", response_model=DeviceProvisionResponse)
async def provision_device(request: DeviceProvisionRequest):
    """
    Provision a new IoT device with mTLS certificates.
    In a real scenario, this endpoint would be protected by Admin/Installer generic auth.
    """
    service = get_pki_service()
    try:
        data = service.generate_device_cert(request.device_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
