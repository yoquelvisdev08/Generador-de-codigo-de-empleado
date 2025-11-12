"""
Utilidades para generar templates HTML de ejemplo
"""
from pathlib import Path


def generar_html_ejemplo() -> str:
    """
    Genera un HTML de ejemplo para carnet con todas las variables disponibles
    
    Returns:
        String con el HTML de ejemplo
    """
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carnet de Empleado</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            width: 637px;
            height: 1010px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            flex: 1;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .photo-section {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .photo {
            width: 120px;
            height: 150px;
            background: #f0f0f0;
            border: 3px solid #667eea;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            overflow: hidden;
        }
        
        .photo img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .info {
            flex: 1;
        }
        
        .info h2 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .info p {
            color: #666;
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .info .id {
            font-weight: bold;
            color: #667eea;
            font-size: 18px;
        }
        
        .barcode-section {
            margin-top: auto;
            text-align: center;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
        }
        
        .barcode-section img {
            max-width: 100%;
            height: auto;
            margin-bottom: 10px;
        }
        
        .barcode-section .code {
            font-family: 'Courier New', monospace;
            font-size: 16px;
            color: #333;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 12px;
        }
        
        .company {
            font-weight: bold;
            font-size: 18px;
        }
        
        .website {
            margin-top: 5px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{empresa}}</h1>
        <p>Credencial de Empleado</p>
    </div>
    
    <div class="content">
        <div class="photo-section">
            <div class="photo">
                {{#if foto}}
                <img src="{{foto}}" alt="Foto del empleado">
                {{else}}
                <span style="color: #999; font-size: 12px;">Sin foto</span>
                {{/if}}
            </div>
            <div class="info">
                <h2>{{nombre}}</h2>
                <p><strong>Cédula:</strong> {{cedula}}</p>
                <p><strong>Cargo:</strong> {{cargo}}</p>
                <p class="id">ID: {{id_unico}}</p>
            </div>
        </div>
        
        <div class="barcode-section">
            {{#if codigo_barras}}
            <img src="{{codigo_barras}}" alt="Código de barras">
            {{else}}
            <div style="height: 80px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; border-radius: 5px;">
                <span style="color: #999;">Código de barras</span>
            </div>
            {{/if}}
            <div class="code">{{id_unico}}</div>
        </div>
    </div>
    
    <div class="footer">
        <div class="company">{{empresa}}</div>
        <div class="website">{{web}}</div>
    </div>
</body>
</html>"""
    
    # Versión simplificada sin Handlebars (solo {{variable}})
    html_simple = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carnet de Empleado</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            width: 637px;
            height: 1010px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            flex: 1;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .photo-section {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .photo {
            width: 120px;
            height: 150px;
            background: #f0f0f0;
            border: 3px solid #667eea;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            overflow: hidden;
        }
        
        .photo img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .info {
            flex: 1;
        }
        
        .info h2 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .info p {
            color: #666;
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .info .id {
            font-weight: bold;
            color: #667eea;
            font-size: 18px;
        }
        
        .barcode-section {
            margin-top: auto;
            text-align: center;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
        }
        
        .barcode-section img {
            max-width: 100%;
            height: auto;
            margin-bottom: 10px;
        }
        
        .barcode-section .code {
            font-family: 'Courier New', monospace;
            font-size: 16px;
            color: #333;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 12px;
        }
        
        .company {
            font-weight: bold;
            font-size: 18px;
        }
        
        .website {
            margin-top: 5px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{empresa}}</h1>
        <p>Credencial de Empleado</p>
    </div>
    
    <div class="content">
        <div class="photo-section">
            <div class="photo">
                <img src="{{foto}}" alt="Foto del empleado" onerror="this.style.display='none'; this.parentElement.innerHTML='<span style=\\'color: #999; font-size: 12px;\\'>Sin foto</span>';">
            </div>
            <div class="info">
                <h2>{{nombre}}</h2>
                <p><strong>Cédula:</strong> {{cedula}}</p>
                <p><strong>Cargo:</strong> {{cargo}}</p>
                <p class="id">ID: {{id_unico}}</p>
            </div>
        </div>
        
        <div class="barcode-section">
            <img src="{{codigo_barras}}" alt="Código de barras" onerror="this.style.display='none';">
            <div class="code">{{id_unico}}</div>
        </div>
    </div>
    
    <div class="footer">
        <div class="company">{{empresa}}</div>
        <div class="website">{{web}}</div>
    </div>
</body>
</html>"""
    
    return html_simple

