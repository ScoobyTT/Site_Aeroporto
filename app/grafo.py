"""
app.py - Sistema de Passagens com Grafo do Nordeste
Integração completa com igraph
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from igraph import Graph

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# ========================================
# SISTEMA DE VOOS COM IGRAPH
# ========================================

class SistemaVoos:
    def __init__(self):
        """Inicializa o grafo com as capitais do Nordeste"""
        self.cidades = [
            "Salvador", "Aracaju", "Maceió", "Recife", "João Pessoa",
            "Natal", "Fortaleza", "Teresina", "São Luís", "Palmas"
        ]
        
        self.grafo = Graph(directed=True)
        self.grafo.add_vertices(self.cidades)
        
        # Rotas do Nordeste
        self.grafo.add_edges([
            ("Salvador", "Aracaju"),
            ("Aracaju", "Maceió"),
            ("Maceió", "Recife"),
            ("Recife", "João Pessoa"),
            ("João Pessoa", "Natal"),
            ("Natal", "Fortaleza"),
            ("Fortaleza", "Teresina"),
            ("Teresina", "São Luís"),
            ("São Luís", "Salvador"),
        ])
        
        # Distâncias (km)
        self.grafo.es["weight"] = [323, 276, 255, 117, 175, 524, 511, 440, 1330]
        
        self.voos_info = {}
        self._inicializar_voos()
    
    def _inicializar_voos(self):
        """Inicializa informações dos voos"""
        rotas = [
            ("Salvador", "Aracaju", 323),
            ("Aracaju", "Maceió", 276),
            ("Maceió", "Recife", 255),
            ("Recife", "João Pessoa", 117),
            ("João Pessoa", "Natal", 175),
            ("Natal", "Fortaleza", 524),
            ("Fortaleza", "Teresina", 511),
            ("Teresina", "São Luís", 440),
            ("São Luís", "Salvador", 1330),
        ]
        
        voo_id = 1
        for origem, destino, distancia in rotas:
            preco = (distancia * 0.50) + 100
            
            self.voos_info[(origem, destino)] = {
                "id": voo_id,
                "origem": origem,
                "destino": destino,
                "distancia_km": distancia,
                "preco": round(preco, 2),
                "data": "2024-01-20",
                "horario": f"{8 + (voo_id % 12):02d}:00",
                "n_assentos": 180,
                "t_aeronave": "Airbus A320",
                "milhagem": int(distancia * 1.2),
                "tipo_passagem": "Economica"
            }
            voo_id += 1
    
    def calcular_rota(self, origem, destino):
        """Calcula menor caminho usando Dijkstra"""
        try:
            caminho_ids = self.grafo.get_shortest_paths(
                origem, 
                destino, 
                weights="weight", 
                output="vpath"
            )[0]
            
            if not caminho_ids:
                return None, None
            
            rota = [self.grafo.vs[i]["name"] for i in caminho_ids]
            
            distancia_total = 0
            for i in range(len(caminho_ids) - 1):
                edge_id = self.grafo.get_eid(caminho_ids[i], caminho_ids[i+1])
                distancia_total += self.grafo.es[edge_id]["weight"]
            
            return rota, distancia_total
        except:
            return None, None
    
    def buscar_voos_diretos(self, origem, destino):
        """Busca voos diretos"""
        chave = (origem, destino)
        return [self.voos_info[chave]] if chave in self.voos_info else []
    
    def buscar_com_conexoes(self, origem, destino):
        """Busca voos com conexões"""
        diretos = self.buscar_voos_diretos(origem, destino)
        
        try:
            origem_idx = self.cidades.index(origem)
            destino_idx = self.cidades.index(destino)
        except ValueError:
            return {"diretos": diretos, "com_1_conexao": []}
        
        caminhos = self.grafo.get_all_simple_paths(origem_idx, to=destino_idx, cutoff=4)
        
        conexoes = []
        for caminho in caminhos:
            if len(caminho) == 3:  # Exatamente 1 conexão
                rota_cidades = [self.grafo.vs[i]["name"] for i in caminho]
                
                voos_rota = []
                custo_total = 0
                
                for i in range(len(caminho) - 1):
                    c1 = self.grafo.vs[caminho[i]]["name"]
                    c2 = self.grafo.vs[caminho[i+1]]["name"]
                    voo = self.voos_info.get((c1, c2))
                    
                    if voo:
                        voos_rota.append(voo)
                        custo_total += voo["preco"]
                
                if len(voos_rota) == 2:  # Tem os 2 voos
                    conexoes.append({
                        "voo1": voos_rota[0],
                        "voo2": voos_rota[1],
                        "conexao_em": rota_cidades[1],
                        "preco_total": round(custo_total, 2)
                    })
        
        return {"diretos": diretos, "com_1_conexao": conexoes}
    
    def listar_todos_voos(self):
        """Lista todos os voos"""
        return list(self.voos_info.values())


# Instância global
sistema = SistemaVoos()