"""
Grafo para busca de voos com conexões
Implementa busca de voos diretos e com 1 conexão
"""

class Grafo:
    def __init__(self):
        """Inicializa o grafo vazio"""
        self.adjacencias = {}  # {cidade: [voos que saem dessa cidade]}
    
    def limpar(self):
        """Limpa o grafo"""
        self.adjacencias = {}
    
    def adicionar_voo(self, voo):
        """
        Adiciona um voo ao grafo
        voo: dicionário com origem, destino, preco, etc.
        """
        origem = voo['origem'].lower().strip()
        
        if origem not in self.adjacencias:
            self.adjacencias[origem] = []
        
        self.adjacencias[origem].append(voo)
    
    def carregar_voos(self, voos):
        """
        Carrega múltiplos voos no grafo
        voos: lista de dicionários
        """
        self.limpar()
        for voo in voos:
            self.adicionar_voo(voo)
    
    def buscar_voos_diretos(self, origem, destino):
        """
        Busca voos diretos entre origem e destino
        Retorna: lista de voos
        """
        origem = origem.lower().strip()
        destino = destino.lower().strip()
        
        resultados = []
        
        if origem in self.adjacencias:
            for voo in self.adjacencias[origem]:
                if voo['destino'].lower().strip() == destino:
                    resultados.append(voo)
        
        return resultados
    
    def buscar_voos_com_1_conexao(self, origem, destino):
        """
        Busca voos com exatamente 1 conexão
        Retorna: lista de dicionários com {voo1, voo2, conexao_em, preco_total, tempo_total}
        """
        origem = origem.lower().strip()
        destino = destino.lower().strip()
        
        resultados = []
        
        # Verifica se a origem existe no grafo
        if origem not in self.adjacencias:
            return resultados
        
        # Para cada voo que sai da origem
        for voo1 in self.adjacencias[origem]:
            cidade_conexao = voo1['destino'].lower().strip()
            
            # Não faz conexão se já chegou no destino (isso seria voo direto)
            if cidade_conexao == destino:
                continue
            
            # Verifica se existe voo saindo da cidade de conexão
            if cidade_conexao in self.adjacencias:
                for voo2 in self.adjacencias[cidade_conexao]:
                    # Verifica se o segundo voo vai pro destino final
                    if voo2['destino'].lower().strip() == destino:
                        # Calcula preço total
                        preco_total = float(voo1.get('preco', 0)) + float(voo2.get('preco', 0))
                        
                        # Monta o resultado
                        conexao = {
                            'voo1': voo1,
                            'voo2': voo2,
                            'conexao_em': voo1['destino'],  # cidade original (com capitalização)
                            'preco_total': preco_total,
                            'origem': voo1['origem'],
                            'destino': voo2['destino']
                        }
                        
                        resultados.append(conexao)
        
        # Ordena por preço (mais barato primeiro)
        resultados.sort(key=lambda x: x['preco_total'])
        
        return resultados
    
    def buscar_todas_rotas(self, origem, destino):
        """
        Busca TODAS as rotas: diretas + com 1 conexão
        Retorna: dicionário com {diretos: [], com_1_conexao: []}
        """
        diretos = self.buscar_voos_diretos(origem, destino)
        com_conexao = self.buscar_voos_com_1_conexao(origem, destino)
        
        return {
            'diretos': diretos,
            'com_1_conexao': com_conexao,
            'total_diretos': len(diretos),
            'total_com_conexao': len(com_conexao)
        }
    
    def obter_cidades(self):
        """Retorna lista de todas as cidades no grafo"""
        cidades = set(self.adjacencias.keys())
        
        # Adiciona também os destinos
        for voos in self.adjacencias.values():
            for voo in voos:
                cidades.add(voo['destino'].lower().strip())
        
        return sorted(list(cidades))
    
    def obter_estatisticas(self):
        """Retorna estatísticas do grafo"""
        total_voos = sum(len(voos) for voos in self.adjacencias.values())
        total_cidades = len(self.obter_cidades())
        
        return {
            'total_voos': total_voos,
            'total_cidades': total_cidades,
            'cidades_com_voos_saindo': len(self.adjacencias)
        }