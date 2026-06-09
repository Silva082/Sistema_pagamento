import pytest
from unittest.mock import Mock, patch
import requests
from pagamento import processar_compra

# Dados de teste
USUARIO_TESTE = 12345
CARTAO_VALIDO = {
    "numero": "4111111111111111",
    "validade": "12/2025",
    "cvv": "123"
}
VALOR_TESTE = 100.00


class TestSistemaPagamento:
    
    def test_desafio1_compra_aprovada(self, mocker):
        """Desafio 1: Mock de compra aprovada com código de transação"""
        
        # Mock da resposta do gateway para aprovação
        mock_resposta = Mock()
        mock_resposta.json.return_value = {
            "status": "aprovado",
            "transacao_id": "TRX-987654321"
        }
        
        # Intercepta a função enviar_para_gateway
        mocker.patch(
            'pagamento.enviar_para_gateway',
            return_value=mock_resposta.json.return_value
        )
        
        # Executa o teste
        resultado = processar_compra(USUARIO_TESTE, CARTAO_VALIDO, VALOR_TESTE)
        
        # Verificações
        assert "Sucesso" in resultado
        assert "TRX-987654321" in resultado
        assert "confirmada" in resultado
        
    def test_desafio2_cliente_sem_limite(self, mocker):
        """Desafio 2: Mock de cartão recusado por falta de limite"""
        
        # Mock da resposta do gateway para recusa
        mock_resposta = Mock()
        mock_resposta.json.return_value = {
            "status": "recusado",
            "motivo": "Limite insuficiente"
        }
        
        # Intercepta a função enviar_para_gateway
        mocker.patch(
            'pagamento.enviar_para_gateway',
            return_value=mock_resposta.json.return_value
        )
        
        # Executa o teste
        resultado = processar_compra(USUARIO_TESTE, CARTAO_VALIDO, VALOR_TESTE)
        
        # Verificações
        assert "Pagamento recusado" in resultado
        assert "Limite insuficiente" in resultado
        
    def test_desafio3_timeout_black_friday(self, mocker):
        """Desafio 3: Mock de timeout no requests.post durante Black Friday"""
        
        # Mock do requests.post para lançar Timeout
        mock_requests = mocker.patch('pagamento.requests.post')
        mock_requests.side_effect = requests.exceptions.Timeout(
            "Tempo limite excedido"
        )
        
        # Executa o teste
        resultado = processar_compra(USUARIO_TESTE, CARTAO_VALIDO, VALOR_TESTE)
        
        # Verificações
        assert "Tempo de resposta esgotado" in resultado
        assert "Verifique sua fatura" in resultado
        
    def test_extra_gateway_indisponivel(self, mocker):
        """Teste extra: Gateway retorna erro 500"""
        
        # Mock para simular erro 500 na API
        with patch('pagamento.enviar_para_gateway') as mock_envio:
            mock_envio.side_effect = ConnectionError("Gateway de pagamento indisponível.")
            
            resultado = processar_compra(USUARIO_TESTE, CARTAO_VALIDO, VALOR_TESTE)
            
            assert "Erro no servidor de pagamentos" in resultado
            
    def test_extra_status_desconhecido(self, mocker):
        """Teste extra: Gateway retorna status desconhecido"""
        
        # Mock com status não mapeado
        mock_resposta = Mock()
        mock_resposta.json.return_value = {
            "status": "pendente",
            "mensagem": "Aguardando confirmação"
        }
        
        mocker.patch(
            'pagamento.enviar_para_gateway',
            return_value=mock_resposta.json.return_value
        )
        
        resultado = processar_compra(USUARIO_TESTE, CARTAO_VALIDO, VALOR_TESTE)
        
        assert "Status de pagamento desconhecido" in resultado