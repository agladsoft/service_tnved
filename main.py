import uvicorn
from service_alta_tnved import *
from fastapi import Request
from fastapi import FastAPI


app: FastAPI = FastAPI()


@app.post("/")
async def main(request: Request):
    response: dict = await request.json()
    tnved: ServiceAltaTNVED = ServiceAltaTNVED(response)
    return tnved.main()


@app.get("/get_ip_address")
async def test(request: Request):
    print(request.headers)
    print(request.client)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
