#!/usr/bin/env python3
"""
Script para processar documentos PDF.
Converte o PDF para Docling JSON e depois extrai o conteúdo para Markdown.

Inspirado em:
- converter_para_docling_json.py
- extrair_tudo_markdown_docling_md.py
"""

from pathlib import Path
import json
import time
import unicodedata
import re

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.document import DoclingDocument


# ============================================================================
# CONFIGURACAO PADRAO (OPCIONAL)
# ============================================================================
# Se desejar usar valores padrão sem interação, descomente e configure:
# PDF_ENTRADA_PADRAO = "documents/credito-de-regeneracao.pdf"
# DIRETORIO_SAIDA_PADRAO = None  # None = chatbot-ia/documents/
# ============================================================================


def corrigir_caracteres_latex(texto):
    """
    Corrige caracteres compostos provenientes de PDFs gerados com LaTeX.
    
    O LaTeX às vezes gera acentos como caracteres espaçados separados (U+00B4)
    ao invés de combining characters (U+0301), impedindo normalização Unicode.
    Esta função substitui manualmente os padrões problemáticos.
    """
    if not texto:
        return texto
    
    # Mapeamento de acentos espaçados + letras base para caracteres compostos
    substituicoes = [
        # Acento agudo (´) - pode vir antes ou depois da letra
        (r'[´\u00b4\u00c2\u00b4]\s*a', 'á'),
        (r'a\s*[´\u00b4\u00c2\u00b4]', 'á'),
        (r'[´\u00b4\u00c2\u00b4]\s*e', 'é'),
        (r'e\s*[´\u00b4\u00c2\u00b4]', 'é'),
        (r'[´\u00b4\u00c2\u00b4]\s*i', 'í'),
        (r'i\s*[´\u00b4\u00c2\u00b4]', 'í'),
        (r'[´\u00b4\u00c2\u00b4]\s*o', 'ó'),
        (r'o\s*[´\u00b4\u00c2\u00b4]', 'ó'),
        (r'[´\u00b4\u00c2\u00b4]\s*u', 'ú'),
        (r'u\s*[´\u00b4\u00c2\u00b4]', 'ú'),
        (r'[´\u00b4\u00c2\u00b4]\s*A', 'Á'),
        (r'A\s*[´\u00b4\u00c2\u00b4]', 'Á'),
        (r'[´\u00b4\u00c2\u00b4]\s*E', 'É'),
        (r'E\s*[´\u00b4\u00c2\u00b4]', 'É'),
        (r'[´\u00b4\u00c2\u00b4]\s*I', 'Í'),
        (r'I\s*[´\u00b4\u00c2\u00b4]', 'Í'),
        (r'[´\u00b4\u00c2\u00b4]\s*O', 'Ó'),
        (r'O\s*[´\u00b4\u00c2\u00b4]', 'Ó'),
        (r'[´\u00b4\u00c2\u00b4]\s*U', 'Ú'),
        (r'U\s*[´\u00b4\u00c2\u00b4]', 'Ú'),
        
        # Til (~) e variantes - pode vir antes ou depois
        (r'[~\u02dc\u007e\u02dc\u00cb\u009c]\s*a', 'ã'),
        (r'a\s*[~\u02dc\u007e\u00cb\u009c]\s*o', 'ão'),
        (r'a\s*[~\u02dc\u007e\u00cb\u009c]', 'ã'),
        (r'[~\u02dc\u007e\u00cb\u009c]\s*o', 'õ'),
        (r'o\s*[~\u02dc\u007e\u00cb\u009c]', 'õ'),
        (r'[~\u02dc\u007e\u00cb\u009c]\s*A', 'Ã'),
        (r'A\s*[~\u02dc\u007e\u00cb\u009c]', 'Ã'),
        (r'[~\u02dc\u007e\u00cb\u009c]\s*O', 'Õ'),
        (r'O\s*[~\u02dc\u007e\u00cb\u009c]', 'Õ'),
        
        # Casos específicos para "ção" e "ções"
        (r'c\s*[¸\u00b8]\s*[~\u02dc\u00cb\u009c\u007e]\s*a\s*o', 'ção'),
        (r'c\s*[¸\u00b8]\s*[~\u02dc\u00cb\u009c\u007e]\s*o\s*e\s*s', 'ções'),
        (r'ç\s*[~\u02dc\u00cb\u009c\u007e]\s*a\s*o', 'ção'),
        (r'ç\s*[~\u02dc\u00cb\u009c\u007e]\s*o\s*e\s*s', 'ções'),
        (r'ç\s*[~\u02dc\u00cb\u009c\u007e]\s*o', 'ção'),
        (r'ç\s*õ', 'ção'),
        
        # Circunflexo (^) - pode vir antes ou depois
        (r'[\^\u02c6\u005e\u02c6]\s*a', 'â'),
        (r'a\s*[\^\u02c6\u005e]', 'â'),
        (r'[\^\u02c6\u005e]\s*e', 'ê'),
        (r'e\s*[\^\u02c6\u005e]', 'ê'),
        (r'[\^\u02c6\u005e]\s*o', 'ô'),
        (r'o\s*[\^\u02c6\u005e]', 'ô'),
        (r'[\^\u02c6\u005e]\s*A', 'Â'),
        (r'A\s*[\^\u02c6\u005e]', 'Â'),
        (r'[\^\u02c6\u005e]\s*E', 'Ê'),
        (r'E\s*[\^\u02c6\u005e]', 'Ê'),
        (r'[\^\u02c6\u005e]\s*O', 'Ô'),
        (r'O\s*[\^\u02c6\u005e]', 'Ô'),
        
        # Cedilha (¸) - pode vir antes ou depois
        (r'c\s*[¸\u00b8]', 'ç'),
        (r'[¸\u00b8]\s*c', 'ç'),
        (r'C\s*[¸\u00b8]', 'Ç'),
        (r'[¸\u00b8]\s*C', 'Ç'),
    ]
    
    # Aplica todas as substituições (múltiplas passadas para capturar padrões complexos)
    texto_corrigido = texto
    for _ in range(3):  # Três passadas para padrões complexos aninhados
        for padrao, substituicao in substituicoes:
            texto_corrigido = re.sub(padrao, substituicao, texto_corrigido)
    
    # Substituições adicionais para casos específicos encontrados no PDF
    casos_especificos = [
        # Correções de combining characters Unicode (U+0301, U+0302, U+0303, U+0327)
        ('e\u0302', 'ê'),  # e + combining circumflex
        ('o\u0302', 'ô'),  # o + combining circumflex  
        ('a\u0302', 'â'),  # a + combining circumflex
        ('e\u0301', 'é'),  # e + combining acute
        ('o\u0301', 'ó'),  # o + combining acute
        ('a\u0301', 'á'),  # a + combining acute
        ('a\u0303', 'ã'),  # a + combining tilde
        ('o\u0303', 'õ'),  # o + combining tilde
        ('c\u0327', 'ç'),  # c + combining cedilla
        
        # Padrões de caracteres com espaços (ordem importa - específico primeiro)
        (r' a\s*$', ''),  # Remove " a" no final de linha (comum no PDF)
        (r' a\s+de ', ' de '),
        (r'Peer-to-Peer\s+a\s+de', 'Peer-to-Peer de'),
        (r'Natureza\s+a\s*$', 'Natureza'),
        (r'Proposta\s+a\s*$', 'Proposta'),
        (r'Tokens\s+a\s*$', 'Tokens'),
        
        # Circunflexo + vogais problemáticas
        (r'tˆm', 'têm'),
        (r'econˆmico', 'econômico'),
        (r'econˆomic', 'econômic'),
        (r'autˆnomo', 'autônomo'),
        (r'ˆ', '^'),  # Substitui resíduos de circunflexo
        
        # Acento agudo problemático
        (r'ap´s', 'após'),
        (r'problemá\s+e', 'problema é'),
        (r'sistemá\s+e', 'sistema é'),
        (r'estruturá\s+e', 'estrutura é'),
        (r'metodologiá\s+e', 'metodologia é'),
        (r'mudançá\s+e', 'mudança é'),
        (r'aindá\s+e', 'ainda é'),
        (r'á\s+e', 'a é'),
        (r'jornadá\s+e', 'jornada é'),
        (r'regrá\s+e', 'regra é'),
        (r'vagá\s+e', 'vaga é'),
        (r'lidadé', 'lidade é'),
        (r'Erá\s+é', 'Era é'),
        (r'Ativistá\s+e', 'Ativista é'),
        
        # Til problemático
        (r'nõ\s+para', 'não para'),
        (r'nõ\s+([aáàâã])', r'não \1'),
        (r'nõ\s+é', 'não é'),
        (r'sõ\s+', 'são '),
        (r'õ\s+E', 'É'),
        (r'geraç\s*˜\s*es', 'gerações'),
        (r'geraç\s+˜es', 'gerações'),
        (r'aç\s*˜\s*[õo]', 'ação'),
        (r'aç\s*˜\s*es', 'ações'),
        
        # Cedilha problemática com til
        (r'c\s*[¸\u00b8]\s*˜', 'ç'),
        (r'ç\s*˜\s*a\s*o', 'ção'),
        (r'regeneracõ', 'regeneração'),
        (r'degradacõ', 'degradação'),
        (r'extracõ', 'extração'),
        (r'erosõ', 'erosão'),
        (r'perturbacõ', 'perturbação'),
        (r'formacõ', 'formação'),
        (r'regulacõ', 'regulação'),
        (r'valoracõ', 'valoração'),
        (r'distribuicõ', 'distribuição'),
        (r'Alocacõ', 'Alocação'),
        (r'participacõ', 'participação'),
        (r'inspecõ', 'inspeção'),
        (r'transacõ', 'transação'),
        (r'certificacõ', 'certificação'),
        (r'Validacõ', 'Validação'),
        (r'compensacõ', 'compensação'),
        (r'Pontuacõ', 'Pontuação'),
        (r'aplicacõ', 'aplicação'),
        (r'inovacõ', 'inovação'),
        (r'publicacõ', 'publicação'),
        (r'contribuicõ', 'contribuição'),
        (r'identificacõ', 'identificação'),
        (r'traducõ', 'tradução'),
        (r'invalidacõ', 'invalidação'),
        (r'finalizacõ', 'finalização'),
        (r'revisõ', 'revisão'),
        (r'realizacõ', 'realização'),
        (r'emissõ', 'emissão'),
        (r'avaliacõ', 'avaliação'),
        (r'integracõ', 'integração'),
        (r'violacõ', 'violação'),
        (r'delacõ', 'delação'),
        (r'Descricõ', 'Descrição'),
        (r'Derivacõ', 'Derivação'),
        (r'Regeneracõ', 'Regeneração'),
        (r'manutencõ', 'manutenção'),
        (r'conversõ', 'conversão'),
        (r'compreensõ', 'compreensão'),
        (r'Funcõ', 'Função'),
        (r'funcõ', 'função'),
        
        # Caracteres especiais isolados
        (r'[¸\u00b8]\s*a\s+', ''),  # Remove resíduos de cedilha
        (r'[´\u00b4]\s+([eo])\s+', r'\1 '),  # Remove acento agudo isolado
        
        # É problemático
        (r'íncentivar', 'incentivar'),
        (r'éssencial', 'é essencial'),
        (r'éxecutado', 'é executado'),
        (r'éntõ', 'é então'),
        (r'\sé\s+e\s+', ' é '),
        (r'elá\s+e', 'ela é'),
        (r'úma\s+', 'é uma '),
        (r'umá\s+', 'uma '),
        (r'área\s+', 'área '),
        (r'umárea', 'uma área'),
        (r'\s´\s+', ' é '),
        (r'usúrio', 'usuário'),
        (r'Usúrio', 'Usuário'),
        
        # Vogais com acentos problemáticos - níveis
        (r'n´\s*ıvel', 'nível'),
        (r'n´mero\s+u', 'número'),
        (r'N´mero\s+u', 'Número'),
        (r'N´vel\s+ı', 'Nível'),
        (r'M´ximo\s+a', 'Máximo'),
        (r'Atribúdo\s+ı', 'Atribuído'),
        
        # Expressões compostas problemáticas
        (r'princ´\s*ıpio', 'princípio'),
        (r'Princ´\s*ıpio', 'Princípio'),
        (r'espec´\s*ıfico', 'específico'),
        (r'cient´\s*ıfico', 'científico'),
        (r'ecol´\s*ógico', 'ecológico'),
        (r'sistˆ\s*mica', 'sistêmica'),
        (r'ecossistˆ\s*mico', 'ecossistêmico'),
        (r'cont´\s*ınuo', 'contínuo'),
        (r'distribú\s*ıdo', 'distribuído'),
        (r'conclú\s*ıdo', 'concluído'),
        (r'indiv´\s*ıduo', 'indivíduo'),
        (r'fam´\s*ılia', 'família'),
        (r'acess´\s*ıvel', 'acessível'),
        (r'poss´\s*ıvel', 'possível'),
        (r'dispon´\s*ıvel', 'disponível'),
        (r'verific´\s*ável', 'verificável'),
        (r'quantific´\s*ável', 'quantificável'),
        (r'catastr´\s*ófico', 'catastrófico'),
        (r'intr´\s*ınseco', 'intrínseco'),
        (r'imutável', 'imutável'),
        (r'irrevers´\s*ıvel', 'irreversível'),
        (r'impratic´\s*ável', 'impraticável'),
        (r'tang´\s*ıvel', 'tangível'),
        (r'metodol´\s*ógico', 'metodológico'),
        (r'geneal´\s*ógico', 'genealógico'),
        (r'obrigat´\s*ório', 'obrigatório'),
        (r'vital´\s*ıcio', 'vitalício'),
        (r'eleg´\s*ıvel', 'elegível'),
        (r'reivindic´\s*ável', 'reivindicável'),
        (r'inating´\s*ıvel', 'inatingível'),
        (r'agn´\s*óstico', 'agnóstico'),
        (r'autocust´\s*ódia', 'autocustódia'),
        (r'previs´\s*ıvel', 'previsível'),
        (r'per´\s*ıodo', 'período'),
        (r'pr´\s*óprio', 'próprio'),
        (r'pr´\s*évio', 'prévio'),
        (r'pr´\s*óximo', 'próximo'),
        (r'pr´-lancamento', 'pré-lançamento'),
        (r'p´\s*ública', 'pública'),
        (r'p´\s*úblico', 'público'),
        (r'c´\s*ódigo', 'código'),
        (r'c´\s*ópía', 'cópia'),
        (r'c´\s*írculo', 'círculo'),
        (r'c´\s*ıclico', 'cíclico'),
        (r'única', 'única'),
        (r'´\s*única', 'única'),
        (r'u´nico', 'único'),
        (r'´nico', 'único'),
        (r'ónico', 'único'),
        (r'o´rgão', 'órgão'),
        (r'´rgão', 'órgão'),
        (r'relat´\s*ório', 'relatório'),
        (r'd´\s*ólares', 'dólares'),
        (r'f´\s*órmula', 'fórmula'),
        (r'f´\s*értil', 'fértil'),
        (r'f´\s*ısica', 'física'),
        (r'cent´\s*ımetros', 'centímetros'),
        (r'diâmetro', 'diâmetro'),
        (r'sá\s*úde', 'saúde'),
        (r'açonjunto', 'conjunto'),
        (r'v´\s*ınculo', 'vínculo'),
        (r'Índice', 'Índice'),
        (r'índice', 'índice'),
        (r'dó\s+[IÍ]ndice', 'do Índice'),
        (r'dó\s+índice', 'do índice'),
        (r'Ó\s+ındice', 'O índice'),
        (r'territ´\s*ório', 'território'),
        (r'planet´\s*ária', 'planetária'),
        (r'priet´\s*ário', 'proprietário'),
        (r'combust´\s*ıvel', 'combustível'),
        (r'sustent´\s*ável', 'sustentável'),
        (r'transparˆncia', 'transparência'),
        (r'confianca', 'confiança'),
        (r'ausˆncia', 'ausência'),
        (r'privil´\s*égio', 'privilégio'),
        (r'demográfico', 'demográfico'),
        (r'geográfico', 'geográfico'),
        (r'criptográfico', 'criptográfico'),
        (r'imunológico', 'imunológico'),
        
        # Palavras compostas específicas do PDF
        (r'Peer-to-Peer\s+a\s+', 'Peer-to-Peer '),
        (r'Ametodologia', 'A metodologia'),
        (r'Ádistribuição', 'A distribuição'),
        (r'Otokenomics', 'O tokenomics'),
        (r'Ocálculo', 'O cálculo'),
        (r'Operfil', 'O perfil'),
        (r'OProblema', 'O Problema'),
        (r'OCiclo', 'O Ciclo'),
        (r'OProcesso', 'O Processo'),
        (r'OMecanismo', 'O Mecanismo'),
        (r'OLastro', 'O Lastro'),
        (r'Umavez', 'Uma vez'),
        (r'Épocas\s+E', 'Épocas ('),
        (r'é\s+pocas', 'Épocas'),
        (r'Erá\s+´', 'Era'),
        (r'dé\s+émissão', 'de emissão'),
        (r'árvoré', 'árvore'),
        (r'´\s*rvores', 'árvores'),
        (r'´\s*RVORE', 'ÁRVORE'),
        (r'Árvores\s+A\s+', 'Árvores '),
        (r'dé\s+Arvores', 'de Árvores'),
        (r'dérvores', 'de árvores'),
        (r'Categoriá\s+rvores', 'Categoria Árvores'),
        (r'plantac˜es', 'plantações'),
        (r'inspec˜es', 'inspeções'),
        (r'inspeç\s*˜es', 'inspeções'),
        (r'transaç\s*˜es', 'transações'),
        (r'compensaç\s*˜es', 'compensações'),
        (r'organizaç\s*˜es', 'organizações'),
        (r'populaç\s*˜es', 'populações'),
        (r'opç\s*˜es', 'opções'),
        (r'integraç\s*˜es', 'integrações'),
        (r'contribuiç\s*˜es', 'contribuições'),
        (r'funç\s*˜es', 'funções'),
        (r'restric˜es', 'restrições'),
        (r'solicitac˜es', 'solicitações'),
        (r'invalidaç\s*˜es', 'invalidações'),
        (r'condiç\s*˜es', 'condições'),
        (r'M´tricas', 'Métricas'),
        (r'M´trica', 'Métrica'),
        (r'm´trica', 'métrica'),
        (r'm´dia', 'média'),
        (r'm´dium', 'médio'),
        (r'm´dio', 'médio'),
        (r'm´ximo', 'máximo'),
        (r'm´ınimo', 'mínimo'),
        (r'm´vel', 'móvel'),
        (r'm´todo', 'método'),
        (r'estat´\s*ıstica', 'estatística'),
        (r't´cnica', 'técnica'),
        (r't´cnico', 'técnico'),
        (r'atú\s+', 'até '),
        (r'Além', 'Além'),
        (r'além', 'além'),
        (r'também', 'também'),
        (r'tamb´m', 'também'),
        (r'fundacão', 'fundação'),
        (r'comprovacão', 'comprovação'),
        (r'inspeçãó', 'inspeção é'),
        (r'PontuacõDeRegeneração', 'PontuaçãoDeRegeneração'),
        (r'PontuaçãoDeRegeneração\s+¸a', 'PontuaçãoDeRegeneração'),
        (r'usuárió', 'usuário é'),
        (r'registró', 'registro é'),
        (r'propósitó', 'propósito é'),
        (r'Regeneraç˜ó', 'Regeneração é'),
        (r'nãó', 'não é'),
        (r'ímposto', 'é imposto'),
        (r'átribú\s*ıda', 'é atribuída'),
        (r'çampanha', 'campanha'),
        (r'lancar', 'lançar'),
        (r'alcancar', 'alcançar'),
        (r'através', 'através'),
        (r'trocá-los', 'trocá-los'),
        (r'completá-la', 'completá-la'),
        (r'imp˜e', 'impõe'),
        (r'prop˜e', 'propõe'),
        (r'gracas', 'graças'),
        (r'estálgoritmicamente', 'está algoritmicamente'),
    ]
    
    for padrao, substituicao in casos_especificos:
        texto_corrigido = re.sub(padrao, substituicao, texto_corrigido)
    
    # Limpeza final de resíduos (ordem importa)
    limpeza_final = [
        (r'\s+a\s*$', '', re.MULTILINE),  # Remove " a" no final das linhas
        (r'\s+e\s+o\s+', ' '),  # Remove "e o" espaçado
        (r'\s+o\s+e\s+', ' '),  # Remove "o e" espaçado  
        (r'\s+a\s+o\s+', ' '),  # Remove "a o" espaçado
        (r'\s+o\s+a\s+', ' '),  # Remove "o a" espaçado
        (r'\s+(a|o|e)\s+\1\s+\1\s*', ' '),  # Remove repetições triplas
        (r'\s+(a|o|e)\s+\1\s*', ' '),  # Remove repetições duplas
        (r'´\s*ı', 'í'),  # Resíduos de acentos
        (r'´\s*a', 'á'),
        (r'´\s*e', 'é'),
        (r'´\s*o', 'ó'),
        (r'´\s*u', 'ú'),
        (r'ˆ\s*a', 'â'),
        (r'ˆ\s*e', 'ê'),
        (r'ˆ\s*o', 'ô'),
        (r'õ\s+,', 'ão,'),  # Correção de "õ ," para "ão,"
        (r'será\s+émitido', 'será emitido'),
        (r'será\s+é', 'será '),
        (r'ássustador', 'é assustador'),
        (r'territ´\s*rio', 'território'),
        (r'f´rtil', 'fértil'),
        (r'quantific´veis', 'quantificáveis'),
        (r'catastr´ficos', 'catastróficos'),
        (r'cont´\s*ınua', 'contínua'),
        (r'cont´\s*ınuo', 'contínuo'),
        (r'\sé\s+(ser|ter|estar)\s+', r' é \1 '),  # Espaçamento de verbos
        (r'A\s+missão\s+do\s+projeto\s+incentivar', 'A missão do projeto é incentivar'),
    ]
    
    for padrao, substituicao, *flags in limpeza_final:
        if flags:
            texto_corrigido = re.sub(padrao, substituicao, texto_corrigido, flags=flags[0])
        else:
            texto_corrigido = re.sub(padrao, substituicao, texto_corrigido)
    
    # Aplica normalização Unicode NFC após todas as substituições
    texto_corrigido = unicodedata.normalize('NFC', texto_corrigido)
    
    return texto_corrigido


