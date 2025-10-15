from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from io import BytesIO
from typing import List, Dict
from models import Ship, CreateShip

app = FastAPI(title="Ship Management Web")

ship_list = []

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/ships")
async def get_ships() -> List:
    return ship_list

@app.get("/ships/download_word")
async def export_ships_to_word():
    try:
        if not ship_list:
            raise HTTPException(status_code=404, detail="No ships available for export")
            
        doc = Document()
        doc.add_heading('Ship Fleet Report', 0)
        doc.add_paragraph(f"Total ships in fleet: {len(ship_list)}")
        doc.add_paragraph()

        for i, ship in enumerate(ship_list, 1):
            if i > 1:
                doc.add_paragraph("-" * 50)
                doc.add_paragraph()
            
            doc.add_heading(f'Ship #{ship.id}: {ship.name}', level=2)
            doc.add_paragraph(f"ID: {ship.id}")
            doc.add_paragraph(f"Ship Name: {ship.name}")
            doc.add_paragraph(f"Displacement: {ship.displacement} tons")
            doc.add_paragraph(f"Home Port: {ship.port}")
            doc.add_paragraph(f"Captain: {ship.captain}")
            doc.add_paragraph(f"Berth Number: {ship.berth_num}")
            doc.add_paragraph(f"Destination: {ship.target}")

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={'Content-Disposition': 'attachment; filename="ship_fleet_report.docx"'}
        )
    except Exception as e:
        print(f"Error in export_ships_to_word: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    
@app.get("/ships/download_excel")
async def export_ships_to_excel():
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Ship Information"

        # Добавляем название таблицы
        ws['A1'] = f"Ship Report"
        title_cell = ws['A1']
        title_cell.font = Font(size=14, bold=True)
        ws.merge_cells('A1:G1')  # Объединяем ячейки для заголовка
        ws.row_dimensions[1].height = 25  # Высота строки для заголовка

        current_row = 3

        # Добавляем заголовки таблицы
        headers = ["ID", "Ship Name", "Displacement", "Home Port", "Captain", "Berth Number", "Destination"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

        for ship in ship_list:
            # Добавляем данные корабля
            current_row += 1
            ship_data = [
                ship.id,
                ship.name,
                f"{ship.displacement} tons",
                ship.port,
                ship.captain,
                ship.berth_num,
                ship.target
            ]

            for col, value in enumerate(ship_data, 1):
                cell = ws.cell(row=current_row, column=col, value=value)
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )

            # Выравнивание заголовка по центру
            ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

            # Выравнивание всех ячеек по центру
            for row in ws.iter_rows(min_row=3, max_row=current_row):
                for cell in row:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = f"ships_report.xlsx"

        return Response(
            content=buffer.getvalue(),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )

        raise HTTPException(status_code=404, detail="Ship not found")
    except Exception as e:
        print(f"Error in export_ship_to_excel: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Excel report: {str(e)}")

@app.get("/ships/{ship_id}")
async def get_ship(ship_id: int) -> Ship:
    for ship in ship_list:
        if ship_id == ship.id:
            return ship
    raise HTTPException(status_code=404, detail="ship not found")

@app.post("/ships")
async def add_ship(ship: CreateShip) -> Ship:
    new_id = max([s.id for s in ship_list], default=0) + 1

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

@app.get("/ships/download_word/{ship_id}")
async def export_ship_to_word(ship_id: int):
    try:
        for ship in ship_list:
            if ship_id == ship.id:
                doc = Document()
                doc.add_heading(f'Ship Report: {ship.name}', 0)
                
                # Данные корабля
                ship_data = [
                    ("ID", str(ship.id)),
                    ("Ship Name", ship.name),
                    ("Displacement", f"{ship.displacement} tons"),
                    ("Home Port", ship.port),
                    ("Captain", ship.captain),
                    ("Berth Number", str(ship.berth_num)),
                    ("Destination", ship.target)
                ]
                
                for field, value in ship_data:
                    p = doc.add_paragraph()
                    p.add_run(f"{field}: ").bold = True
                    p.add_run(value)

                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                filename = f"ship_{ship.id}_report.docx"
                
                return Response(
                    content=buffer.getvalue(),
                    media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'}
                )
        
        raise HTTPException(status_code=404, detail="Ship not found")
    except Exception as e:
        print(f"Error in export_ship_to_word: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating ship report: {str(e)}")

@app.get("/ships/download_excel/{ship_id}")
async def export_ship_to_excel(ship_id: int):
    try:
        for ship in ship_list:
            if ship_id == ship.id:
                wb = Workbook()
                ws = wb.active
                ws.title = "Ship Information"

                # Добавляем название таблицы
                ws['A1'] = f"Ship Report: {ship.name}"
                title_cell = ws['A1']
                title_cell.font = Font(size=14, bold=True)
                ws.merge_cells('A1:G1')  # Объединяем ячейки для заголовка
                ws.row_dimensions[1].height = 25  # Высота строки для заголовка

                current_row = 3

                # Добавляем заголовки таблицы
                headers = ["ID", "Ship Name", "Displacement", "Home Port", "Captain", "Berth Number", "Destination"]
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=current_row, column=col, value=header)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
                    cell.border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )

                # Добавляем данные корабля
                current_row += 1
                ship_data = [
                    ship.id,
                    ship.name,
                    f"{ship.displacement} tons",
                    ship.port,
                    ship.captain,
                    ship.berth_num,
                    ship.target
                ]

                for col, value in enumerate(ship_data, 1):
                    cell = ws.cell(row=current_row, column=col, value=value)
                    cell.border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )

                # Выравнивание заголовка по центру
                ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

                # Выравнивание всех ячеек по центру
                for row in ws.iter_rows(min_row=3, max_row=current_row):
                    for cell in row:
                        cell.alignment = Alignment(horizontal='center', vertical='center')

                buffer = BytesIO()
                wb.save(buffer)
                buffer.seek(0)

                filename = f"ship_{ship.id}_report.xlsx"

                return Response(
                    content=buffer.getvalue(),
                    media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'}
                )

        raise HTTPException(status_code=404, detail="Ship not found")
    except Exception as e:
        print(f"Error in export_ship_to_excel: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Excel report: {str(e)}")