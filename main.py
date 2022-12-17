from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from user_routers import products, token, receipts, custom
from admin_routers import admin_custom
app = FastAPI()

app.include_router(token.router)
app.include_router(products.router)
app.include_router(receipts.router)
app.include_router(custom.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>There is nothing here, to see api docs - please follow this link: <a href="http://10.9.179.156:8080/docs"> 
            docs</a></h1>
        </body>
    </html>
    """
