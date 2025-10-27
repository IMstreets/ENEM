"""
Módulo para correção e normalização de dados das provas do ENEM.
Processa arquivos CSV ajustando valores de dificuldade (NU_PARAM_B).
"""

import pandas as pd
import os
from typing import List, Union, Optional
import logging
from pathlib import Path


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ENEMDataProcessor:
    """Classe para processar e corrigir dados das provas do ENEM."""
    
    # Constantes para ajuste de notas
    ADJUSTMENT_RULES = {
        'large_positive': (1000, 100000, 500),     # valor > 1000 e < 100000: +500
        'large_negative': (-100000, -1000, 500),   # valor > -100000 e < -1000: +500
        'small_range': (-10, 10, 100, 500),        # -10 < valor < 10: *100 + 500
        'default': 0                                # outros casos: 0
    }
    
    DEFAULT_ENCODING = "latin1"
    DEFAULT_SEPARATOR = ";"
    DECIMAL_SEPARATOR = "."
    OUTPUT_DECIMAL = ","
    
    def __init__(self, base_path: str = "base-de-dados-CSV"):
        """
        Inicializa o processador de dados.
        
        Args:
            base_path: Caminho para o diretório com os arquivos CSV
        """
        self.base_path = Path(base_path)
        self._validate_path()
    
    def _validate_path(self):
        """Valida se o caminho base existe."""
        if not self.base_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {self.base_path}")
    
    def processar_anos(self, anos: Optional[List[int]] = None):
        """
        Processa dados de múltiplos anos.
        
        Args:
            anos: Lista de anos a processar. Se None, usa anos padrão (2009-2024)
        """
        if anos is None:
            anos = list(range(2009, 2025))
        
        resultados = []
        for ano in anos:
            try:
                sucesso = self.processar_ano(ano)
                resultados.append((ano, sucesso))
            except Exception as e:
                logger.error(f"Erro ao processar ano {ano}: {e}")
                resultados.append((ano, False))
        
        self._relatorio_processamento(resultados)
        return resultados
    
    def processar_ano(self, ano: int) -> bool:
        """
        Processa dados de um ano específico.
        
        Args:
            ano: Ano a ser processado
            
        Returns:
            True se processado com sucesso, False caso contrário
        """
        arquivo_csv = self.base_path / f"ITENS_PROVA_{ano}.csv"
        
        if not arquivo_csv.exists():
            logger.warning(f"Arquivo não encontrado: {arquivo_csv}")
            return False
        
        try:
            # Carrega e processa o DataFrame
            df = self._carregar_dataframe(arquivo_csv)
            df = self._processar_dataframe(df, ano)
            self._salvar_dataframe(df, arquivo_csv)
            
            logger.info(f"Arquivo {ano} atualizado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {ano}: {e}")
            return False
    
    def _carregar_dataframe(self, arquivo: Path) -> pd.DataFrame:
        """Carrega DataFrame do arquivo CSV."""
        return pd.read_csv(
            arquivo,
            sep=self.DEFAULT_SEPARATOR,
            encoding=self.DEFAULT_ENCODING,
            decimal=self.DECIMAL_SEPARATOR
        )
    
    def _processar_dataframe(self, df: pd.DataFrame, ano: int) -> pd.DataFrame:
        """
        Processa o DataFrame aplicando todas as transformações necessárias.
        
        Args:
            df: DataFrame a processar
            ano: Ano do arquivo (para logging)
            
        Returns:
            DataFrame processado
        """
        # Filtra apenas caderno azul
        df = self._filtrar_caderno_azul(df)
        
        # Converte e ajusta valores de NU_PARAM_B
        df = self._processar_coluna_param_b(df, ano)
        
        return df
    
    def _filtrar_caderno_azul(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra apenas questões do caderno azul."""
        if "TX_COR" not in df.columns:
            logger.warning("Coluna TX_COR não encontrada no DataFrame")
            return df
        
        return df[df["TX_COR"].str.upper() == "AZUL"].copy()
    
    def _processar_coluna_param_b(self, df: pd.DataFrame, ano: int) -> pd.DataFrame:
        """Processa a coluna NU_PARAM_B com conversões e ajustes."""
        if "NU_PARAM_B" not in df.columns:
            logger.warning("Coluna NU_PARAM_B não encontrada no DataFrame")
            return df
        
        # Converte para float
        df["NU_PARAM_B"] = self._converter_para_float(df["NU_PARAM_B"])
        
        # Aplica ajustes
        df["NU_PARAM_B"] = df["NU_PARAM_B"].apply(
            lambda x: self._ajustar_nota(x, ano)
        )
        
        # Converte de volta para formato brasileiro
        df["NU_PARAM_B"] = self._formatar_decimal_brasileiro(df["NU_PARAM_B"])
        
        return df
    
    def _converter_para_float(self, series: pd.Series) -> pd.Series:
        """Converte série para float, tratando vírgulas."""
        return (
            series
            .astype(str)
            .str.replace(",", ".", regex=False)
            .apply(pd.to_numeric, errors='coerce')
        )
    
    def _ajustar_nota(self, valor: Union[float, None], ano: int) -> str:
        """
        Aplica regras de ajuste à nota.
        
        Args:
            valor: Valor a ajustar
            ano: Ano do arquivo (para logging de erros)
            
        Returns:
            Valor ajustado formatado como string
        """
        try:
            if pd.isna(valor):
                return "0.00"
            
            # Aplica regras de ajuste
            nota = self._calcular_ajuste(valor)
            return f"{nota:.2f}"
            
        except (ValueError, TypeError) as e:
            logger.error(f"[ERRO] Ano {ano} | Valor inválido: {valor} | Erro: {e}")
            return "0.00"
    
    def _calcular_ajuste(self, valor: float) -> float:
        """
        Calcula o ajuste baseado nas regras definidas.
        
        Args:
            valor: Valor original
            
        Returns:
            Valor ajustado
        """
        # Verifica grandes valores positivos ou negativos
        if (1000 < valor < 100000) or (-100000 < valor < -1000):
            return valor + 500
        
        # Verifica pequenos valores
        elif -10 < valor < 10:
            return (valor * 100) + 500
        
        # Caso padrão
        else:
            return 0
    
    def _formatar_decimal_brasileiro(self, series: pd.Series) -> pd.Series:
        """Formata série para padrão decimal brasileiro (vírgula)."""
        return (
            series
            .astype(str)
            .str.replace(".", ",", regex=False)
        )
    
    def _salvar_dataframe(self, df: pd.DataFrame, arquivo: Path):
        """Salva DataFrame no arquivo CSV."""
        df.to_csv(
            arquivo,
            sep=self.DEFAULT_SEPARATOR,
            index=False,
            encoding=self.DEFAULT_ENCODING
        )
    
    def _relatorio_processamento(self, resultados: List[tuple]):
        """
        Gera relatório do processamento.
        
        Args:
            resultados: Lista de tuplas (ano, sucesso)
        """
        total = len(resultados)
        sucessos = sum(1 for _, sucesso in resultados if sucesso)
        falhas = total - sucessos
        
        logger.info("=" * 50)
        logger.info(f"RELATÓRIO DE PROCESSAMENTO")
        logger.info(f"Total de arquivos: {total}")
        logger.info(f"Processados com sucesso: {sucessos}")
        logger.info(f"Falhas: {falhas}")
        
        if falhas > 0:
            anos_falha = [ano for ano, sucesso in resultados if not sucesso]
            logger.warning(f"Anos com falha: {anos_falha}")
        
        logger.info("=" * 50)
    
    def validar_processamento(self, ano: int) -> bool:
        """
        Valida se o processamento de um ano foi correto.
        
        Args:
            ano: Ano a validar
            
        Returns:
            True se válido, False caso contrário
        """
        arquivo_csv = self.base_path / f"ITENS_PROVA_{ano}.csv"
        
        if not arquivo_csv.exists():
            return False
        
        try:
            df = self._carregar_dataframe(arquivo_csv)
            
            # Verifica se há apenas caderno azul
            if "TX_COR" in df.columns:
                cores_unicas = df["TX_COR"].str.upper().unique()
                if len(cores_unicas) != 1 or cores_unicas[0] != "AZUL":
                    logger.warning(f"Ano {ano}: Encontradas cores além de AZUL")
                    return False
            
            # Verifica formato dos valores
            if "NU_PARAM_B" in df.columns:
                # Verifica se usa vírgula como separador decimal
                valores_com_ponto = df["NU_PARAM_B"].str.contains(".", regex=False).any()
                if valores_com_ponto:
                    logger.warning(f"Ano {ano}: Valores com ponto decimal encontrados")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar ano {ano}: {e}")
            return False


def main():
    """Função principal para execução do script."""
    # Define anos a processar
    anos_processar = list(range(2009, 2025))
    
    # Cria processador e executa
    processador = ENEMDataProcessor("base-de-dados-CSV")
    
    # Processa todos os anos
    resultados = processador.processar_anos(anos_processar)
    
    # Opcionalmente, valida o processamento
    print("\nValidando processamento...")
    for ano in anos_processar:
        if processador.validar_processamento(ano):
            print(f"✓ Ano {ano} validado com sucesso")
        else:
            print(f"✗ Ano {ano} com problemas na validação")


if __name__ == "__main__":
    main()