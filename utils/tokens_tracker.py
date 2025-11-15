#!/usr/bin/env python3
"""
Módulo para rastreamento de uso de tokens e custos em conversas com LLMs.

Permite rastrear múltiplas chamadas a LLMs (agente principal, retriever, etc.)
e gerar resumos agregados por componente e totais.
"""
from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime

try:
    from .pricing import calcular_custo, calcular_custo_detalhado
except ImportError:
    # Fallback para execução direta do script
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from pricing import calcular_custo, calcular_custo_detalhado


class TokensTracker:
    """
    Rastreador de tokens e custos para múltiplas chamadas LLM.
    
    Funcionalidades:
    - Registrar chamadas individuais com tokens, modelo e tempo
    - Calcular custos automaticamente
    - Gerar resumos por componente (agente, retriever, etc.)
    - Gerar resumo total da conversa
    - Exportar tabela detalhada de todas as chamadas
    """
    
    def __init__(self):
        """Inicializa o tracker vazio"""
        self.chamadas: List[Dict[str, Any]] = []
    
    def registrar_chamada(
        self,
        componente: str,
        model: str,
        tokens: Dict[str, int],
        elapsed_seconds: float = 0.0,
        turno: int | None = None,
        metadata: Dict[str, Any] | None = None
    ) -> None:
        """
        Registra uma chamada ao LLM.
        
        Args:
            componente: Identificador do componente (ex: "agente", "retriever", "seletor")
            model: Nome do modelo usado
            tokens: Dict com contagens de tokens {input, output, reasoning, cache_*, etc}
            elapsed_seconds: Tempo de execução em segundos
            turno: Número do turno/iteração (opcional)
            metadata: Metadados adicionais (opcional)
        """
        # Calcula custo da chamada
        custo = calcular_custo(tokens, model)
        custo_detalhado = calcular_custo_detalhado(tokens, model)
        
        # Total de tokens (usa 'total' se existir, senão calcula)
        if "total" in tokens and tokens["total"] > 0:
            total_tokens = tokens["total"]
        else:
            # Fallback: soma input + output + reasoning (sem contar total para evitar duplicação)
            total_tokens = (
                tokens.get("input", 0) + 
                tokens.get("output", 0) + 
                tokens.get("reasoning", 0)
            )
        
        # Registro da chamada
        chamada = {
            "timestamp": datetime.now().isoformat(),
            "componente": componente,
            "turno": turno,
            "model": model,
            "tokens": {
                "input": tokens.get("input", 0) or tokens.get("input_tokens", 0),
                "output": tokens.get("output", 0) or tokens.get("output_tokens", 0),
                "reasoning": tokens.get("reasoning", 0) or tokens.get("reasoning_tokens", 0),
                "cache_creation": tokens.get("cache_creation_input_tokens", 0),
                "cache_read": tokens.get("cache_read_input_tokens", 0),
                "total": total_tokens,
            },
            "custo": custo,
            "custo_detalhado": custo_detalhado,
            "elapsed_seconds": elapsed_seconds,
            "metadata": metadata or {},
        }
        
        self.chamadas.append(chamada)
    
    def obter_resumo_por_componente(self) -> Dict[str, Any]:
        """
        Gera resumo agregado por componente.
        
        Returns:
            {
                "agente": {
                    "chamadas": int,
                    "tokens": {input, output, reasoning, total},
                    "custo": float,
                    "elapsed_seconds": float
                },
                "retriever": {...},
                ...
            }
        """
        componentes: Dict[str, Any] = {}
        
        for chamada in self.chamadas:
            comp = chamada["componente"]
            
            if comp not in componentes:
                componentes[comp] = {
                    "chamadas": 0,
                    "tokens": {
                        "input": 0,
                        "output": 0,
                        "reasoning": 0,
                        "cache_creation": 0,
                        "cache_read": 0,
                        "total": 0,
                    },
                    "custo": 0.0,
                    "elapsed_seconds": 0.0,
                }
            
            # Agrega métricas
            componentes[comp]["chamadas"] += 1
            for tipo in ["input", "output", "reasoning", "cache_creation", "cache_read", "total"]:
                componentes[comp]["tokens"][tipo] += chamada["tokens"].get(tipo, 0)
            componentes[comp]["custo"] += chamada["custo"]
            componentes[comp]["elapsed_seconds"] += chamada["elapsed_seconds"]
        
        return componentes
    
    def obter_resumo_total(self) -> Dict[str, Any]:
        """
        Gera resumo total de todas as chamadas.
        
        Returns:
            {
                "total_chamadas": int,
                "total_tokens": int,
                "total_custo": float,
                "total_elapsed_seconds": float,
                "tokens_por_tipo": {input, output, reasoning, ...}
            }
        """
        total_tokens_dict = {
            "input": 0,
            "output": 0,
            "reasoning": 0,
            "cache_creation": 0,
            "cache_read": 0,
            "total": 0,
        }
        total_custo = 0.0
        total_elapsed = 0.0
        
        for chamada in self.chamadas:
            for tipo in total_tokens_dict.keys():
                total_tokens_dict[tipo] += chamada["tokens"].get(tipo, 0)
            total_custo += chamada["custo"]
            total_elapsed += chamada["elapsed_seconds"]
        
        return {
            "total_chamadas": len(self.chamadas),
            "total_tokens": total_tokens_dict["total"],
            "total_custo": total_custo,
            "total_elapsed_seconds": total_elapsed,
            "tokens_por_tipo": total_tokens_dict,
        }
    
    def obter_tabela_detalhada(self) -> List[Dict[str, Any]]:
        """
        Retorna lista detalhada de todas as chamadas (para exportação).
        
        Returns:
            Lista de dicts com campos: componente, turno, model, tokens (por tipo), custo, tempo
        """
        tabela = []
        
        for chamada in self.chamadas:
            tokens = chamada["tokens"]
            row = {
                "timestamp": chamada["timestamp"],
                "componente": chamada["componente"],
                "turno": chamada.get("turno"),
                "model": chamada["model"],
                "input_tokens": tokens["input"],
                "output_tokens": tokens["output"],
                "reasoning_tokens": tokens["reasoning"],
                "cache_creation_tokens": tokens.get("cache_creation", 0),
                "cache_read_tokens": tokens.get("cache_read", 0),
                "total_tokens": tokens["total"],
                "custo": chamada["custo"],
                "elapsed_seconds": chamada["elapsed_seconds"],
            }
            tabela.append(row)
        
        return tabela
    
    def obter_resumo_por_turno(self) -> Dict[int, Dict[str, Any]]:
        """
        Gera resumo agregado por turno.
        
        Returns:
            {
                1: {chamadas, tokens, custo, elapsed_seconds},
                2: {...},
                ...
            }
        """
        turnos: Dict[int, Any] = {}
        
        for chamada in self.chamadas:
            turno = chamada.get("turno")
            if turno is None:
                continue
            
            if turno not in turnos:
                turnos[turno] = {
                    "chamadas": 0,
                    "tokens": {
                        "input": 0,
                        "output": 0,
                        "reasoning": 0,
                        "total": 0,
                    },
                    "custo": 0.0,
                    "elapsed_seconds": 0.0,
                }
            
            turnos[turno]["chamadas"] += 1
            for tipo in ["input", "output", "reasoning", "total"]:
                turnos[turno]["tokens"][tipo] += chamada["tokens"].get(tipo, 0)
            turnos[turno]["custo"] += chamada["custo"]
            turnos[turno]["elapsed_seconds"] += chamada["elapsed_seconds"]
        
        return turnos
    
    def limpar(self) -> None:
        """Limpa todos os registros"""
        self.chamadas = []
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais úteis para debug.
        
        Returns:
            {
                "total_chamadas": int,
                "componentes_unicos": list,
                "modelos_unicos": list,
                "primeiro_timestamp": str,
                "ultimo_timestamp": str,
                "duracao_total_segundos": float
            }
        """
        if not self.chamadas:
            return {
                "total_chamadas": 0,
                "componentes_unicos": [],
                "modelos_unicos": [],
            }
        
        componentes = set(c["componente"] for c in self.chamadas)
        modelos = set(c["model"] for c in self.chamadas)
        
        timestamps = [datetime.fromisoformat(c["timestamp"]) for c in self.chamadas]
        primeiro = min(timestamps)
        ultimo = max(timestamps)
        duracao = (ultimo - primeiro).total_seconds()
        
        return {
            "total_chamadas": len(self.chamadas),
            "componentes_unicos": sorted(componentes),
            "modelos_unicos": sorted(modelos),
            "primeiro_timestamp": primeiro.isoformat(),
            "ultimo_timestamp": ultimo.isoformat(),
            "duracao_total_segundos": duracao,
        }


if __name__ == "__main__":
    # Teste básico
    print("="*70)
    print("TESTE DO TOKENS TRACKER")
    print("="*70)
    
    tracker = TokensTracker()
    
    # Simula algumas chamadas
    print("\n1. Registrando chamadas simuladas...")
    
    # Chamada 1: Agente principal
    tracker.registrar_chamada(
        componente="agente",
        model="claude-sonnet-4.5",
        tokens={"input": 5000, "output": 1000},
        elapsed_seconds=2.5,
        turno=1
    )
    
    # Chamada 2: Retriever
    tracker.registrar_chamada(
        componente="retriever",
        model="claude-haiku-3.5",
        tokens={"input": 2000, "output": 500},
        elapsed_seconds=1.2,
        turno=1
    )
    
    # Chamada 3: Agente principal (turno 2)
    tracker.registrar_chamada(
        componente="agente",
        model="claude-sonnet-4.5",
        tokens={"input": 6000, "output": 1500},
        elapsed_seconds=3.1,
        turno=2
    )
    
    print("   [OK] 3 chamadas registradas")
    
    # Teste 2: Resumo por componente
    print("\n2. RESUMO POR COMPONENTE:")
    resumo_comp = tracker.obter_resumo_por_componente()
    for comp, dados in resumo_comp.items():
        print(f"\n   {comp.upper()}:")
        print(f"   - Chamadas: {dados['chamadas']}")
        print(f"   - Tokens: {dados['tokens']['total']:,}")
        print(f"   - Custo: ${dados['custo']:.4f}")
        print(f"   - Tempo: {dados['elapsed_seconds']:.1f}s")
    
    # Teste 3: Resumo total
    print("\n3. RESUMO TOTAL:")
    resumo_total = tracker.obter_resumo_total()
    print(f"   - Total de chamadas: {resumo_total['total_chamadas']}")
    print(f"   - Total de tokens: {resumo_total['total_tokens']:,}")
    print(f"   - Custo total: ${resumo_total['total_custo']:.4f}")
    print(f"   - Tempo total: {resumo_total['total_elapsed_seconds']:.1f}s")
    
    # Teste 4: Tabela detalhada
    print("\n4. TABELA DETALHADA:")
    tabela = tracker.obter_tabela_detalhada()
    print(f"   {len(tabela)} entradas na tabela")
    for i, row in enumerate(tabela, 1):
        print(f"   [{i}] {row['componente']:10s} | Turno {row['turno']} | "
              f"{row['total_tokens']:6,} tokens | ${row['custo']:.4f}")
    
    # Teste 5: Estatísticas
    print("\n5. ESTATÍSTICAS:")
    stats = tracker.obter_estatisticas()
    print(f"   - Componentes: {', '.join(stats['componentes_unicos'])}")
    print(f"   - Modelos: {', '.join(stats['modelos_unicos'])}")
    
    print("\n" + "="*70)
    print("TESTE CONCLUÍDO")
    print("="*70)

