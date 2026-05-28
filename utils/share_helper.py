# utils/share_helper.py
import urllib.parse
import webbrowser

def enviar_cardapio_whatsapp(telefone_cliente: str, produtos: list, msg_customizada: str, *args):
    """
    Formata o cardápio da Angelicia e abre o chat do WhatsApp com a mensagem pronta.
    Produtos contém: (nome, categoria, preco_venda, ingredientes)
    """
    # Cabeçalho da Mensagem
    texto = "✨ *ANGELICIA* ✨\n"
    texto += "🧁 _Doces, Bolos, Tortas e Salgados feitos com amor!_\n\n"
    
    if msg_customizada:
        texto += f"{msg_customizada}\n\n"
        
    texto += "📋 *NOSSO CARDÁPIO ATUALIZADO:*\n"
    texto += "───────────────────────\n"
    
    # Agrupando produtos por categoria
    categorias_processadas = {}
    for p in produtos:
        nome, cat, preco, ing = p
        if cat not in categorias_processadas:
            categorias_processadas[cat] = []
        categorias_processadas[cat].append((nome, preco, ing))
        
    for cat, itens in categorias_processadas.items():
        texto += f"\n🔹 *{cat.upper()}* 🔹\n"
        for nome, preco, ing in itens:
            texto += f"• *{nome}* - _R$ {preco:.2f}_\n"
            if ing:
                texto += f"  (Ingredientes: {ing})\n"
                
    texto += "\n───────────────────────\n"
    texto += "📞 *Faça seu pedido por aqui!*\n"
    texto += "📧 E-mail: amojuara@gmail.com\n"
    texto += "📱 Telefone/WhatsApp: (21) 98264-1428\n"
    texto += "\n_Angelicia | Agradecemos a preferência!_ 🥰"
    
    # Codificação da URL
    texto_codificado = urllib.parse.quote(texto)
    tel_limpo = "".join(filter(str.isdigit, telefone_cliente))
    
    url_whatsapp = f"https://wa.me/{tel_limpo}?text={texto_codificado}"
    webbrowser.open(url_whatsapp)