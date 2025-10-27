import os
import json
import re
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pathlib import Path
import base64
from io import BytesIO

class PDFQuestionExtractor:
    def __init__(self, pdf_path, output_dir="questions"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.doc = fitz.open(pdf_path)
        
        # Criar diretório de saída se não existir
        Path(self.output_dir).mkdir(exist_ok=True)
        
    def extract_text_from_page(self, page_num):
        """Extrai texto de uma página específica do PDF"""
        page = self.doc[page_num]
        return page.get_text()
    
    def extract_images_from_page(self, page_num):
        """Extrai imagens de uma página específica do PDF"""
        page = self.doc[page_num]
        images = []
        
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(self.doc, xref)
            
            if pix.n - pix.alpha < 4:  # GRAY ou RGB
                img_data = pix.tobytes("png")
                images.append({
                    "index": img_index,
                    "data": img_data,
                    "format": "png"
                })
            pix = None
            
        return images
    
    def identify_question_pattern(self, text):
        """Identifica padrões de questões no texto"""
        # Padrão para identificar início de questão (ex: "Questão 40", "40.", etc.)
        question_patterns = [
            r'Questão\s+(\d+)',
            r'^(\d+)\.',
            r'QUESTÃO\s+(\d+)',
            r'Question\s+(\d+)'
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def extract_year_from_text(self, text):
        """Extrai o ano da prova do texto"""
        year_patterns = [
            r'ENEM\s+(\d{4})',
            r'(\d{4})',  # Qualquer ano de 4 dígitos
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                year = int(match)
                if 1990 <= year <= 2030:  # Range válido para anos de prova
                    return year
        return None
    
    def identify_discipline(self, text):
        """Identifica a disciplina baseada no conteúdo"""
        disciplines = {
            'matematica': ['matemática', 'função', 'equação', 'gráfico', 'cálculo', 'geometria'],
            'fisica': ['física', 'força', 'energia', 'movimento', 'velocidade', 'aceleração'],
            'quimica': ['química', 'reação', 'átomo', 'molécula', 'elemento', 'composto'],
            'biologia': ['biologia', 'célula', 'gene', 'dna', 'evolução', 'organismo'],
            'ciencias-natureza': ['nanomateriais', 'nanopartículas', 'biotecnologia'],
            'linguagens': ['texto', 'linguagem', 'literatura', 'gramática'],
            'historia': ['história', 'século', 'guerra', 'império', 'revolução'],
            'geografia': ['geografia', 'clima', 'população', 'território']
        }
        
        text_lower = text.lower()
        for discipline, keywords in disciplines.items():
            if any(keyword in text_lower for keyword in keywords):
                return discipline
        
        return 'geral'
    
    def extract_context(self, text):
        """Extrai o contexto da questão (texto introdutório)"""
        lines = text.split('\n')
        context_lines = []
        
        # Pula as primeiras linhas até encontrar o contexto
        start_collecting = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Se encontrar um padrão de questão, para de coletar
            if self.identify_question_pattern(line) and start_collecting:
                break
                
            # Se a linha tem conteúdo substancial, começa a coletar
            if len(line) > 30 and not re.match(r'^[A-E]\)', line):
                start_collecting = True
                
            if start_collecting:
                # Para se encontrar alternativas
                if re.match(r'^[A-E]\)', line):
                    break
                context_lines.append(line)
        
        return '\n\n'.join(context_lines).strip()
    
    def extract_references(self, text):
        """Extrai referências bibliográficas"""
        # Padrões comuns de referências
        ref_patterns = [
            r'Disponível em:.*?(?:\n|$)',
            r'Fonte:.*?(?:\n|$)',
            r'[A-Z][^.]*\. Disponível em:.*?(?:\n|$)',
            r'Adaptado.*?(?:\n|$)'
        ]
        
        references = []
        for pattern in ref_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            references.extend(matches)
        
        return ' '.join(references).strip()
    
    def extract_alternatives(self, text):
        """Extrai as alternativas da questão"""
        alternatives = []
        
        # Encontra todas as alternativas A, B, C, D, E
        alt_pattern = r'^([A-E])\)\s*(.*?)(?=^[A-E]\)|$)'
        matches = re.findall(alt_pattern, text, re.MULTILINE | re.DOTALL)
        
        for letter, alt_text in matches:
            alternatives.append({
                "letter": letter,
                "text": alt_text.strip().replace('\n', ' '),
                "file": None,
                "isCorrect": False  # Será definido posteriormente
            })
        
        return alternatives
    
    def extract_alternatives_introduction(self, text):
        """Extrai a introdução das alternativas"""
        # Procura por texto antes das alternativas
        lines = text.split('\n')
        intro_lines = []
        
        for line in lines:
            line = line.strip()
            if re.match(r'^[A-E]\)', line):
                break
            if len(line) > 10 and not self.identify_question_pattern(line):
                intro_lines.append(line)
        
        # Pega as últimas linhas antes das alternativas
        if len(intro_lines) > 0:
            return intro_lines[-1]
        
        return ""
    
    def save_question_image(self, question_num, images):
        """Salva imagens da questão e retorna URLs"""
        question_dir = Path(self.output_dir) / str(question_num)
        question_dir.mkdir(exist_ok=True)
        
        image_files = []
        for i, img in enumerate(images):
            img_filename = f"image_{i}.png"
            img_path = question_dir / img_filename
            
            with open(img_path, 'wb') as f:
                f.write(img["data"])
            
            image_files.append(f"./questions/{question_num}/{img_filename}")
        
        return image_files
    
    def process_question(self, page_num, text, images):
        """Processa uma questão individual"""
        question_num = self.identify_question_pattern(text)
        if not question_num:
            return None
        
        # Extrair informações
        year = self.extract_year_from_text(text)
        discipline = self.identify_discipline(text)
        context = self.extract_context(text)
        references = self.extract_references(text)
        alternatives = self.extract_alternatives(text)
        alt_intro = self.extract_alternatives_introduction(text)
        
        # Salvar imagens se existirem
        image_files = []
        if images:
            image_files = self.save_question_image(question_num, images)
        
        # Criar estrutura da questão
        question_data = {
            "title": f"Questão {question_num}" + (f" - ENEM {year}" if year else ""),
            "index": question_num,
            "year": year,
            "language": None,
            "discipline": discipline,
            "context": context,
            "references": references,
            "files": image_files,
            "correctAlternative": None,  # Precisa ser definido manualmente
            "alternativesIntroduction": alt_intro,
            "alternatives": alternatives
        }
        
        return question_data
    
    def save_question_data(self, question_data):
        """Salva os dados da questão em arquivo JSON"""
        question_num = question_data["index"]
        question_dir = Path(self.output_dir) / str(question_num)
        question_dir.mkdir(exist_ok=True)
        
        details_path = question_dir / "details.json"
        with open(details_path, 'w', encoding='utf-8') as f:
            json.dump(question_data, f, ensure_ascii=False, indent=4)
        
        print(f"Questão {question_num} salva em: {details_path}")
    
    def extract_all_questions(self):
        """Extrai todas as questões do PDF"""
        extracted_questions = []
        
        # Começar da página 1 se skip_first_page estiver ativo
        start_page = 1 if self.skip_first_page else 0
        
        print(f"📖 Processando páginas {start_page + 1} até {len(self.doc)} (ignorando capa: {self.skip_first_page})")
        
        for page_num in range(start_page, len(self.doc)):
            try:
                text = self.extract_text_from_page(page_num)
                images = self.extract_images_from_page(page_num)
                
                # Debug: mostrar quantas imagens foram filtradas
                if images:
                    print(f"   Página {page_num + 1}: {len(images)} imagem(ns) relevante(s) encontrada(s)")
                
                # Se encontrou uma questão na página
                if self.identify_question_pattern(text):
                    question_data = self.process_question(page_num, text, images)
                    
                    if question_data:
                        self.save_question_data(question_data)
                        extracted_questions.append(question_data)
                        
            except Exception as e:
                print(f"❌ Erro ao processar página {page_num + 1}: {str(e)}")
                continue
        
        return extracted_questions
    
    def close(self):
        """Fecha o documento PDF"""
        self.doc.close()

def main():
    """Função principal"""
    print("=== Extrator de Questões ENEM ===")
    print("Você pode fornecer:")
    print("1. URL do ENEM (ex: https://download.inep.gov.br/enem/provas_e_gabaritos/2024_PV_reaplicacao_PPL_D1_CD1.pdf)")
    print("2. Caminho local para o arquivo PDF")
    
    # Obter fonte do PDF
    pdf_source = input("\nDigite a URL ou caminho do PDF: ").strip()
    
    if not pdf_source:
        print("Nenhuma fonte fornecida!")
        return
    
    # Validar se é URL ou arquivo local
    if pdf_source.startswith('http'):
        if 'inep.gov.br' not in pdf_source and 'enem' not in pdf_source.lower():
            print("⚠️  Aviso: URL não parece ser do ENEM oficial")
    else:
        if not os.path.exists(pdf_source):
            print("Arquivo PDF não encontrado!")
            return
    
    # Criar extrator
    try:
        extractor = PDFQuestionExtractor(pdf_source)
    except Exception as e:
        print(f"Erro ao inicializar extrator: {str(e)}")
        return
    
    try:
        print("\n📚 Iniciando extração de questões...")
        questions = extractor.extract_all_questions()
        
        print(f"\n✅ Extração concluída!")
        print(f"📊 Total de questões extraídas: {len(questions)}")
        
        if extractor.exam_info:
            print(f"📋 Informações do exame: {extractor.exam_info}")
        
        # Mostrar resumo
        print("\n📝 Questões extraídas:")
        for q in questions:
            print(f"   • Questão {q['index']}: {q['title']} [{q['discipline']}]")
        
        print(f"\n📁 Arquivos salvos em: ./questions/")
        print("\n⚠️  Lembre-se de definir manualmente as alternativas corretas nos arquivos details.json!")
            
    except Exception as e:
        print(f"❌ Erro durante a extração: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()