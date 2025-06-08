"""
Testes unitários para o módulo Genoma.
"""

import unittest
from modelos.genoma import Genoma

class TestGenoma(unittest.TestCase):
    """
    Testes para a classe Genoma.
    """
    
    def test_inicializacao(self):
        """
        Testa a inicialização de um Genoma.
        """
        genoma = Genoma()
        
        # Verificar se os genes foram gerados
        self.assertIsNotNone(genoma.genes)
        self.assertIsInstance(genoma.genes, dict)
        
        # Verificar se todos os genes esperados estão presentes
        genes_esperados = [
            "tamanho", "velocidade", "inteligencia", "resistencia",
            "social", "forca", "percepcao", "adaptabilidade"
        ]
        
        for gene in genes_esperados:
            self.assertIn(gene, genoma.genes)
            self.assertIsInstance(genoma.genes[gene], float)
    
    def test_combinar(self):
        """
        Testa a combinação de dois Genomas.
        """
        genoma1 = Genoma()
        genoma2 = Genoma()
        
        # Combinar genomas
        genoma_filho = genoma1.combinar(genoma2)
        
        # Verificar se o genoma filho foi criado corretamente
        self.assertIsNotNone(genoma_filho)
        self.assertIsInstance(genoma_filho, Genoma)
        
        # Verificar se todos os genes estão presentes no filho
        for gene in genoma1.genes:
            self.assertIn(gene, genoma_filho.genes)
    
    def test_aplicar_efeitos_mutacoes(self):
        """
        Testa a aplicação de efeitos de mutações.
        """
        genoma = Genoma()
        
        # Adicionar mutações
        genoma.mutacoes = ["gene_metabolismo_eficiente", "gene_visao_noturna"]
        
        # Aplicar efeitos
        modificadores = genoma.aplicar_efeitos_mutacoes()
        
        # Verificar modificadores
        self.assertIsNotNone(modificadores)
        self.assertIsInstance(modificadores, dict)
        
        # Verificar efeitos específicos
        self.assertEqual(modificadores["metabolismo"], 0.8)
        self.assertEqual(modificadores["percepcao_noturna"], 2.0)
    
    def test_to_dict(self):
        """
        Testa a conversão do Genoma para dicionário.
        """
        genoma = Genoma()
        
        # Converter para dicionário
        genoma_dict = genoma.to_dict()
        
        # Verificar estrutura do dicionário
        self.assertIsNotNone(genoma_dict)
        self.assertIsInstance(genoma_dict, dict)
        self.assertIn("genes", genoma_dict)
        self.assertIn("mutacoes", genoma_dict)
        
        # Verificar conteúdo
        self.assertIsInstance(genoma_dict["genes"], dict)
        self.assertIsInstance(genoma_dict["mutacoes"], list)

if __name__ == '__main__':
    unittest.main()


