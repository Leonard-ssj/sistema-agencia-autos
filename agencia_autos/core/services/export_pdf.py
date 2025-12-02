"""
Servicio para exportar reportes a PDF con formato profesional
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.http import HttpResponse
from datetime import datetime
from decimal import Decimal


def exportar_disponibilidad_pdf(datos, filtros=None):
    """
    Exporta el reporte de disponibilidad a PDF profesional
    """
    response = HttpResponse(content_type='application/pdf')
    filename = f'reporte_disponibilidad_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Crear documento
    doc = SimpleDocTemplate(response, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Contenedor de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph("REPORTE DE DISPONIBILIDAD DE VEHÍCULOS", title_style)
    elements.append(title)
    
    # Fecha de generación
    fecha_style = ParagraphStyle(
        'Fecha',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    fecha_text = f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}"
    elements.append(Paragraph(fecha_text, fecha_style))
    elements.append(Spacer(1, 20))
    
    # Filtros aplicados
    if filtros:
        filtros_text = "<b>Filtros aplicados:</b><br/>"
        if filtros.get('fecha_desde') or filtros.get('fecha_hasta'):
            filtros_text += f"Período: {filtros.get('fecha_desde', 'Inicio')} - {filtros.get('fecha_hasta', 'Hoy')}<br/>"
        if filtros.get('marca'):
            filtros_text += f"Marca: {filtros['marca']}<br/>"
        if filtros.get('tipo'):
            filtros_text += f"Tipo: {filtros['tipo']}<br/>"
        
        elements.append(Paragraph(filtros_text, styles['Normal']))
        elements.append(Spacer(1, 20))
    
    # Tabla de datos
    if datos:
        # Encabezados
        table_data = [['Marca', 'Tipo de Vehículo', 'Cantidad', 'Precio Promedio']]
        
        # Datos
        total_cantidad = 0
        total_precio = Decimal('0')
        
        for dato in datos:
            cantidad = dato['cantidad_disponible']
            precio = Decimal(str(dato['precio_promedio']))
            total_cantidad += cantidad
            total_precio += precio
            
            table_data.append([
                dato['marca'],
                dato['tipo_vehiculo'],
                str(cantidad),
                f"${precio:,.2f}"
            ])
        
        # Fila de totales
        promedio_precio = total_precio / len(datos) if datos else Decimal('0')
        table_data.append([
            'TOTAL',
            '',
            str(total_cantidad),
            f"${promedio_precio:,.2f}"
        ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[2*inch, 2.5*inch, 1.2*inch, 1.5*inch])
        
        # Estilo de tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Cantidad centrada
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Precio a la derecha
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('TOPPADDING', (0, 1), (-1, -2), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
            
            # Fila de totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No hay datos disponibles para mostrar.", styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    return response


def exportar_ventas_pdf(datos, filtros=None):
    """
    Exporta el reporte de ventas a PDF profesional
    """
    response = HttpResponse(content_type='application/pdf')
    filename = f'reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Crear documento
    doc = SimpleDocTemplate(response, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#28A745'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    title = Paragraph("REPORTE DE VENTAS", title_style)
    elements.append(title)
    
    # Fecha
    fecha_style = ParagraphStyle(
        'Fecha',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    fecha_text = f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}"
    elements.append(Paragraph(fecha_text, fecha_style))
    elements.append(Spacer(1, 20))
    
    # Filtros
    if filtros:
        filtros_text = "<b>Filtros aplicados:</b><br/>"
        if filtros.get('fecha_desde') or filtros.get('fecha_hasta'):
            filtros_text += f"Período: {filtros.get('fecha_desde', 'Inicio')} - {filtros.get('fecha_hasta', 'Hoy')}<br/>"
        
        elements.append(Paragraph(filtros_text, styles['Normal']))
        elements.append(Spacer(1, 20))
    
    # Tabla
    if datos:
        table_data = [['ID', 'Fecha', 'Cliente', 'Total', 'Estado']]
        
        total_ventas = Decimal('0')
        
        for venta in datos:
            total = Decimal(str(venta.total_venta))
            total_ventas += total
            
            table_data.append([
                str(venta.id),
                venta.fecha_venta.strftime('%d/%m/%Y'),
                venta.cliente.nombre_completo[:30],  # Truncar si es muy largo
                f"${total:,.2f}",
                venta.estado_venta
            ])
        
        # Totales
        table_data.append([
            '',
            '',
            'TOTAL',
            f"${total_ventas:,.2f}",
            ''
        ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[0.6*inch, 1*inch, 2.5*inch, 1.2*inch, 1*inch])
        
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28A745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('TOPPADDING', (0, 1), (-1, -2), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
            
            # Totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No hay ventas para mostrar.", styles['Normal']))
    
    doc.build(elements)
    return response
