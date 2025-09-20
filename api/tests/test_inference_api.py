from fastapi.testclient import TestClient
from api.main import app
import numpy as np
import cv2
import io
import jwt

client = TestClient(app)


def make_token():
    from api.config import settings
    payload = {"sub": "tester", "role": "admin"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_inference_frame():
    # Create a blank JPEG image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', img)
    files = {'file': ('frame.jpg', io.BytesIO(buf.tobytes()), 'image/jpeg')}
    headers = {"Authorization": f"Bearer {make_token()}"}
    r = client.post("/inference/frame", files=files, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert 'result' in data
