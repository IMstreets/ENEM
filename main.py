import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns
import os
import json
import requests
from io import BytesIO
import re

st.title("Gerador de Compilado de Questões ENEM")

# Entradas
ano = st.selectbox(
    "Ano da prova",
    (
        "2009",
        "2010",
        "2011",
        "2012",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018",
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
    ),
)
materia = st.selectbox(
    "Matéria",
    [
        "MT - Matemática",
        "CN - Ciências da Natureza",
        "CH - Ciências Humanas",
        "LC - Linguagens",
    ],
)
posicoes = st.text_input(
    "Número das questões (separadas por espaço)", placeholder="Ex: 109,110"
)

dificuldade_minima = st.slider("Dificuldade Mínima (Coloque 0 para a menor dificuldade possível)",-10000, 10000, 300)
dificuldade_maxima = st.slider("Dificuldade Máxima",-10000, 10000, 1000)

# Caminhos
pasta_csv = r"base-de-dados-CSV"
base_json = os.path.join(r"enem-api\public")

if st.button("Gerar DOCX"):
    arquivo_csv = os.path.join(pasta_csv, f"ITENS_PROVA_{ano}.csv")

    if not os.path.exists(arquivo_csv):
        st.error(f"Arquivo {arquivo_csv} não encontrado!")
    else:
        df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1")
        posicoes_lista = [
            int(p.strip()) for p in posicoes.split() if p.strip().isdigit()
        ]

        # Se a lista estiver vazia, pegar todas as posições da matéria
        if not posicoes_lista:
            df_filtrado = df[df["SG_AREA"] == materia[:2]]  # filtra pela matéria
            posicoes_lista = df_filtrado["CO_POSICAO"].unique().tolist()

        # Filtrar por matéria e posição
        

        filtro = df[
        (df["SG_AREA"] == materia[:2]) & (df["CO_POSICAO"].isin(posicoes_lista))
                ].drop_duplicates(subset=["CO_POSICAO"])

        # Reordena as linhas de acordo com a ordem fornecida pelo usuário
        filtro["CO_POSICAO"] = pd.Categorical(filtro["CO_POSICAO"], categories=posicoes_lista, ordered=True)
        filtro = filtro.sort_values("CO_POSICAO")

        # Cria a numeração sequencial (1, 2, 3, …)
        filtro = filtro.reset_index(drop=True)
        filtro["NUMERO_QUESTAO"] = filtro.index + 1

        if filtro.empty:
            st.warning("Nenhuma questão encontrada.")
        else:
            doc = Document()
            

            #Configurações do documento
            
            #1 Definição de fonte padrão
            style = doc.styles["Normal"]
            font = style.font
            font.name = "Calibri"
            font.size = Pt(11)


            #Definindo espaçamento e alinhamento justificado para parágrafos

            for style_name in ["Normal", "Heading 1", "Heading 2"]:
                style = doc.styles[style_name]
                style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # ---- CONFIGURAR COLUNAS ----

            #Número de Colunas

            seção = doc.sections[0]
            sectPr = seção._sectPr
            seção.top_margin = Cm(1)
            seção.bottom_margin = Cm(2.5)
            seção.left_margin = Cm(1)
            seção.right_margin = Cm(1)

            for child in sectPr.findall(ns.qn("w:cols")):
                sectPr.remove(child)
            
            cols = OxmlElement("w:cols")
            cols.set(ns.qn("w:num"), "2")
            cols.set(ns.qn("w:space"), "200")
            sectPr.append(cols)

            for idx,(_,linha) in enumerate(filtro.iterrows(),start=1):
                questao_num = linha["CO_POSICAO"]
                
                if linha["CO_HABILIDADE"] != "":
                    habilidade = float(linha["CO_HABILIDADE"])
                nota = linha["NU_PARAM_B"]

                caminho_json = os.path.join(
                    base_json, str(ano), "questions", str(questao_num), "details.json"
                )

                if not os.path.exists(caminho_json):
                    st.warning(f"JSON não encontrado: {caminho_json}")
                    continue

                with open(caminho_json, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                # Título e enunciado
                par = doc.add_paragraph()
                run = par.add_run()
                run.bold = True
                

                par.add_run(
                    f"{idx}. ({questao_num} - ENEM {ano}) (H{habilidade:.0f} - {nota})",None).bold = True
               
                
                if dados.get("context"):
                    # Regex para pegar imagens em markdown ![](url)
                    pattern = r'!\[[^\]]*\]\(([^)]+)\)'
                    partes = re.split(pattern, dados["context"])

                    for i, parte in enumerate(partes):
                        if i % 2 == 0:
                            # Parte de texto
                            if parte.strip():
                                doc.add_paragraph(parte.strip())
                else:
                    # Parte é uma URL de imagem
                    img_url = parte.strip()
                    try:
                        resp = requests.get(img_url)
                        resp.raise_for_status()
                        img_data = BytesIO(resp.content)
                        doc.add_picture(img_data, width=Inches(5))
                    except Exception as e:
                        st.warning(f"Erro ao baixar imagem do enunciado: {img_url} - {e}")

                # Imagens
                for img_url in dados.get("files", []):
                    try:
                        resp = requests.get(img_url)
                        resp.raise_for_status()
                        img_data = BytesIO(resp.content)
                        doc.add_picture(img_data, width=Cm(2))
                    except Exception as e:
                        st.warning(f"Erro ao baixar imagem: {img_url} - {e}")

                # Alternativas
                if dados.get("alternativesIntroduction"):
                    doc.add_paragraph(dados["alternativesIntroduction"])

                for alt in dados.get("alternatives", []):
                    doc.add_paragraph(f"{alt['letter']}) {alt['text']}")
            
            doc.add_paragraph("Gabarito")
            doc.add_paragraph("")

            for x, (_,linha) in enumerate(filtro.iterrows(), start=1):
                gabarito = linha["TX_GABARITO"]
                doc.add_paragraph(f"{x}) {gabarito}", None).add_run().bold = True



            # Salvar e oferecer download
            nome_arquivo = f"prova_{ano}_{materia}.docx"
            doc.save(nome_arquivo)

            with open(nome_arquivo, "rb") as f:
                st.download_button(
                    label="📥 Baixar DOCX",
                    data=f,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )


##############################


####### adicionar filtro de dificuldade

# adicionar filtros para habilidades
