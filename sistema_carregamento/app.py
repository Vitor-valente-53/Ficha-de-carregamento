import streamlit as st
import sqlite3
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Carregamento", page_icon="🚛", layout="wide")


# Criar pasta para salvar PDFs se não existir
if not os.path.exists("gerados"):
    os.makedirs("gerados")

# --- BANCO DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect("historico.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fichas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_registro TEXT,
            origem TEXT,
            destino TEXT,
            motorista TEXT,
            data_carregamento TEXT,
            placa_cavalo TEXT,
            placa_carreta TEXT,
            placa_truck TEXT,
            equipe TEXT,
            qtd_modulos TEXT,
            palletes_pbr TEXT,
            palletes_descartaveis TEXT,
            outros TEXT,
            bau_limpo TEXT,
            bau_adequado TEXT,
            motivo_negativo TEXT,
            qtd_cte TEXT,
            num_isca TEXT,
            assinatura TEXT,
            obs TEXT,
            pdf_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- FUNÇÃO PARA GERAR O PDF ---
def gerar_pdf(dados, filename):
    filepath = os.path.join("gerados", filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=14, alignment=1, spaceAfter=10)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=9, leading=12)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=9, leading=11)
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold')

    # Cabeçalho Oficial
    header_data = [
        [Paragraph("<b>ATIVA TRANS LOG</b>", title_style), Paragraph("<b>Relatório de Carregamento</b><br/>FOR-OP-TRA-003", title_style)]
    ]
    t_header = Table(header_data, colWidths=[250, 300])
    t_header.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 10))

    # Tabela 1: Dados do Transporte
    dados_transporte = [
        [Paragraph("<b>Origem:</b> " + dados['origem'], cell_style), Paragraph("<b>Destino:</b> " + dados['destino'], cell_style)],
        [Paragraph("<b>Motorista:</b> " + dados['motorista'], cell_style), Paragraph("<b>Data:</b> " + dados['data_carregamento'], cell_style)],
        [Paragraph("<b>Placa Cavalo:</b> " + dados['placa_cavalo'], cell_style), Paragraph("<b>Placa Carreta:</b> " + dados['placa_carreta'], cell_style)],
        [Paragraph("<b>Placa Truck:</b> " + dados['placa_truck'], cell_style), Paragraph("<b>Equipe:</b> " + dados['equipe'], cell_style)],
    ]
    t_trans = Table(dados_transporte, colWidths=[275, 275])
    t_trans.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_trans)
    story.append(Spacer(1, 10))

    # Tabela 2: Quantidades
    dados_qtd = [
        [Paragraph("<b>Quantidade / Módulos:</b> " + dados['qtd_modulos'], cell_style), Paragraph("<b>Palletes PBR:</b> " + dados['palletes_pbr'], cell_style)],
        [Paragraph("<b>Palletes Descartáveis:</b> " + dados['palletes_descartaveis'], cell_style), Paragraph("<b>Outros:</b> " + dados['outros'], cell_style)]
    ]
    t_qtd = Table(dados_qtd, colWidths=[275, 275])
    t_qtd.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_qtd)
    story.append(Spacer(1, 10))

    # Tabela 3: Verificação de Limpeza
    dados_v = [
        [Paragraph("<b>Verificação de Limpeza e Situação dos Veículos</b>", cell_bold), ""],
        [Paragraph("O baú está limpo?", cell_style), Paragraph(dados['bau_limpo'], cell_bold)],
        [Paragraph("O baú está adequado para efetuar o serviço?", cell_style), Paragraph(dados['bau_adequado'], cell_bold)],
        [Paragraph("Caso negativo, informar motivo:", cell_style), Paragraph(dados['motivo_negativo'], cell_style)]
    ]
    t_v = Table(dados_v, colWidths=[350, 200])
    t_v.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_v)
    story.append(Spacer(1, 10))

    # Tabela 4: Outros e Observações
    dados_outros = [
        [Paragraph("<b>Quantidade de CTE:</b> " + dados['qtd_cte'], cell_style), Paragraph("<b>Número de Isca:</b> " + dados['num_isca'], cell_style)],
        [Paragraph("<b>Assinatura do Responsável:</b> " + dados['assinatura'], cell_style), ""]
    ]
    t_outros = Table(dados_outros, colWidths=[275, 275])
    t_outros.setStyle(TableStyle([
        ('SPAN', (0,1), (1,1)),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_outros)
    story.append(Spacer(1, 10))

    # OBS
    obs_table = [
        [Paragraph("<b>OBS (Observações):</b>", cell_bold)],
        [Paragraph(dados['obs'].replace('\n', '<br/>'), cell_style)]
    ]
    t_obs = Table(obs_table, colWidths=[550])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.lightgrey),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_obs)

    doc.build(story)
    return filepath

# --- NAVEGAÇÃO DA INTERFACE ---
aba1, aba2 = st.tabs(["📝 Novo Preenchimento", "📜 Histórico de Fichas"])

