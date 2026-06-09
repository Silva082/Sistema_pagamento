import requests

def enviar_para_gateway(dados_cartao, valor):
    """Faz a requisição HTTP POST para a API do gateway de pagamento."""
    url = "https://api.pagarapido.com.br/v1/transacoes"
    payload = {
        "cartao": dados_cartao,
        "valor": valor
    }
    
    # Em um teste real sem mock, isso cobraria o cartão!
    response = requests.post(url, json=payload, timeout=10)
    
    if response.status_code == 500:
        raise ConnectionError("Gateway de pagamento indisponível.")
        
    return response.json()

def processar_compra(usuario_id, dados_cartao, valor):
    """Processa a compra e retorna o status do pedido."""
    try:
        resposta_gateway = enviar_para_gateway(dados_cartao, valor)
        
        status = resposta_gateway.get("status")
        
        if status == "aprovado":
            codigo = resposta_gateway.get("transacao_id")
            return f"Sucesso! Transação {codigo} confirmada."
        elif status == "recusado":
            motivo = resposta_gateway.get("motivo", "Desconhecido")
            return f"Pagamento recusado. Motivo: {motivo}."
        else:
            return "Status de pagamento desconhecido."
            
    except ConnectionError:
        return "Erro no servidor de pagamentos. Tente novamente mais tarde."
    except requests.exceptions.Timeout:
        return "Tempo de resposta esgotado. Verifique sua fatura antes de tentar de novo."
