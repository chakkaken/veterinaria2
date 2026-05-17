import csv
import io
from datetime import datetime, timedelta
from django.db.models import Count, Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from ..models import Citas, Mascotas, Duenos, Doctores, Historias, Raza


class ReportService:
    """Servicio para generar reportes en PDF y CSV."""

    @staticmethod
    def get_estadisticas_generales():
        """Obtiene estadísticas generales del sistema."""
        now = datetime.now()
        mes_actual = now.month
        anio_actual = now.year
        
        citas_mes = Citas.objects.filter(
            fecha_cita__month=mes_actual,
            fecha_cita__year=anio_actual
        )
        
        stats = {
            'total_mascotas': Mascotas.objects.count(),
            'total_duenos': Duenos.objects.count(),
            'total_doctores': Doctores.objects.count(),
            'total_citas': Citas.objects.count(),
            'total_historias': Historias.objects.count(),
            'total_razas': Raza.objects.count(),
            'citas_pendientes': Citas.objects.filter(estado='pendiente').count(),
            'citas_confirmadas': Citas.objects.filter(estado='confirmada').count(),
            'citas_canceladas': Citas.objects.filter(estado='cancelada').count(),
            'citas_completadas': Citas.objects.filter(estado='completada').count(),
            'citas_mes_actual': citas_mes.count(),
            'citas_mes_pendientes': citas_mes.filter(estado='pendiente').count(),
            'citas_mes_completadas': citas_mes.filter(estado='completada').count(),
        }
        
        return stats

    @staticmethod
    def get_citas_por_estado():
        """Obtiene distribución de citas por estado."""
        return Citas.objects.values('estado').annotate(
            total=Count('IdCita')
        ).order_by('-total')

    @staticmethod
    def get_citas_por_doctor():
        """Obtiene cantidad de citas por doctor."""
        return Citas.objects.values(
            'doctor__Nombre',
            'doctor__Apellido'
        ).annotate(
            total=Count('IdCita')
        ).order_by('-total')[:10]

    @staticmethod
    def get_citas_por_mes():
        """Obtiene citas agrupadas por mes."""
        return Citas.objects.extra(
            select={'mes': "TO_CHAR(fecha_cita, 'YYYY-MM')"}
        ).values('mes').annotate(
            total=Count('IdCita')
        ).order_by('mes')[:12]

    @staticmethod
    def get_top_mascotas_frecuentes():
        """Obtiene las mascotas con más citas."""
        return Citas.objects.values(
            'mascota__nombre'
        ).annotate(
            total=Count('IdCita')
        ).order_by('-total')[:10]

    @staticmethod
    def get_citas_rango_fechas(fecha_inicio, fecha_fin):
        """Obtiene citas en un rango de fechas."""
        return Citas.objects.filter(
            fecha_cita__range=[fecha_inicio, fecha_fin]
        ).select_related('mascota', 'doctor', 'dueno').order_by('fecha_cita')

    @staticmethod
    def generar_pdf_citas(citas_queryset, titulo='Reporte de Citas'):
        """Genera un PDF con el listado de citas."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#6c63ff'),
            spaceAfter=10,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7b8099'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        elements.append(Paragraph('VetSystem', title_style))
        elements.append(Paragraph(titulo, subtitle_style))
        elements.append(Paragraph(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', subtitle_style))
        elements.append(Spacer(1, 20))

        data = [['#', 'Mascota', 'Dueño', 'Doctor', 'Fecha', 'Motivo', 'Estado']]
        
        for i, cita in enumerate(citas_queryset, 1):
            data.append([
                str(i),
                cita.mascota.nombre,
                f'{cita.dueno.Nombre} {cita.dueno.Apellido}',
                f'Dr. {cita.doctor.Nombre}',
                cita.fecha_cita.strftime('%d/%m/%Y %H:%M'),
                cita.motivo[:30],
                cita.get_estado_display()
            ])

        col_widths = [0.4*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c63ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 30))

        stats_style = ParagraphStyle(
            'StatsStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333'),
            alignment=TA_RIGHT
        )
        elements.append(Paragraph(f'Total de citas: {len(citas_queryset)}', stats_style))

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    @staticmethod
    def generar_pdf_estadisticas():
        """Genera un PDF con estadísticas generales."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#6c63ff'),
            spaceAfter=10,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7b8099'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        elements.append(Paragraph('VetSystem', title_style))
        elements.append(Paragraph('Reporte Estadístico General', subtitle_style))
        elements.append(Paragraph(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', subtitle_style))
        elements.append(Spacer(1, 20))

        stats = ReportService.get_estadisticas_generales()

        stats_data = [
            ['Métrica', 'Cantidad'],
            ['Total Mascotas', str(stats['total_mascotas'])],
            ['Total Dueños', str(stats['total_duenos'])],
            ['Total Doctores', str(stats['total_doctores'])],
            ['Total Citas', str(stats['total_citas'])],
            ['Total Historias Clínicas', str(stats['total_historias'])],
            ['Citas Pendientes', str(stats['citas_pendientes'])],
            ['Citas Confirmadas', str(stats['citas_confirmadas'])],
            ['Citas Completadas', str(stats['citas_completadas'])],
            ['Citas Canceladas', str(stats['citas_canceladas'])],
        ]

        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c63ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(stats_table)
        elements.append(Spacer(1, 30))

        citas_por_doctor = ReportService.get_citas_por_doctor()
        if citas_por_doctor:
            elements.append(Paragraph('Top Doctores por Citas', styles['Heading2']))
            elements.append(Spacer(1, 10))

            doctor_data = [['Doctor', 'Total Citas']]
            for doc_item in citas_por_doctor:
                doctor_data.append([
                    f"Dr. {doc_item['doctor__Nombre']} {doc_item['doctor__Apellido']}",
                    str(doc_item['total'])
                ])

            doctor_table = Table(doctor_data, colWidths=[4*inch, 1.5*inch])
            doctor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4ecdc4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f5')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            elements.append(doctor_table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    @staticmethod
    def generar_csv_citas(citas_queryset):
        """Genera un CSV con el listado de citas."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['ID', 'Mascota', 'Dueño', 'Doctor', 'Fecha', 'Motivo', 'Estado', 'Notas'])
        
        for cita in citas_queryset:
            writer.writerow([
                cita.IdCita,
                cita.mascota.nombre,
                f'{cita.dueno.Nombre} {cita.dueno.Apellido}',
                f'Dr. {cita.doctor.Nombre} {cita.doctor.Apellido}',
                cita.fecha_cita.strftime('%d/%m/%Y %H:%M'),
                cita.motivo,
                cita.get_estado_display(),
                cita.notas or ''
            ])
        
        return output.getvalue()

    @staticmethod
    def generar_csv_mascotas():
        """Genera un CSV con el listado de mascotas."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['ID', 'Nombre', 'Especie', 'Dueño', 'Raza'])
        
        mascotas = Mascotas.objects.select_related('dueno', 'raza').all()
        for mascota in mascotas:
            especie_text = mascota.otra_especie if mascota.especie == 'otro' else mascota.get_especie_display()
            writer.writerow([
                mascota.IdMascota,
                mascota.nombre,
                especie_text,
                f'{mascota.dueno.Nombre} {mascota.dueno.Apellido}',
                mascota.raza.nombre
            ])
        
        return output.getvalue()

    @staticmethod
    def generar_csv_duenos():
        """Genera un CSV con el listado de dueños."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['ID', 'Nombre', 'Apellido', 'Edad', 'Correo', 'Teléfono'])
        
        duenos = Duenos.objects.all()
        for dueno in duenos:
            writer.writerow([
                dueno.id,
                dueno.Nombre,
                dueno.Apellido,
                dueno.Edad,
                dueno.Correo,
                dueno.Telefono
            ])
        
        return output.getvalue()