with aba1:
    st.title("🚛 Ficha de Carregamento - Manifesto")
    st.caption("Preencha os campos abaixo para gerar o PDF e registrar no banco de dados.")

    with st.form("form_carregamento"):
        st.subheader("1. Informações de Transporte")
        col1, col2 = st.columns(2)
        with col1:
            origem = st.text_input("Origem")
            motorista = st.text_input("Motorista")
            placa_cavalo = st.text_input("Placa Cavalo")
            placa_truck = st.text_input("Placa Truck")
        with col2:
            destino = st.text_input("Destino")
            data_carregamento = st.date_input("Data do Carregamento").strftime("%d/%m/%Y")
            placa_carreta = st.text_input("Placa Carreta")
            equipe = st.text_input("Equipe")

        st.subheader("2. Quantidades de Carga")
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            qtd_modulos = st.text_input("Módulos")
        with col4:
            palletes_pbr = st.text_input("Palletes PBR")
        with col5:
            palletes_descartaveis = st.text_input("Palletes Descartáveis")
        with col6:
            outros = st.text_input("Outros")

        st.subheader("3. Verificação do Veículo")
        col7, col8 = st.columns(2)
        with col7:
            bau_limpo = st.radio("O baú está limpo?", ["Sim", "Não"], horizontal=True)
        with col8:
            bau_adequado = st.radio("O baú está adequado para efetuar o serviço?", ["Sim", "Não"], horizontal=True)
        
        motivo_negativo = st.text_input("Caso negativo, informar motivo:")

        st.subheader("4. Controle e Assinatura")
        col9, col10, col11 = st.columns(3)
        with col9:
            qtd_cte = st.text_input("Quantidade de CTE")
        with col10:
            num_isca = st.text_input("Número de Isca")
        with col11:
            assinatura = st.text_input("Assinatura do Responsável")

        st.subheader("5. Observações")
        obs = st.text_area("OBS (Observações gerais do carregamento)", height=100)

        submitted = st.form_submit_button("💾 Salvar e Gerar PDF", use_container_width=True)

    if submitted:
        dados = {
            "origem": origem, "destino": destino, "motorista": motorista,
            "data_carregamento": data_carregamento, "placa_cavalo": placa_cavalo,
            "placa_carreta": placa_carreta, "placa_truck": placa_truck, "equipe": equipe,
            "qtd_modulos": qtd_modulos, "palletes_pbr": palletes_pbr,
            "palletes_descartaveis": palletes_descartaveis, "outros": outros,
            "bau_limpo": bau_limpo, "bau_adequado": bau_adequado,
            "motivo_negativo": motivo_negativo, "qtd_cte": qtd_cte,
            "num_isca": num_isca, "assinatura": assinatura, "obs": obs
        }
        
        data_hora_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"Ficha_{data_hora_str}.pdf"
        
        # Gerar o arquivo PDF
        pdf_path = gerar_pdf(dados, pdf_filename)
        
        # Salvar no banco de dados SQLite
        conn = sqlite3.connect("historico.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fichas (
                data_registro, origem, destino, motorista, data_carregamento,
                placa_cavalo, placa_carreta, placa_truck, equipe, qtd_modulos,
                palletes_pbr, palletes_descartaveis, outros, bau_limpo, bau_adequado,
                motivo_negativo, qtd_cte, num_isca, assinatura, obs, pdf_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime("%d/%m/%Y %H:%M"), origem, destino, motorista, data_carregamento,
            placa_cavalo, placa_carreta, placa_truck, equipe, qtd_modulos,
            palletes_pbr, palletes_descartaveis, outros, bau_limpo, bau_adequado,
            motivo_negativo, qtd_cte, num_isca, assinatura, obs, pdf_path
        ))
        conn.commit()
        conn.close()

        st.success("✅ Ficha registrada com sucesso!")
        
        # Botão de Download do PDF imediato
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Baixar PDF para Imprimir",
                data=f,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )

with aba2:
    st.title("📜 Histórico de Fichas Emitidas")
    
    conn = sqlite3.connect("historico.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_registro, motorista, origem, destino, data_carregamento, pdf_path FROM fichas ORDER BY id DESC")
    registros = cursor.fetchall()
    conn.close()

    if registros:
        for reg in registros:
            r_id, r_data_reg, r_motorista, r_origem, r_destino, r_data_carr, r_pdf = reg
            with st.expander(f"📌 Ficha #{r_id} | Motorista: {r_motorista} | Data: {r_data_carr}"):
                st.write(f"**Registrado em:** {r_data_reg}")
                st.write(f"**Rota:** {r_origem} ➔ {r_destino}")
                
                if os.path.exists(r_pdf):
                    with open(r_pdf, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Rebaixar PDF #{r_id}",
                            data=f,
                            file_name=os.path.basename(r_pdf),
                            mime="application/pdf",
                            key=f"btn_{r_id}"
                        )
                else:
                    st.warning("Arquivo PDF não localizado na pasta local.")
    else:
        st.info("Nenhuma ficha registrada no histórico até o momento.")
