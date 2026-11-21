#!/usr/bin/env python3.12
"""Arma el .docx de la Actividad 2.3: md2docx, captura insertada, viñetas y
numeración nativas de Word, y referencias juntas con sangría francesa."""
import os
import re
import shutil
import subprocess
import zipfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from PIL import Image

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WORK = '/home/daniel/.hermes/profiles/otto/workspace/Entornos_2.3_Heroku'
MD = os.path.join(WORK, 'Actividad_2.3_Ambientes_Efimeros.md')
DOCX = os.path.join(WORK, 'Actividad_2.3_Ambientes_Efimeros.docx')
PNG = os.path.join(WORK, 'captura_app.png')
TEMPLATE = '/home/daniel/.hermes/profiles/otto/attachments/Plantilla_Tarea_Escolar.docx'
ANCLA_FIGURA = 'La página responde con los datos del contenedor'

NUMBERING_XML = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="{W}">
  <w:abstractNum w:abstractNumId="0">
    <w:multiLevelType w:val="hybridMultilevel"/>
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="bullet"/>
      <w:lvlText w:val="•"/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
      <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="1">
    <w:multiLevelType w:val="hybridMultilevel"/>
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1."/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
      <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
  <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>
'''


def convertir_md():
    subprocess.run(['python3.12',
                    '/home/daniel/.hermes/profiles/otto/skills/productivity/md2docx/scripts/md2docx.py',
                    MD, DOCX, '--template', TEMPLATE], check=True)


def figura_y_referencias():
    doc = Document(DOCX)

    ancla = None
    for p in doc.paragraphs:
        if p.text.strip().startswith(ANCLA_FIGURA):
            ancla = p
            break
    if ancla is None:
        raise SystemExit('ERROR: no se encontró el párrafo ancla de la figura')

    with Image.open(PNG) as im:
        ancho_px, alto_px = im.size
    ancho = Cm(14.0)
    alto = Cm(14.0 * alto_px / ancho_px)

    fig = doc.add_paragraph()
    fig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fig.paragraph_format.space_before = Cm(0.3)
    fig.paragraph_format.space_after = Cm(0)
    fig.paragraph_format.keep_together = True
    ancla.paragraph_format.keep_with_next = True
    fig.add_run().add_picture(PNG, width=ancho, height=alto)
    ancla._p.addnext(fig._p)

    ref_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() == 'referencias':
            ref_idx = i
            break
    if ref_idx is None:
        raise SystemExit('ERROR: no se encontró el encabezado Referencias')

    doc.paragraphs[ref_idx].paragraph_format.page_break_before = True

    for p in doc.paragraphs[:ref_idx]:
        texto = p.text.strip()
        if len(texto) > 120:
            p.paragraph_format.keep_together = True
        # los encabezados del cuerpo llegan en negrita y sin punto final: no
        # deben quedarse solos al pie de la hoja
        if texto and len(texto) < 80 and p.runs and all(r.bold for r in p.runs if r.text.strip()):
            p.paragraph_format.keep_with_next = True

    for p in doc.paragraphs:
        if p.text.strip() == 'Verificación del despliegue':
            p.paragraph_format.keep_with_next = True

    n_ref = 0
    for p in doc.paragraphs[ref_idx + 1:]:
        if not p.text.strip():
            continue
        pPr = p._p.find(qn('w:pPr'))
        if pPr is None:
            pPr = OxmlElement('w:pPr')
            p._p.insert(0, pPr)
        for old in pPr.findall(qn('w:ind')):
            pPr.remove(old)
        ind = OxmlElement('w:ind')
        ind.set(qn('w:left'), '720')
        ind.set(qn('w:hanging'), '720')
        pPr.append(ind)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        n_ref += 1

    doc.save(DOCX)
    print(f'OK: figura insertada a {ancho.cm:.1f} cm y sangría francesa en {n_ref} referencias')


def numeracion_nativa(path):
    with zipfile.ZipFile(path) as zin:
        items = {n: zin.read(n) for n in zin.namelist()}
        order = zin.namelist()

    doc_xml = items['word/document.xml'].decode('utf-8')

    def fix(m):
        bloque = m.group(0)
        if '>• <' in bloque:
            bloque = re.sub(r'<w:r>(?:(?!<w:r>)[\s\S])*?<w:t[^>]*>• </w:t></w:r>', '', bloque, count=1)
            return bloque.replace(
                '<w:ind w:left="720" w:hanging="360"/>',
                '<w:ind w:left="720" w:hanging="360"/>'
                '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>', 1)
        if re.search(r'<w:t[^>]*>\d+\. </w:t>', bloque):
            bloque = re.sub(r'<w:r>(?:(?!<w:r>)[\s\S])*?<w:t[^>]*>\d+\. </w:t></w:r>', '', bloque, count=1)
            return bloque.replace(
                '<w:ind w:left="720" w:hanging="360"/>',
                '<w:ind w:left="720" w:hanging="360"/>'
                '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>', 1)
        return bloque

    nuevo = re.sub(r'<w:p>[\s\S]*?</w:p>', fix, doc_xml)
    print('viñetas sueltas restantes:', nuevo.count('>• <'),
          '| números sueltos:', len(re.findall(r'>\d+\. </w:t>', nuevo)))
    items['word/document.xml'] = nuevo.encode('utf-8')

    ct = items['[Content_Types].xml'].decode('utf-8')
    if '/word/numbering.xml' not in ct:
        ct = ct.replace('</Types>',
                        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.'
                        'openxmlformats-officedocument.wordprocessingml.numbering+xml"/></Types>')
        items['[Content_Types].xml'] = ct.encode('utf-8')

    rels_name = 'word/_rels/document.xml.rels'
    rels = items[rels_name].decode('utf-8')
    if 'numbering.xml' not in rels:
        usados = {int(i) for i in re.findall(r'Id="rId(\d+)"', rels)}
        rid = f'rId{max(usados) + 1 if usados else 1}'
        rels = rels.replace('</Relationships>',
                            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                            f'officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
                            '</Relationships>')
        items[rels_name] = rels.encode('utf-8')

    items['word/numbering.xml'] = NUMBERING_XML.encode('utf-8')
    if 'word/numbering.xml' not in order:
        order.append('word/numbering.xml')

    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for nombre in order:
            zout.writestr(nombre, items[nombre])
    shutil.move(tmp, path)


def a_pdf():
    # LibreOffice de snap no puede leer rutas ocultas: se convierte en una
    # carpeta visible y el PDF se copia de vuelta a la carpeta de la actividad.
    salida = '/home/daniel/udg_render/entornos23'
    os.makedirs(salida, exist_ok=True)
    visible = os.path.join(salida, os.path.basename(DOCX))
    shutil.copy(DOCX, visible)
    pdf_visible = os.path.join(salida, 'Actividad_2.3_Ambientes_Efimeros.pdf')
    if os.path.exists(pdf_visible):
        os.remove(pdf_visible)
    subprocess.run(['/snap/bin/libreoffice', '--headless', '--norestore',
                    f'-env:UserInstallation=file:///tmp/lo_23_{os.getpid()}',
                    '--convert-to', 'pdf', '--outdir', salida, visible],
                   check=True, capture_output=True, timeout=280)
    destino = os.path.join(WORK, 'render')
    os.makedirs(destino, exist_ok=True)
    pdf = os.path.join(destino, 'Actividad_2.3_Ambientes_Efimeros.pdf')
    shutil.copy(pdf_visible, pdf)
    return pdf


if __name__ == '__main__':
    convertir_md()
    figura_y_referencias()
    numeracion_nativa(DOCX)
    pdf = a_pdf()
    print('PDF:', pdf)
