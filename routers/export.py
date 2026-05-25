import io
import csv
import json
import xml.etree.ElementTree as ET
from fpdf import FPDF
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import models, schemas
from database import get_db

router = APIRouter(
    prefix="/export",
    tags=["Data Export"]
)

@router.get("/")
def export_weather_data(
    format: str = Query(..., description="Supported Formats: json, csv, xml, md, pdf"),
    ids: str = Query(None, description="IDs separated by comma. If empty, exports all."),
    db: Session = Depends(get_db)
):
    query = db.query(models.WeatherRecord)
    if ids:
        id_list = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip().isdigit()]
        if id_list:
            query = query.filter(models.WeatherRecord.id.in_(id_list))
    
    records = query.all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No records found for export.")

    format = format.lower()

    if format == "json":
        data = [schemas.WeatherResponse.model_validate(r).model_dump() for r in records]
        output = io.StringIO(json.dumps(data, indent=4, default=str))
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="application/json", 
            headers={"Content-Disposition": "attachment; filename=weather_export.json"}
        )

    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Location", "Start Date", "End Date", "Max Temp (°C)", "Min Temp (°C)"])
        for r in records:
            writer.writerow([r.id, r.location, r.start_date, r.end_date, r.temperature_max, r.temperature_min])
        
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=weather_export.csv"}
        )

    elif format == "xml":
        root = ET.Element("WeatherRecords")
        for r in records:
            record_xml = ET.SubElement(root, "Record")
            ET.SubElement(record_xml, "ID").text = str(r.id)
            ET.SubElement(record_xml, "Location").text = r.location
            ET.SubElement(record_xml, "StartDate").text = r.start_date
            ET.SubElement(record_xml, "EndDate").text = r.end_date
            ET.SubElement(record_xml, "MaxTemp").text = str(r.temperature_max)
            ET.SubElement(record_xml, "MinTemp").text = str(r.temperature_min)
            
        tree = ET.ElementTree(root)
        output = io.BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=True)
        output.seek(0)
        
        return StreamingResponse(
            output, 
            media_type="application/xml", 
            headers={"Content-Disposition": "attachment; filename=weather_export.xml"}
        )

    elif format == "md":
        md = "# Weather Data Export\n\n"
        md += "| ID | Location | Start Date | End Date | Max Temp | Min Temp |\n"
        md += "|---|---|---|---|---|---|\n"
        for r in records:
             md += f"| {r.id} | {r.location} | {r.start_date} | {r.end_date} | {r.temperature_max}°C | {r.temperature_min}°C |\n"
        
        return StreamingResponse(
            iter([md]), 
            media_type="text/markdown", 
            headers={"Content-Disposition": "attachment; filename=weather_export.md"}
        )

    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=16)
        pdf.cell(200, 10, txt="Weather Records Export", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("helvetica", size=10)
        for r in records:
            txt = f"ID: {r.id} | Loc: {r.location} | {r.start_date} to {r.end_date} | Max: {r.temperature_max}C | Min: {r.temperature_min}C"
            pdf.cell(200, 8, txt=txt, ln=True)
            
        pdf_bytes = pdf.output()
        return StreamingResponse(
            io.BytesIO(pdf_bytes), 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=weather_export.pdf"}
        )

    else:
        raise HTTPException(status_code=400, detail="Format not supported.")