def processar_pdf_credito_regeneracao():
    """
    Processa um documento PDF:
    1. Converte para Docling JSON
    2. Extrai o conteúdo para Markdown
    
    O script solicita interativamente:
    - Caminho do PDF a ser processado
    - Diretório de saída (opcional)
    
    Nota: O PDF pode ter sido gerado com LaTeX e usar caracteres compostos Unicode
    (combining characters), onde acentos são separados das letras base.
    Aplicamos normalização NFC para corrigir isso automaticamente.
    """
    inicio = time.time()
    
    print("\n" + "="*70)
    print("PROCESSADOR DE DOCUMENTOS PDF -> DOCLING JSON + MARKDOWN")
    print("="*70)
    
    # Define os caminhos dos arquivos
    base_dir = Path(__file__).resolve().parent.parent.parent
    
    # Solicita o caminho do PDF
    print("\n[ENTRADA]")
    print("Digite o caminho do arquivo PDF a processar:")
    print("  - Caminho relativo: documents/meu_arquivo.pdf")
    print("  - Caminho absoluto: C:/Users/Usuario/Documents/arquivo.pdf")
    print("  - Pressione ENTER para usar o padrao: documents/credito-de-regeneracao.pdf")
    
    pdf_entrada = input("\nCaminho do PDF: ").strip()
    
    # Usa padrão se vazio
    if not pdf_entrada:
        pdf_entrada = "documents/credito-de-regeneracao.pdf"
        print(f"  -> Usando padrao: {pdf_entrada}")
    
    # Processa o caminho do PDF de entrada
    pdf_path = Path(pdf_entrada)
    if not pdf_path.is_absolute():
        # Se for relativo, resolve em relação ao diretório base do projeto
        pdf_path = base_dir / pdf_entrada
    
    # Solicita o diretório de saída
    print("\n[SAIDA]")
    print("Digite o diretorio onde salvar os arquivos gerados (JSON e MD):")
    print("  - Pressione ENTER para usar o padrao: chatbot-ia/documents/")
    print("  - Ou especifique outro: saida/ ou C:/Users/Usuario/saida/")
    
    dir_saida = input("\nDiretorio de saida: ").strip()
    
    # Define o diretório de saída
    if not dir_saida:
        output_dir = base_dir / "chatbot-ia" / "documents"
        print(f"  -> Usando padrao: chatbot-ia/documents/")
    else:
        output_dir = Path(dir_saida)
        if not output_dir.is_absolute():
            output_dir = base_dir / dir_saida
    
    # Gera nomes de saída baseados no nome do arquivo de entrada
    pdf_name = pdf_path.stem  # Nome sem extensão
    json_path = output_dir / f"{pdf_name}_docling.json"
    markdown_path = output_dir / f"{pdf_name}_docling.md"
    
    # Cria o diretório de saída se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica se o PDF existe
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF nao encontrado: {pdf_path}")
    
    print(f"\n=== Processamento de Documento PDF ===")
    print(f"Arquivo de entrada: {pdf_path}")
    print(f"Diretorio de saida: {output_dir}")
    print(f"Nome base dos arquivos: {pdf_name}")
    
    # ========== ETAPA 1: Converter PDF para Docling JSON ==========
    print("\n[1/2] Convertendo PDF para Docling JSON...")
    
    # Configura o pipeline de processamento
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # OCR desabilitado (mais rápido)
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    pipeline_options.table_structure_options.do_cell_matching = True
    
    # Cria o conversor
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
    
    # Converte o PDF
    resultado = converter.convert(str(pdf_path))
    documento = resultado.document
    
    # Salva o JSON com correção de caracteres LaTeX
    doc_dict = documento.export_to_dict()
    json_str = json.dumps(doc_dict, indent=2, ensure_ascii=False)
    # Corrige caracteres compostos do LaTeX
    json_str_corrigido = corrigir_caracteres_latex(json_str)
    
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_str_corrigido)
    
    print(f"[OK] JSON Docling salvo em: {json_path}")
    
    tempo_json = time.time() - inicio
    print(f"  Tempo da conversão: {int(tempo_json // 60)}m {int(tempo_json % 60)}s")
    
    # ========== ETAPA 2: Extrair para Markdown ==========
    print("\n[2/2] Extraindo conteúdo para Markdown...")
    
    # Exporta o documento para Markdown e corrige caracteres LaTeX
    markdown_content = documento.export_to_markdown()
    # Corrige caracteres compostos do LaTeX (ex: "´ e" -> "é")
    markdown_content_corrigido = corrigir_caracteres_latex(markdown_content)
    
    # Salva o arquivo Markdown
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown_content_corrigido)
    
    print(f"[OK] Markdown salvo em: {markdown_path}")
    
    # Estatísticas do documento
    num_chars = len(markdown_content_corrigido)
    num_lines = markdown_content_corrigido.count('\n') + 1
    print(f"\nEstatísticas do documento:")
    print(f"  - Caracteres: {num_chars:,}")
    print(f"  - Linhas: {num_lines:,}")
    
    # Exibe uma prévia do conteúdo
    print(f"\n--- Primeiras 500 caracteres do Markdown ---")
    print(markdown_content_corrigido[:500])
    print(f"\n--- Últimas 500 caracteres do Markdown ---")
    print(markdown_content_corrigido[-500:])
    
    # Tempo total
    tempo_total = time.time() - inicio
    print(f"\n=== Processamento concluído ===")
    print(f"Tempo total: {int(tempo_total // 60)}m {int(tempo_total % 60)}s")
    
    return json_path, markdown_path


def main():
    """Função principal para execução do script."""
    try:
        json_path, markdown_path = processar_pdf_credito_regeneracao()
        print(f"\n[SUCESSO] Arquivos gerados:")
        print(f"  - JSON: {json_path}")
        print(f"  - Markdown: {markdown_path}")
    except FileNotFoundError as e:
        print(f"\n[ERRO] Arquivo nao encontrado: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

