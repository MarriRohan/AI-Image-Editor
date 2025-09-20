from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from typing import Optional, Dict, Any
from api.api_logic import process_frame_and_store, send_e_challan
from api.auth import get_current_user

router = APIRouter()

@router.post("/frame")
async def inference_frame(
    file: UploadFile = File(...),
    pixel_per_meter: Optional[float] = None,
    fps: Optional[float] = None,
    signal_state: Optional[str] = None,
    stop_line_y: Optional[int] = None,
    user=Depends(get_current_user),
):
    meta: Dict[str, Any] = {}
    if pixel_per_meter: meta["pixel_per_meter"] = pixel_per_meter
    if fps: meta["fps"] = fps
    if signal_state: meta["signal_state"] = signal_state
    if stop_line_y is not None: meta["stop_line_y"] = stop_line_y

    data = await file.read()
    result = process_frame_and_store(data, meta=meta)

    # Multi-stage verification example
    verified = []
    for v in result.get("violations", []):
        conf_ok = v["score"] >= 0.4
        plate_ok = (result.get("plate", {}).get("confidence", 0) >= 0.5) if result.get("plate") else False
        if conf_ok and plate_ok:
            verified.append(v)

    challan_result = None
    if verified:
        challan_payload = {
            "violations": verified,
            "plate": result.get("plate"),
            "evidence": result.get("evidence"),
        }
        challan_result = send_e_challan(challan_payload)

    return {"result": result, "verified": verified, "challan": challan_result}
