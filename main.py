from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from models import Ship, CreateShip

app = FastAPI(title="Ship Management  Web")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

ship_list = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ships")
async def get_ships() -> List:
    return ship_list

@app.get("/ships/{ship_id}")
async def get_ship(ship_id: int) -> Ship:
    for ship in ship_list:
        if ship_id == ship.id:
            return ship
    raise HTTPException(status_code=404, detail="ship not found")

@app.post("/ships")
async def add_ship(ship: CreateShip) -> Ship:
    new_id = len(ship_list) + 1

    ship_response = Ship(id=new_id,
                         name=ship.name,
                         displacement=ship.displacement,
                         port=ship.port,
                         captain=ship.captain,
                         berth_num=ship.berth_num,
                         target=ship.target)
    
    ship_list.append(ship_response)

    return ship_response

@app.put("/ships/{ship_id}")
async def edit_ship(ship_id: int, ship_data: CreateShip) -> Ship:
    for index, ship in enumerate(ship_list):  
        if ship_id == ship.id:
            edit_ship = Ship(
                id=ship.id,  
                name=ship_data.name,
                displacement=ship_data.displacement,
                port=ship_data.port,
                captain=ship_data.captain,
                berth_num=ship_data.berth_num,
                target=ship_data.target
            )
            
            ship_list[index] = edit_ship
            return edit_ship 
    raise HTTPException(status_code=404, detail="ship not found")

@app.delete("/ships/{ship_id}")  
async def delete_ship(ship_id: int) -> Dict:
    for index, ship in enumerate(ship_list): 
        if ship_id == ship.id:
            del ship_list[index] 
            return {"data": "ship deleted"} 
        
    raise HTTPException(status_code=404, detail="ship not found")