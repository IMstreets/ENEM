"""
Módulo de interface para entrada de dados do usuário.
Gerencia a seleção de parâmetros para geração de compilados de questões do ENEM.
"""

import streamlit as st
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum


class Materia(Enum):
    """Enumeração das matérias disponíveis no ENEM."""
    MATEMATICA = ("MT", "Matemática", "mat")
    LINGUAGENS = ("LC", "Linguagens", "ling")
    HUMANAS = ("CH", "Ciências Humanas", "hum")
    NATUREZA = ("CN", "Ciências da Natureza", "nat")
    
    @property
    def codigo(self) -> str:
        """Retorna o código da matéria."""
        return self.value[0]
    
    @property
    def nome(self) -> str:
        """Retorna o nome completo da matéria."""
        return self.value[1]
    
    @property
    def checkbox_id(self) -> str:
        """Retorna o ID para checkbox."""
        return self.value[2]


@dataclass
class FiltrosQuestoes:
    """Classe para armazenar os filtros selecionados pelo usuário."""
    anos: List[str]  # Agora suporta múltiplos anos
    materias: List[str]
    numeros_questoes: Optional[List[int]]
    dificuldade_minima: int
    dificuldade_maxima: int
    filtrar_por_numero: bool
    filtrar_por_dificuldade: bool
    filtrar_por_quantidade: bool
    quantidade_questoes: Optional[int]
    filtrar_por_habilidade: bool
    habilidades: Optional[List[int]]
    
    def validar(self) -> Tuple[bool, Optional[str]]:
        """
        Valida os filtros selecionados.
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        # Verifica se pelo menos um ano foi selecionado
        if not self.anos:
            return False, "Selecione pelo menos um ano"
        
        # Verifica se pelo menos uma matéria foi selecionada
        if not self.materias:
            return False, "Selecione pelo menos uma matéria"
        
        # Valida intervalo de dificuldade
        if self.filtrar_por_dificuldade:
            if self.dificuldade_minima > self.dificuldade_maxima:
                return False, "Dificuldade mínima não pode ser maior que a máxima"
        
        # Valida números das questões
        if self.filtrar_por_numero and not self.numeros_questoes:
            return False, "Digite os números das questões ou desmarque o filtro"
        
        # Valida quantidade de questões
        if self.filtrar_por_quantidade:
            if not self.quantidade_questoes or self.quantidade_questoes <= 0:
                return False, "A quantidade de questões deve ser maior que zero"
        
        # Valida habilidades
        if self.filtrar_por_habilidade and not self.habilidades:
            return False, "Digite as habilidades desejadas ou desmarque o filtro"
        
        # Verifica conflito entre filtros
        if self.filtrar_por_numero and self.filtrar_por_quantidade:
            return False, "Não é possível usar 'Selecionar por número' e 'Limitar quantidade' ao mesmo tempo"
        
        # Aviso quando múltiplos anos com números específicos
        if self.filtrar_por_numero and len(self.anos) > 1:
            # Não é erro, mas vale um aviso (será tratado na interface)
            pass
        
        return True, None


class InterfaceEntradas:
    """Classe para gerenciar a interface de entrada de dados."""
    
    # Constantes de configuração
    ANOS_DISPONIVEIS = [str(ano) for ano in range(2009, 2024)]
    DIFICULDADE_MIN = 1
    DIFICULDADE_MAX = 2000
    DIFICULDADE_DEFAULT_MIN = 1
    DIFICULDADE_DEFAULT_MAX = 2000
    QUANTIDADE_MIN = 1
    QUANTIDADE_MAX = 500  # Aumentado para suportar múltiplos anos
    QUANTIDADE_DEFAULT = 25
    
    # Habilidades do ENEM por área
    HABILIDADES_POR_AREA = {
        "MT": list(range(1, 31)),  # H1 a H30
        "LC": list(range(1, 31)),  # H1 a H30
        "CH": list(range(1, 31)),  # H1 a H30
        "CN": list(range(1, 31)),  # H1 a H30
    }
    
    def __init__(self):
        """Inicializa a interface de entradas."""
        self.materias_map = {m.checkbox_id: m for m in Materia}
    
    def renderizar(self) -> FiltrosQuestoes:
        """
        Renderiza a interface e retorna os filtros selecionados.
        
        Returns:
            Objeto FiltrosQuestoes com as seleções do usuário
        """
        # Seleção de anos (múltiplos)
        anos = self._renderizar_selecao_anos()
        
        # Seleção de matérias
        materias = self._renderizar_selecao_materias()
        
        # Título da seção de filtros
        st.title("Seleção de Questões")
        
        # Filtros adicionais
        filtros = self._renderizar_filtros_adicionais(anos, materias)
        
        # Cria e retorna objeto com todos os filtros
        return FiltrosQuestoes(
            anos=anos,
            materias=materias,
            numeros_questoes=filtros['numeros'],
            dificuldade_minima=filtros['dif_min'],
            dificuldade_maxima=filtros['dif_max'],
            filtrar_por_numero=filtros['por_numero'],
            filtrar_por_dificuldade=filtros['por_dificuldade'],
            filtrar_por_quantidade=filtros['por_quantidade'],
            quantidade_questoes=filtros['quantidade'],
            filtrar_por_habilidade=filtros['por_habilidade'],
            habilidades=filtros['habilidades']
        )
    
    def _renderizar_selecao_anos(self) -> List[str]:
        """Renderiza seleção de anos das provas (múltiplos)."""
        st.subheader("📅 Anos das Provas")
        
        if "anos_selecionados" not in st.session_state:
            st.session_state.anos_selecionados = [self.ANOS_DISPONIVEIS[-1]]
            
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Multiselect para escolher vários anos
            anos_selecionados = st.multiselect(
                "Selecione os anos desejados",
                self.ANOS_DISPONIVEIS,
                default=st.session_state.anos_selecionados,
                help="Você pode selecionar múltiplos anos para compilar questões",
                key="multiselect_anos"
            )
            
            # Atualiza session_state com a seleção manual
            if anos_selecionados != st.session_state.anos_selecionados:
                st.session_state.anos_selecionados = anos_selecionados
        
        with col2:
            st.write("Seleção rápida:")
            if st.button("Últimos 5 anos", use_container_width=True):
                st.session_state.anos_selecionados = self.ANOS_DISPONIVEIS[-5:]
                st.rerun()
                
            if st.button("Últimos 3 anos", use_container_width=True):
                st.session_state.anos_selecionados = self.ANOS_DISPONIVEIS[-3:]
                st.rerun()
                
            if st.button("Todos os anos", use_container_width=True):
                st.session_state.anos_selecionados = self.ANOS_DISPONIVEIS
                st.rerun()
        
        if anos_selecionados:
            st.info(f"📊 {len(anos_selecionados)} ano(s) selecionado(s): {', '.join(sorted(anos_selecionados))}")
        
        return anos_selecionados
    
    def _renderizar_selecao_materias(self) -> List[str]:
        """
        Renderiza checkboxes para seleção de matérias.
        
        Returns:
            Lista com códigos das matérias selecionadas
        """
        st.subheader("📚 Matérias")
        
        col1, col2, col3 = st.columns(3)
        
        materias_selecionadas = []
        
        with col1:
            col1_inner1, col1_inner2 = st.columns(2)
            with col1_inner1:
                if st.checkbox(Materia.MATEMATICA.nome, key=Materia.MATEMATICA.checkbox_id):
                    materias_selecionadas.append(Materia.MATEMATICA.codigo)
            with col1_inner2:
                if st.checkbox(Materia.LINGUAGENS.nome, key=Materia.LINGUAGENS.checkbox_id):
                    materias_selecionadas.append(Materia.LINGUAGENS.codigo)
        
        with col2:
            col2_inner1, col2_inner2 = st.columns(2)
            with col2_inner1:
                if st.checkbox(Materia.HUMANAS.nome, key=Materia.HUMANAS.checkbox_id):
                    materias_selecionadas.append(Materia.HUMANAS.codigo)
            with col2_inner2:
                if st.checkbox(Materia.NATUREZA.nome, key=Materia.NATUREZA.checkbox_id):
                    materias_selecionadas.append(Materia.NATUREZA.codigo)
        
        with col3:
            if st.button("Selecionar todas", use_container_width=False):
                materias_selecionadas = [m.codigo for m in Materia]
            if st.button("Limpar seleção", use_container_width=False):
                materias_selecionadas = []
        
        return materias_selecionadas
    
    def _renderizar_filtros_adicionais(self, anos_selecionados: List[str], 
                                      materias_selecionadas: List[str]) -> Dict:
        """
        Renderiza filtros adicionais.
        
        Returns:
            Dicionário com os valores dos filtros
        """
        st.subheader("🎯 Filtros Avançados")
        
        # Tabs para organizar filtros
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Por Número", 
            "📊 Por Quantidade", 
            "📈 Por Dificuldade",
            "🎓 Por Habilidade"
        ])
        
        filtros_ativos = {
            'por_numero': False,
            'por_quantidade': False,
            'por_dificuldade': False,
            'por_habilidade': False,
            'numeros': None,
            'quantidade': None,
            'dif_min': self.DIFICULDADE_DEFAULT_MIN,
            'dif_max': self.DIFICULDADE_DEFAULT_MAX,
            'habilidades': None
        }
        
        with tab1:
            filtros_ativos['por_numero'] = st.checkbox(
                "Ativar filtro por número",
                help="Seleciona questões específicas pelo número"
            )
            
            if filtros_ativos['por_numero']:
                if len(anos_selecionados) > 1:
                    st.warning("⚠️ Com múltiplos anos, os números de questão se aplicam a todos os anos selecionados")
                
                filtros_ativos['numeros'] = self._renderizar_filtro_numeros()
        
        with tab2:
            filtros_ativos['por_quantidade'] = st.checkbox(
                "Ativar limite de quantidade",
                help="Define número máximo de questões"
            )
            
            if filtros_ativos['por_quantidade']:
                if filtros_ativos['por_numero']:
                    st.error("❌ Não é possível usar filtro por número e quantidade simultaneamente")
                    filtros_ativos['por_quantidade'] = False
                else:
                    filtros_ativos['quantidade'] = self._renderizar_filtro_quantidade()
        
        with tab3:
            filtros_ativos['por_dificuldade'] = st.checkbox(
                "Ativar filtro por dificuldade",
                help="Filtra por intervalo de dificuldade (TRI)"
            )
            
            if filtros_ativos['por_dificuldade']:
                dif_min, dif_max = self._renderizar_filtro_dificuldade()
                filtros_ativos['dif_min'] = dif_min
                filtros_ativos['dif_max'] = dif_max
        
        with tab4:
            filtros_ativos['por_habilidade'] = st.checkbox(
                "Ativar filtro por habilidade",
                help="Seleciona questões de habilidades específicas"
            )
            
            if filtros_ativos['por_habilidade']:
                filtros_ativos['habilidades'] = self._renderizar_filtro_habilidades(materias_selecionadas)
        
        return filtros_ativos
    
    def _renderizar_filtro_habilidades(self, materias_selecionadas: List[str]) -> Optional[List[int]]:
        """
        Renderiza seleção de habilidades.
        
        Args:
            materias_selecionadas: Lista de matérias selecionadas
            
        Returns:
            Lista de habilidades selecionadas
        """
        if not materias_selecionadas:
            st.warning("Selecione pelo menos uma matéria para filtrar por habilidade")
            return None
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Campo de texto para habilidades
            st.info(
                "💡 Cada matéria tem suas próprias habilidades (H1-H30). "
                "Ex: H21 de Matemática é diferente de H21 de Linguagens."
                )
            habilidades_texto = st.text_input(
                "Habilidades (separadas por espaço ou vírgula)",
                placeholder="Ex: 21 22 23 ou H21, H22, H23",
                help="Digite os números das habilidades desejadas"
            )
            
        
        with col2:
            st.write("Habilidades comuns:")
            if st.button("H1-H5", use_container_width=True):
                habilidades_texto = "1 2 3 4 5"
            if st.button("H21-H25", use_container_width=True):
                habilidades_texto = "21 22 23 24 25"
            if st.button("H26-H30", use_container_width=True):
                habilidades_texto = "26 27 28 29 30"
        
        # Processa entrada
        habilidades = self._processar_habilidades(habilidades_texto)
        
        if habilidades:
            # Mostra resumo
            st.success(f"✅ {len(habilidades)} habilidade(s) selecionada(s): H{', H'.join(map(str, sorted(habilidades)))}")
            
            # Aviso sobre habilidades por matéria
            
        
        return habilidades
    
    def _processar_habilidades(self, texto: str) -> List[int]:
        """
        Processa texto de entrada para extrair números de habilidades.
        
        Args:
            texto: String com habilidades
            
        Returns:
            Lista de números de habilidades
        """
        if not texto:
            return []
        
        # Remove 'H' ou 'h' e vírgulas, separa por espaços
        texto_limpo = texto.upper().replace('H', '').replace(',', ' ')
        
        habilidades = []
        invalidas = []
        
        for item in texto_limpo.split():
            item = item.strip()
            if item.isdigit():
                num = int(item)
                if 1 <= num <= 30:
                    habilidades.append(num)
                else:
                    invalidas.append(item)
            elif item:
                invalidas.append(item)
        
        if invalidas:
            st.warning(f"⚠️ Valores ignorados (habilidades válidas são H1-H30): {', '.join(invalidas)}")
        
        return list(set(habilidades))  # Remove duplicatas
    
    def _renderizar_filtro_numeros(self) -> Optional[List[int]]:
        """
        Renderiza campo para entrada de números de questões.
        
        Returns:
            Lista de números ou None se vazio
        """
        entrada = st.text_input(
            "Números das questões (separadas por espaço)",
            placeholder="Ex: 109 110 115",
            help="Digite os números das questões desejadas separados por espaço"
        )
        
        if entrada:
            return self._processar_numeros_questoes(entrada)
        return None
    
    def _renderizar_filtro_quantidade(self) -> int:
        """
        Renderiza controle para seleção de quantidade de questões.
        
        Returns:
            Quantidade de questões selecionada
        """
        col1, col2 = st.columns([2, 1])
        
        with col1:
            quantidade = st.number_input(
                "Quantidade total de questões",
                min_value=self.QUANTIDADE_MIN,
                max_value=self.QUANTIDADE_MAX,
                value=self.QUANTIDADE_DEFAULT,
                step=5,
                help="Número total de questões a serem selecionadas de todos os anos"
            )
        
        with col2:
            st.write("Acesso rápido:")
            if st.button("15", use_container_width=True):
                quantidade = 15
            if st.button("30", use_container_width=True):
                quantidade = 30
            if st.button("50", use_container_width=True):
                quantidade = 50
        
        st.info(
            f"📌 Serão selecionadas até {quantidade} questões no total, "
            f"distribuídas entre os anos e matérias selecionados"
        )
        
        return int(quantidade)
    
    def _processar_numeros_questoes(self, entrada: str) -> List[int]:
        """
        Processa string de entrada para extrair números válidos.
        
        Args:
            entrada: String com números separados por espaço
            
        Returns:
            Lista de inteiros válidos
        """
        numeros = []
        invalidos = []
        
        for item in entrada.split():
            item_limpo = item.strip()
            if item_limpo.isdigit():
                numeros.append(int(item_limpo))
            else:
                invalidos.append(item)
        
        if invalidos:
            st.warning(f"⚠️ Valores ignorados (não são números válidos): {', '.join(invalidos)}")
        
        return numeros
    
    def _renderizar_filtro_dificuldade(self) -> Tuple[int, int]:
        """
        Renderiza sliders para seleção de intervalo de dificuldade.
        
        Returns:
            Tupla (dificuldade_mínima, dificuldade_máxima)
        """
        st.write("Defina o intervalo de dificuldade:")
        
        # Range slider
        valores = st.slider(
            "Intervalo de dificuldade (Parâmetro B - TRI)",
            min_value=self.DIFICULDADE_MIN,
            max_value=self.DIFICULDADE_MAX,
            value=(self.DIFICULDADE_DEFAULT_MIN, self.DIFICULDADE_DEFAULT_MAX),
            step=10,
            help="Valores baseados na Teoria de Resposta ao Item (TRI)",
            format="%d"
        )
        
        dif_min, dif_max = valores
        
        # Interpretação visual
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nivel_min = self._classificar_dificuldade(dif_min)
            if nivel_min == "Fácil":
                st.success(f"Mín: {dif_min} ({nivel_min})")
            elif nivel_min == "Médio":
                st.info(f"Mín: {dif_min} ({nivel_min})")
            else:
                st.warning(f"Mín: {dif_min} ({nivel_min})")
        
        with col2:
            nivel_max = self._classificar_dificuldade(dif_max)
            if nivel_max == "Fácil":
                st.success(f"Máx: {dif_max} ({nivel_max})")
            elif nivel_max == "Médio":
                st.info(f"Máx: {dif_max} ({nivel_max})")
            else:
                st.warning(f"Máx: {dif_max} ({nivel_max})")
        
        with col3:
            st.metric("Amplitude", f"{dif_max - dif_min}")
        
        return dif_min, dif_max
    
    def _classificar_dificuldade(self, valor: int) -> str:
        """Classifica o nível de dificuldade."""
        if valor <= 400:
            return "Fácil"
        elif valor <= 800:
            return "Médio"
        else:
            return "Difícil"


def entradas() -> Tuple[List[str], List[str], Optional[str], int, int, bool, Optional[int], bool, Optional[List[int]]]:
    """
    Função de compatibilidade estendida.
    
    Returns:
        Tupla (anos, materias, posições, dif_max, dif_min, filtrar_quantidade, quantidade, filtrar_habilidade, habilidades)
    """
    interface = InterfaceEntradas()
    filtros = interface.renderizar()
    
    # Converte lista de números para string (compatibilidade)
    posicoes_str = None
    if filtros.numeros_questoes:
        posicoes_str = " ".join(map(str, filtros.numeros_questoes))
    
    return (
        filtros.anos,
        filtros.materias,
        posicoes_str,
        filtros.dificuldade_maxima,
        filtros.dificuldade_minima,
        filtros.filtrar_por_quantidade,
        filtros.quantidade_questoes,
        filtros.filtrar_por_habilidade,
        filtros.habilidades
    )


def entradas_avancado() -> FiltrosQuestoes:
    """
    Função para obter filtros com validação.
    
    Returns:
        Objeto FiltrosQuestoes validado
    """
    interface = InterfaceEntradas()
    filtros = interface.renderizar()
    
    # Valida os filtros
    valido, mensagem_erro = filtros.validar()
    
    if not valido:
        st.error(f"❌ {mensagem_erro}")
        st.stop()
    
    return filtros