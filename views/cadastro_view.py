# views/cadastro_view.py
import os
import flet as ft
shadow = ft.BoxShadow(blur_radius=15, color="#E0E0E0")
from database.connection import conectar, cadastrar_novo_usuario, deletar_usuario_banco
from utils.share_helper import enviar_cardapio_whatsapp

dropdown_clientes_cardapio = None

def abrir_tela_cadastro(page: ft.Page, perfil_logado: str, usuario_logado: str):
    page.title = f"Angelicia - ERP de Gestão Visual [{perfil_logado.upper()}]"
    page.window_width = 880
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    
    EMPRESA_EMAIL = "amojuara@gmail.com"
    EMPRESA_TELEFONE = "(21) 98264-1428"
    id_produto_editando = [None] 

    pode_excluir = (perfil_logado.lower() == "root")

    # --- CONTROLES DA ABA 1: PRODUTOS (NASCENDO NA ORDEM CORRETA) ---
    input_nome = ft.TextField(label="Nome do Produto", width=400)
    dropdown_categoria = ft.Dropdown(label="Categoria", width=400)
    input_ingredientes = ft.TextField(label="Ingredientes", multiline=True, min_lines=2, max_lines=4, width=400)
    input_custo = ft.TextField(label="Custo de Produção (R$)", width=190, value="0.00")
    # Procure por 'input_venda' e adicione esses dois logo abaixo:
    input_venda = ft.TextField(label="Preço de Venda (R$)", value="0.00", width=380)
    
    # 🎯 NOVOS: Campos para ativar a promoção no produto
    switch_produto_em_promo = ft.Switch(label="Este produto está em Promoção? 🔥", value=False)
    input_preco_promocao = ft.TextField(label="Preço Promocional (Se aplicável) (R$)", value="0.00", width=380)
    
    # 1. O Texto do lucro DEVE nascer aqui (Antes de ser usado em qualquer tela ou função!)
    txt_lucro = ft.Text("Lucro Unitário: R$ 0.00", size=16, weight=ft.FontWeight.BOLD, color="#A076F9")
    
    # 2. O Dropdown de imagem nasce logo em seguida
    dropdown_imagem_arquivo = ft.Dropdown(label="Selecione a Foto do Produto (Pasta assets)", width=400)
    
    # 3. A coluna que vai listar os produtos embaixo
    grid_produtos = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=250, spacing=10)

    # ─── FUNÇÃO DE VARREDURA DA PASTA ASSETS ───
    def listar_fotos_da_pasta_assets():
        opcoes = []
        pasta_assets = "assets"
        extensoes_validas = (".png", ".jpg", ".jpeg", ".webp", ".gif")
        if os.path.exists(pasta_assets):
            for arquivo in os.listdir(pasta_assets):
                if arquivo.lower().endswith(extensoes_validas):
                    opcoes.append(ft.dropdown.Option(arquivo))
        if not opcoes:
            opcoes.append(ft.dropdown.Option(text="Nenhuma imagem encontrada na pasta assets", key=""))
        dropdown_imagem_arquivo.options = opcoes
    # ─────────────────────────────────────────────

    # --- CONTROLES DA ABA 2: CATEGORIAS ---
    input_nova_categoria = ft.TextField(label="Nome da Nova Categoria", width=300)
    listview_categorias = ft.ListView(expand=True, spacing=10, height=200)

    # --- CONTROLES DA ABA 3: CARDÁPIO VISUAL MÓVEL (COM FILTROS) ---
    input_tel_cliente = ft.TextField(label="WhatsApp do Cliente (Com DDD)", width=380, hint_text="Ex: 21999998888")
    input_msg_promo = ft.TextField(label="Mensagem Promocional Opcional", width=380, hint_text="Ex: Promoção da Semana! 🍰")
    input_link_foto = ft.TextField(label="Link do Cardápio Completo (Opcional)", width=380, hint_text="Ex: https://imgur.com/link")
    
    # 🎯 NOVOS FILTROS DO CARDÁPIO:
    dropdown_filtro_categoria_cardapio = ft.Dropdown(
        label="Filtrar Categoria no Celular", 
        width=230,
        value="Todos" # Valor padrão
    )
    
    switch_apenas_promocao = ft.Switch(
        label="Apenas Promoções 🔥", 
        value=False
    )
    
    container_celular_feed = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    # 🎯 COLOQUE ESSE BLOCO NOVO AQUI:
    # --- CONTROLES DA ABA: CARDÁPIO ---
    dropdown_clientes_cardapio = ft.Dropdown(
        label="Selecione o Cliente para o Envio",
        width=350,
        on_select=lambda e: selecionar_cliente_cardapio(dropdown_clientes_cardapio)
    )

    # --- CONTROLES DA ABA 4: VENDAS ---
    dropdown_venda_produto = ft.Dropdown(label="Selecione o Produto", width=400)
    
    dropdown_venda_cliente = ft.Dropdown(
        label="Selecione o Cliente (Opcional)", 
        width=400,
        on_select=lambda e: selecionar_cliente_cardapio(dropdown_venda_cliente) # 🎯 Passa ele mesmo como referência
    )
    input_venda_qtd = ft.TextField(label="Qtd", width=400, value="1")
    txt_status_venda = ft.Text("", weight=ft.FontWeight.BOLD)
    
    card_faturamento = ft.Text("R$ 0.00", size=20, weight="bold", color="green")
    card_custo_total = ft.Text("R$ 0.00", size=20, weight="bold", color="red")
    card_lucro_real = ft.Text("R$ 0.00", size=20, weight="bold", color="blue")
    grid_historico_vendas = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=150, spacing=5)

    # --- CONTROLES DA ABA 5: SEGURANÇA ---
    input_senha_atual_me = ft.TextField(label="Sua Senha Atual", password=True, can_reveal_password=True, width=380)
    input_nova_senha_me = ft.TextField(label="Nova Senha", password=True, can_reveal_password=True, width=380)
    txt_status_me = ft.Text("", weight=ft.FontWeight.BOLD)
    input_novo_user = ft.TextField(label="Nome do Novo Usuário / Cliente", width=380)
    
    # 🎯 NOVO: Define se é operador (entra no sistema) ou cliente (vai para o CRM)
    dropdown_tipo_contato = ft.Dropdown(
        label="Tipo de Cadastro",
        width=380,
        options=[
            ft.dropdown.Option("operador", "Operador (Acessa o Sistema)"),
            ft.dropdown.Option("Cliente", "Cliente (Para o CRM/Fidelização)")
        ],
        value="Cliente"
    )
    input_nova_senha = ft.TextField(label="Senha Inicial", password=True, can_reveal_password=True, width=380)
    dropdown_perfil_user = ft.Dropdown(label="Perfil", width=380, options=[ft.dropdown.Option("user", "Usuário Comum"), ft.dropdown.Option("root", "Administrador Master")])
    txt_status_usuarios = ft.Text("", weight=ft.FontWeight.BOLD)
    listview_operadores = ft.ListView(expand=True, spacing=10, height=150)

    # ─────────────────────────────────────────────────────────────────
    # 🎯 FIXADO AQUI: CONTROLES DA NOVA ABA DE CRM & FIDELIZAÇÃO
    # ─────────────────────────────────────────────────────────────────
    dropdown_filtro_dias = ft.Dropdown(
        label="Clientes sem comprar há pelo menos:",
        width=350,
        options=[
            ft.dropdown.Option("5", "5 dias"),
            ft.dropdown.Option("10", "10 dias"),
            ft.dropdown.Option("15", "15 dias (Recomendado)"),
            ft.dropdown.Option("20", "20 dias"),
            ft.dropdown.Option("25", "25 dias"),
            ft.dropdown.Option("30", "30 dias (Crítico ⚠️)"),
        ],
        value="15"
    )

    input_mensagem_crm = ft.TextField(
        label="Mensagem de Saudades (Use {nome} para personalizar)", 
        multiline=True,
        min_lines=2,
        max_lines=3,
        width=400,
        value="Olá, {nome}! Notamos que você sumiu essa semana... 🧁 Que tal deixar seu dia mais doce com as nossas novidades? O cardápio atualizado está pronto para você escolher!"
    )
    
    grid_clientes_sumidos = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=300, spacing=10)
    # ─────────────────────────────────────────────────────────────────

    # 🎯 NOVA: Função para preparar a edição de categorias que estava faltando!
    def preparar_edicao_categoria(cid, cnome):
        # Armazena o ID da categoria que você está editando na memória do sistema
        # (Se a sua variável de controle tiver outro nome, ajuste aqui, ex: id_categoria_editando)
        try:
            id_categoria_editando[0] = cid
        except:
            pass
            
        # Joga o nome antigo de volta para a sua caixinha de texto para você poder alterar
        input_nova_categoria.value = cnome
        page.update()

    # --- RECARREGADORES DE DADOS VISUAIS ---
    def recarregar_categorias(e=None):
        # 🎯 CORREÇÃO: Usando o nome exato da sua variável de tela!
        listview_categorias.controls.clear() 
        
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        
        # 1. Alimenta a sua lista na tela com os botões Editar e Excluir
        for row in rows:
            try:
                cat_id, cat_nome = row
                
                listview_categorias.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CATEGORY, color="#6F42C1"),
                            ft.Text(cat_nome, size=14, weight="bold", color="black", expand=True),
                            
                            # 🔄 Botão Editar (Abre a função para alterar o nome)
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color="blue_700",
                                on_click=lambda e, cid=cat_id, cnome=cat_nome: preparar_edicao_categoria(cid, cnome)
                            ),
                            
                            # ❌ Botão Excluir Categoria
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red_700",
                                on_click=lambda e, cid=cat_id: excluir_categoria(cid)
                            )
                        ]),
                        padding=10, border=ft.Border.all(1, "#E3F2FD"), border_radius=8, bgcolor="white"
                    )
                )
            except Exception as err_cat:
                print(f"Erro ao desenhar linha de categoria: {err_cat}")

        # 2. Alimenta o Dropdown de CADASTRO de produtos usando o nome correto (r[1] que é o texto)
        try:
            dropdown_categoria.options = [ft.dropdown.Option(r[1]) for r in rows]
        except:
            pass
        
        # 3. Alimenta o Dropdown de FILTRO da aba Cardápio
        try:
            dropdown_filtro_categoria_cardapio.options = [ft.dropdown.Option("Todos")] + [ft.dropdown.Option(r[1]) for r in rows]
        except:
            pass
            
        page.update()

    
    def recarregar_lista_produtos(e=None):
        grid_produtos.controls.clear() 
        
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, categoria, preco_venda, custo_producao, ingredientes, foto_path, em_promocao, preco_promocao 
            FROM produtos 
            ORDER BY categoria, nome
        """)
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            try:
                p_id, p_nome, p_cat, p_venda, p_custo, p_ing, p_img, p_em_promo, p_pre_promo = row
                status_promo = f" 🔥 (Promo: R$ {p_pre_promo:.2f})" if p_em_promo == 1 else ""
                
                # 🛠️ Desenha o container de cada produto diretamente na tela
                grid_produtos.controls.append(
                    ft.Container(
                        content=ft.Row([
                            # Foto ou Ícone
                            ft.Icon(ft.Icons.CAKE, color="#6F42C1") if not p_img else ft.Image(src=f"/{p_img}", width=40, height=40, fit="cover", border_radius=5),
                            
                            # Textos
                            ft.Column([
                                ft.Text(f"{p_nome}{status_promo}", size=14, weight="bold", color="black"),
                                ft.Text(f"Categoria: {p_cat} | Custo: R$ {p_custo:.2f} | Venda: R$ {p_venda:.2f}", size=12, color="grey700")
                            ], expand=True),
                            
                            # Botão Editar (Chama sua def preparar_edicao)
                            ft.IconButton(
                                icon=ft.Icons.EDIT, 
                                icon_color="blue_700",
                                on_click=lambda e, item=row: preparar_edicao(item)
                            ),
                            
                            # Botão Deletar Direto (Sem travar com 'pode_excluir')
                            ft.IconButton(
                                icon=ft.Icons.DELETE, 
                                icon_color="red_700",
                                on_click=lambda e, idx=p_id: deletar_produto(idx)
                            )
                        ]),
                        padding=10, 
                        border=ft.Border.all(1, "#E3F2FD"), 
                        border_radius=8, 
                        bgcolor="white"
                    )
                )
            except Exception as erro_render:
                print(f"Erro em um produto específico: {erro_render}")
            
        # Tenta atualizar o celular do cardápio se ele já estiver pronto na tela
        try:
            filtrar_e_recarregar_cardapio_celular()
        except:
            pass
            
        page.update() # <-- Atualiza o layout do Flet

    def recarregar_dropdown_clientes_venda():
        # Limpa as opções antigas com segurança
        try:
            dropdown_clientes_cardapio.options.clear()
        except: pass
        try:
            dropdown_venda_cliente.options.clear()
        except: pass
        
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM contatos WHERE tipo = 'Cliente' ORDER BY nome")
        clientes = cursor.fetchall()
        conn.close()
        
        for cid, nome in clientes:
            # Alimenta o dropdown do cardápio
            try:
                dropdown_clientes_cardapio.options.append(ft.dropdown.Option(key=str(cid), text=nome))
            except: pass
            # Alimenta o dropdown de vendas
            try:
                dropdown_venda_cliente.options.append(ft.dropdown.Option(key=str(cid), text=nome))
            except: pass
            
        # 🎯 O SEGREDO AQUI: Em vez de atualizar cada dropdown individualmente e dar erro,
        # atualizamos a página inteira de uma vez com segurança!
        try:
            page.update()
        except:
            pass

    def recarregar_dropdown_produtos_venda():
        # 🎯 CORREÇÃO: Usando o seu nome exato 'dropdown_venda_produto'
        dropdown_venda_produto.options = []
        
        conn = conectar()
        cursor = conn.cursor()
        # Busca as 9 colunas do banco para não travar com o sistema de promoções
        cursor.execute("""
            SELECT id, nome, categoria, preco_venda, custo_producao, ingredientes, foto_path, em_promocao, preco_promocao 
            FROM produtos 
            ORDER BY nome
        """)
        rows = cursor.fetchall()
        conn.close()
        
        opcoes = []
        for row in rows:
            try:
                p_id, p_nome, p_cat, p_venda, p_custo, p_ing, p_img, p_em_promo, p_pre_promo = row
                
                # 🔥 LÓGICA DO CAIXA: Se estiver em promoção, o preço vira o promocional na hora!
                preco_final = p_pre_promo if p_em_promo == 1 else p_venda
                tag_promo = " (PROMO 🔥)" if p_em_promo == 1 else ""
                
                opcoes.append(
                    ft.dropdown.Option(
                        key=str(p_id), 
                        text=f"{p_nome} — R$ {preco_final:.2f}{tag_promo}" 
                    )
                )
            except Exception as e_drop:
                print(f"Erro ao carregar produto no dropdown de venda: {e_drop}")
                
        # 🎯 CORREÇÃO: Atualiza a sua variável de tela
        dropdown_venda_produto.options = opcoes
        page.update()

    # ─────────────────────────────────────────────────────────────────
    # 💥 COLE A FUNÇÃO ABAIXO EXATAMENTE AQUI (ALINHADA COM A ANTERIOR)
    # ─────────────────────────────────────────────────────────────────
    def filtrar_e_recarregar_cardapio_celular(e=None):
            cat_filtrada = dropdown_filtro_categoria_cardapio.value
            s_promo = switch_apenas_promocao.value
            
            conn = conectar()
            cursor = conn.cursor()
            
            # Monta a busca no banco aplicando os filtros que você escolheu na tela
            query = "SELECT id, nome, categoria, preco_venda, custo_producao, ingredientes, foto_path, em_promocao, preco_promocao FROM produtos WHERE 1=1"
            parametros = []
            
            if cat_filtrada and cat_filtrada != "Todos":
                query += " AND categoria = ?"
                parametros.append(cat_filtrada)
                
            if s_promo:
                query += " AND em_promocao = 1"
                
            query += " ORDER BY categoria, nome"
            cursor.execute(query, tuple(parametros))
            produtos = cursor.fetchall()
            conn.close()
            
            # 🎯 AQUI ESTÁ O SEGREDO: Ela pega os produtos filtrados e joga para a função que desenha!
            desenhar_feed_celular(produtos)

        # Vincula os filtros da tela para rodarem a busca sozinhos ao clicar
    dropdown_filtro_categoria_cardapio.on_change = filtrar_e_recarregar_cardapio_celular
    switch_apenas_promocao.on_change = filtrar_e_recarregar_cardapio_celular

    def desenhar_feed_celular(produtos):
        container_celular_feed.controls.clear()
        container_celular_feed.controls.append(
            ft.Text("🧁 CARDÁPIO ANGELICIA 🧁", size=16, weight="bold", color="#6F42C1", text_align="center")
        )
        
        cat_atual = ""
        for p_id, p_nome, p_cat, p_venda, p_custo, p_ing, p_img, p_em_promo, p_pre_promo in produtos:
            if p_cat != cat_atual:
                cat_atual = p_cat
                container_celular_feed.controls.append(
                    ft.Container(
                        content=ft.Text(cat_atual.upper(), size=12, weight="bold", color="white"),
                        bgcolor="#6F42C1", padding=5, border_radius=3, margin=ft.Margin.only(top=10)
                    )
                )
            
            caminho_foto = f"/{p_img}" if p_img else "/default_cake.png"
            
            # 🛡️ Bloco corrigido e seguro aqui:
            if p_em_promo == 1:
                preco_layout = ft.Row([
                    ft.Text(f"De: R$ {p_venda:.2f}", size=11, color="red_400"),
                    ft.Text(f"Por: R$ {p_pre_promo:.2f}", size=14, weight="bold", color="green_700"),
                    ft.Container(content=ft.Text("PROMO 🔥", size=8, color="white", weight="bold"), bgcolor="red_700", padding=3, border_radius=3)
                ], spacing=5)
            else:
                preco_layout = ft.Text(f"R$ {p_venda:.2f}", size=14, weight="bold", color="green_700")

            container_celular_feed.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Image(src=caminho_foto, width=320, height=130, fit="cover", border_radius=ft.BorderRadius.only(top_left=8, top_right=8)),
                        ft.Container(
                            padding=8,
                            content=ft.Column([
                                ft.Text(p_nome, size=14, weight="bold", color=ft.Colors.BLACK),
                                ft.Text(p_ing if p_ing else "Especialidade da Casa", size=10, color="grey600"),
                                ft.Row([
                                    preco_layout,
                                    ft.Container(content=ft.Text("Pedir", size=10, color="white"), bgcolor="#A076F9", padding=4, border_radius=5)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            ], spacing=2)
                        )
                    ], spacing=0),
                    bgcolor=ft.Colors.WHITE, border_radius=8, border=ft.Border.all(1, "#E3F2FD")
                )
            )
        page.update()

    def recarregar_relatorios():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(v.valor_total), 0), COALESCE(SUM(p.custo_producao * v.quantidade), 0) FROM vendas v JOIN produtos p ON v.produto_id = p.id")
        fat, custo = cursor.fetchone()
        card_faturamento.value = f"R$ {fat:.2f}"
        card_custo_total.value = f"R$ {custo:.2f}" if pode_excluir else "RESTRITO"
        card_lucro_real.value = f"R$ {(fat - custo):.2f}" if pode_excluir else "RESTRITO"
        
        cursor.execute("SELECT v.id, p.nome, v.quantidade, v.valor_total, v.data_venda FROM vendas v JOIN produtos p ON v.produto_id = p.id ORDER BY v.id DESC LIMIT 10")
        vendas = cursor.fetchall()
        grid_historico_vendas.controls.clear()
        for v in vendas:
            v_id, p_nome, v_qtd, v_total, v_data = v
            grid_historico_vendas.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SHOPPING_BAG, color="#A076F9", size=16),
                        ft.Column([ft.Text(f"{v_qtd}x {p_nome} = R$ {v_total:.2f}", size=13, weight="bold"), ft.Text(f"Data: {v_data[:16]}", size=10, color="grey600")], expand=True),
                        ft.IconButton(icon=ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED_400 if pode_excluir else ft.Colors.GREY_400, disabled=not pode_excluir, on_click=lambda e, idx=v_id: estornar_venda(idx))
                    ]), padding=5, border=ft.Border(bottom=ft.BorderSide(1, "#E3F2FD"))
                )
            )
        conn.close()
        page.update()

    def recarregar_lista_usuarios(e=None):
        listview_operadores.controls.clear()
        
        conn = conectar()
        cursor = conn.cursor()
        try:
            # 🎯 BUSCA TURBINADA: Agora buscamos todas as colunas de endereço ordenadas
            cursor.execute("SELECT id, nome, tipo, telefone, cep, endereco, bairro, estado FROM contatos ORDER BY tipo, nome")
            rows = cursor.fetchall()
        except Exception as err_banco:
            print(f"Erro ao ler tabela no banco: {err_banco}")
            rows = []
        finally:
            conn.close()
        
        for row in rows:
            try:
                # 🕵️‍♂️ PROTEÇÃO MÁXIMA MANTIDA: Mapeia cada dado com segurança
                c_id = row[0]
                c_nome = str(row[1]) if row[1] is not None else "Sem Nome"
                c_tipo = str(row[2]) if row[2] is not None else "Não Definido"
                
                # Coleta os novos campos tratando valores nulos com segurança
                c_tel = str(row[3]) if row[3] is not None else ""
                c_cep = str(row[4]) if row[4] is not None else ""
                c_end = str(row[5]) if row[5] is not None else ""
                c_bai = str(row[6]) if row[6] is not None else ""
                c_est = str(row[7]) if row[7] is not None else ""
                
                icone = ft.Icons.PERSON if c_tipo == "Cliente" else "🔐"
                
                # 📝 FUNÇÃO INTERNA: Abre a janela pop-up para Ver e Editar tudo
                def abrir_detalhes_cliente(id_alvo, nome_atual, tel_atual, cep_atual, end_atual, bai_atual, est_atual):
                    edit_nome = ft.TextField(label="Nome", value=nome_atual, width=300, color="black")
                    edit_tel = ft.TextField(label="Telefone", value=tel_atual, width=300, color="black")
                    edit_cep = ft.TextField(label="CEP", value=cep_atual, width=300, color="black")
                    edit_end = ft.TextField(label="Endereço", value=end_atual, width=300, color="black")
                    edit_bai = ft.TextField(label="Bairro", value=bai_atual, width=300, color="black")
                    edit_est = ft.TextField(label="Estado", value=est_atual, width=300, max_length=2, color="black")

                    def salvar_alteracoes(ev):
                        try:
                            conexao = conectar()
                            ctx = conexao.cursor()
                            ctx.execute("""
                                UPDATE contatos 
                                SET nome=?, telefone=?, cep=?, endereco=?, bairro=?, estado=? 
                                WHERE id=?
                            """, (edit_nome.value.strip(), edit_tel.value.strip(), edit_cep.value.strip(), 
                                  edit_end.value.strip(), edit_bai.value.strip(), edit_est.value.strip(), id_alvo))
                            conexao.commit()
                            conexao.close()
                            
                            janela_dialogo.open = False # Fecha a janela
                            recarregar_lista_usuarios() # Atualiza a listagem na tela
                            
                            page.snack_bar = ft.SnackBar(ft.Text("✅ Cadastro atualizado com sucesso!"))
                            page.snack_bar.open = True
                            page.update()
                        except Exception as err_up:
                            print(f"Erro ao atualizar: {err_up}")

                    def fechar_janela(ev):
                        janela_dialogo.open = False
                        page.update()

                    janela_dialogo = ft.AlertDialog(
                        title=ft.Text(f"📋 Cadastro Completo: {nome_atual}", weight="bold"),
                        content=ft.Column([
                            edit_nome, edit_tel, edit_cep, edit_end, edit_bai, edit_est
                        ], tight=True, scroll=ft.ScrollMode.AUTO),
                        actions=[
                            ft.TextButton("Cancelar", on_click=fechar_janela),
                            ft.ElevatedButton("Salvar Alterações", bgcolor="#6F42C1", color="white", on_click=salvar_alteracoes)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    # 🎯 AJUSTE DE OURO PARA O POP-UP ABRIR NO CLIQUE:
                    page.overlay.append(janela_dialogo) # Envia a janela para a frente da tela
                    janela_dialogo.open = True          # Ativa a abertura
                    page.update()                       # Redesenha a interface na mesma hora
                    return                              # Finaliza o clique com sucesso

                # 🛠️ CONSTRUÇÃO DA LINHA VISUAL COM DOIS BOTÕES (EDITAR/VIEW + DELETAR)
                listview_operadores.controls.append(
                    ft.Container(
                        data=c_id, 
                        content=ft.Row([
                            ft.Icon(icone, color="#6F42C1"),
                            ft.Text(f"{c_nome} ({c_tipo})", size=14, weight="bold", expand=True, color="black"),
                            
                            # ✏️ NOVO BOTÃO: Abre o pop-up com os dados cadastrais (Serve para VER e EDITAR)
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color="#6F42C1",
                                tooltip="Visualizar / Editar dados completos",
                                on_click=lambda e, ia=c_id, na=c_nome, ta=c_tel, cp=c_cep, ed=c_end, br=c_bai, es=c_est: 
                                         abrir_detalhes_cliente(ia, na, ta, cp, ed, br, es)
                            ),
                            
                            # 🗑️ SEU BOTÃO ORIGINAL: Mantido com a função exata que já funcionava
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red_400",
                                on_click=lambda e, idx=c_id: executar_exclusao_usuario(idx) 
                            )
                        ]),
                        padding=8, 
                        border=ft.Border.all(1, "#E3F2FD"), 
                        border_radius=5,
                        bgcolor="white" 
                    )
                )
            except Exception as err_linha:
                print(f"Pulando registro com erro visual: {err_linha}")
                continue
                
        try:
            listview_operadores.update()
        except:
            pass
        page.update()

    def executar_exclusao_usuario(username_alvo):
        try:
            # 1. Executa a deleção no banco usando a função oficial
            # Ela aceita o ID ou o Nome do contato
            deletar_usuario_banco(username_alvo)
            
            txt_status_usuarios.value = "🗑️ Registro removido com sucesso!"
            txt_status_usuarios.color = "green_700"
            
        except Exception as e:
            # Caso dê algum erro no banco, ele avisa aqui
            txt_status_usuarios.value = f"❌ Erro ao deletar: {e}"
            txt_status_usuarios.color = "red_700"
        
        # 2. 🎯 RECARREGA A TELA NA HORA!
        # Agora que o banco apagou, essa função limpa e redesenha os nomes atuais
        recarregar_lista_usuarios()
        
        # 3. Atualiza os dropdowns do cardápio e do caixa
        try:
            recarregar_dropdown_clientes_venda()
        except:
            pass
            
        page.update()

    # --- OPERAÇÕES DO BANCO (CRUD) ---
    def calcular_lucro_dinamico(e):
        try:
            c = float(input_custo.value.replace(",", ".")) if input_custo.value else 0.0
            v = float(input_venda.value.replace(",", ".")) if input_venda.value else 0.0
            txt_lucro.value = f"Lucro Unitário: R$ {(v - c):.2f}"
        except: pass
        page.update()

    input_custo.on_change = calcular_lucro_dinamico
    input_venda.on_change = calcular_lucro_dinamico

    def salvar_ou_atualizar_produto(e):
        nome = input_nome.value.strip()
        cat = dropdown_categoria.value
        ing = input_ingredientes.value.strip()
        img = dropdown_imagem_arquivo.value
        
        # 🎯 COLETA OS NOVOS CAMPOS DE PROMOÇÃO
        em_promo_status = 1 if switch_produto_em_promo.value else 0
        try:
            custo = float(input_custo.value.replace(",", "."))
            venda = float(input_venda.value.replace(",", "."))
            # Converte o preço da promoção
            promo_preco = float(input_preco_promocao.value.replace(",", "."))
        except: 
            return
        if not nome or not cat: 
            return

        conn = conectar()
        cursor = conn.cursor()
        
        if id_produto_editando[0] is None:
            # ➕ ROTA A: Produto Novo (Adicionado em_promocao e preco_promocao)
            cursor.execute("""
                INSERT INTO produtos (nome, categoria, preco_venda, custo_producao, ingredientes, foto_path, em_promocao, preco_promocao) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cat, venda, custo, ing, img, em_promo_status, promo_preco))
        else:
            # 🔄 ROTA B: Editar Produto Existente (Adicionado em_promocao e preco_promocao)
            cursor.execute("""
                UPDATE produtos 
                SET nome=?, categoria=?, preco_venda=?, custo_producao=?, ingredientes=?, foto_path=?, em_promocao=?, preco_promocao=? 
                WHERE id=?
            """, (nome, cat, venda, custo, ing, img, em_promo_status, promo_preco, id_produto_editando[0]))
            
        conn.commit()
        conn.close()
        
        # Reseta a memória de edição
        id_produto_editando[0] = None
        
        # 🧼 Limpa todos os campos da tela (incluindo os novos)
        input_nome.value = ""
        input_ingredientes.value = ""
        dropdown_imagem_arquivo.value = None
        input_custo.value = "0.00"
        input_venda.value = "0.00"
        switch_produto_em_promo.value = False # Reseta o interruptor
        input_preco_promocao.value = "0.00"   # Reseta o preço
        
        recarregar_lista_produtos()
        recarregar_relatorios()

    def preparar_edicao(item):
        # Desempacota as 9 colunas do produto que veio do banco de dados
        p_id, p_nome, p_cat, p_venda, p_custo, p_ing, p_img, p_em_promo, p_pre_promo = item
        
        # Preenche os campos normais da tela com os dados dele
        id_produto_editando[0] = p_id
        input_nome.value = p_nome
        dropdown_categoria.value = p_cat
        input_ingredientes.value = p_ing
        input_custo.value = f"{p_custo:.2f}"
        input_venda.value = f"{p_venda:.2f}"
        dropdown_imagem_arquivo.value = p_img
        
        # 🎯 NOVO: Preenche os novos campos de promoção na tela para você alterar!
        switch_produto_em_promo.value = True if p_em_promo == 1 else False
        input_preco_promocao.value = f"{p_pre_promo:.2f}"
        
        page.update()

    def deletar_produto(idx):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=?", (idx,))
        conn.commit()
        conn.close()
        recarregar_lista_produtos()
        recarregar_relatorios()

    def adicionar_categoria(e):
        nova_cat = input_nova_categoria.value.strip()
        if nova_cat:
            conn = conectar()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nova_cat,))
                conn.commit()
                input_nova_categoria.value = ""
                recarregar_categorias()
            except: pass
            conn.close()

    def excluir_categoria(cid):
        # ... (Deixe as linhas de conectar e executar o DELETE que você já tem aí) ...
        # Garanta que o comando seja parecido com: cursor.execute("DELETE FROM categorias WHERE id = ?", (cid,))
        
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categorias WHERE id = ?", (cid,))
        conn.commit()
        conn.close()
        
        # 🎯 O SEGREDO ESTÁ AQUI: Força o sistema a apagar o item da tela na hora!
        recarregar_categorias()
        page.update()

    def realizar_venda(e):
        p_id = dropdown_venda_produto.value
        try: qtd = int(input_venda_qtd.value)
        except: return
        if not p_id or qtd <= 0: return
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT preco_venda FROM produtos WHERE id = ?", (p_id,))
        preco = cursor.fetchone()[0]
        cursor.execute("INSERT INTO vendas (produto_id, quantidade, valor_total) VALUES (?, ?, ?)", (p_id, qtd, preco * qtd))
        conn.commit()
        conn.close()
        recarregar_relatorios()

    def estornar_venda(venda_id):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
        conn.commit()
        conn.close()
        recarregar_relatorios()

    def realizar_logoff(e):
        page.clean()
        from views.login_view import abrir_tela_login
        abrir_tela_login(page, lambda p, u: abrir_tela_cadastro(page, p, u))

    def alterar_minha_senha(e):
        atual = input_senha_atual_me.value.strip()
        nova = input_nova_senha_me.value.strip()
        if not atual or not nova: return
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = ?", (usuario_logado,))
        hash_salvo = cursor.fetchone()[0]
        from utils.security import verificar_senha
        if verificar_senha(atual, hash_salvo):
            cursor.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", (gerar_hash_senha(nova), usuario_logado))
            conn.commit()
            txt_status_me.value = "Senha alterada!"
            txt_status_me.color = "green"
        conn.close()
        page.update()

    # 🎯 NOVOS CAMPOS DE ENDEREÇO (Colados logo acima da def executar_cadastro_usuario)
    input_cep_cliente = ft.TextField(label="CEP", width=350, hint_text="00000-000", color="black")
    input_endereco_cliente = ft.TextField(label="Endereço (Rua, Nº, Compl.)", width=350, color="black")
    input_bairro_cliente = ft.TextField(label="Bairro", width=350, color="black")
    input_estado_cliente = ft.TextField(label="Estado (UF)", width=350, max_length=2, hint_text="RJ", color="black")
    
    def executar_cadastro_usuario(e=None):
        nome = input_novo_user.value.strip() if input_novo_user.value else ""
        tipo_contato = dropdown_tipo_contato.value # 'Cliente' ou 'Usuario'
        
        telefone_cliente = input_tel_cliente.value.strip() if input_tel_cliente.value else ""
        # 🎯 COLETANDO OS NOVOS CAMPOS DE ENDEREÇO DA TELA (Coloque dentro da def)
        cep_cliente = input_cep_cliente.value.strip() if input_cep_cliente.value else ""
        endereco_cliente = input_endereco_cliente.value.strip() if input_endereco_cliente.value else ""
        bairro_cliente = input_bairro_cliente.value.strip() if input_bairro_cliente.value else ""
        estado_cliente = input_estado_cliente.value.strip() if input_estado_cliente.value else ""
        senha_usuario = input_nova_senha.value.strip() if input_nova_senha.value else ""
        
        # 🎯 COLETANDO OS NOVOS CAMPOS DE ENDEREÇO DA TELA
        cep_cliente = input_cep_cliente.value.strip() if input_cep_cliente.value else ""
        endereco_cliente = input_endereco_cliente.value.strip() if input_endereco_cliente.value else ""
        bairro_cliente = input_bairro_cliente.value.strip() if input_bairro_cliente.value else ""
        estado_cliente = input_estado_cliente.value.strip() if input_estado_cliente.value else ""
        
        if not nome:
            txt_status_usuarios.value = "❌ Digite o nome do cadastro!"
            txt_status_usuarios.color = "red_700"
            page.update()
            return

        # Define as variáveis baseado no tipo
        if tipo_contato == "Cliente":
            tipo_banco = "Cliente"
            dado_salvar = telefone_cliente  # Salva o telefone real
        else:
            tipo_banco = "Usuario"
            dado_salvar = senha_usuario     # Salva a senha se for operador

        # 💾 Gravação Inteligente no Banco de Dados
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            # 🔗 GRAVAÇÃO TURBINADA: Tenta salvar com todas as colunas novas de endereço
            try:
                cursor.execute("""
                    INSERT INTO contatos (nome, tipo, telefone, cep, endereco, bairro, estado) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nome, tipo_banco, dado_salvar, cep_cliente, endereco_cliente, bairro_cliente, estado_cliente))
            except:
                cursor.execute("""
                    INSERT INTO contatos (nome, tipo, telefone) 
                    VALUES (?, ?, ?)
                """, (nome, tipo_banco, dado_salvar))
                
            conn.commit()
            conn.close()
            
            # ✨ Limpa todos os campos da tela após o sucesso (incluindo os novos!)
            input_novo_user.value = ""
            input_nova_senha.value = ""
            input_tel_cliente.value = ""  
            input_cep_cliente.value = ""
            input_endereco_cliente.value = ""
            input_bairro_cliente.value = ""
            input_estado_cliente.value = ""
            
            txt_status_usuarios.value = f"✅ {tipo_contato} registrado com sucesso!"
            txt_status_usuarios.color = "green_700"
            
            # 🔄 Atualiza as listagens e o cardápio na mesma hora!
            try:
                recarregar_lista_usuarios() 
            except: pass
            
            try:
                recarregar_dropdown_clientes_venda() 
            except: pass
                
        except Exception as erro_banco:
            txt_status_usuarios.value = f"❌ Erro: {erro_banco}"
            txt_status_usuarios.color = "red_700"
            
        page.update()

    def disparar_cardapio(e):
        tel = input_tel_cliente.value.strip()
        if not tel: return
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, categoria, preco_venda, ingredientes FROM produtos ORDER BY categoria")
        produtos_banco = cursor.fetchall()
        conn.close()
        enviar_cardapio_whatsapp(tel, produtos_banco, input_msg_promo.value.strip(), input_link_foto.value.strip())
    
    def selecionar_cliente_cardapio(e):
        # 🎯 ATUALIZADO: Agora lê o dropdown específico do Cardápio!
        cliente_id = dropdown_clientes_cardapio.value  
        if not cliente_id:
            return
            
        conn = conectar()
        cursor = conn.cursor()
        # Busca o telefone do cliente no banco pelo ID ou pelo nome se o ID falhar
        cursor.execute("SELECT telefone FROM contatos WHERE id = ? OR nome = ?", (cliente_id, cliente_id))
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado and resultado[0]:
            # Joga o telefone direto na caixinha que o WhatsApp lê!
            input_tel_cliente.value = str(resultado[0])
        else:
            input_tel_cliente.value = ""
            
        # 🎯 ATUALIZADO: Atualiza especificamente o campo de telefone na tela
        input_tel_cliente.update()

    # --- MONTAGEM DAS TELAS FILHAS ---
    btn_salvar = ft.ElevatedButton(content=ft.Text("Cadastrar Produto", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), bgcolor="#A076F9", width=400, on_click=salvar_ou_atualizar_produto)
    
    #  A sua coluna de cadastro de produtos corrigida com a lista inclusa!
    tela_produtos = ft.Column([
        ft.Text("📦 CADASTRO DE PRODUTOS", weight="bold", size=16),
        input_nome,
        dropdown_categoria,
        input_ingredientes,
        input_custo,
        input_venda,
        switch_produto_em_promo,
        input_preco_promocao,
        dropdown_imagem_arquivo,
        ft.ElevatedButton("Salvar Produto", on_click=salvar_ou_atualizar_produto, bgcolor="#6F42C1", color="white"),
        
        # ─── ADICIONE ESTAS DUAS LINHAS ABAIXO DO BOTÃO SALVAR ───
        ft.Divider(height=20, color="grey300"), # Uma linha fina para separar o cadastro da lista
        grid_produtos # 🎯 AQUI ESTÁ O MOTOR QUE TRAZ A LISTA DE VOLTA!
        
    ], 
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    scroll=ft.ScrollMode.AUTO,  # 👈 ADICIONE ISSO PARA ATIVAR O SCROLL DO MOUSE!
    expand=True                 # 👈 ADICIONE ISSO PARA SE ADAPTAR AO MONITOR DELA!
    )

    tela_categorias = ft.Column([
        ft.Text("Gerenciar Categorias", size=18, weight="bold", color="#6F42C1"),
        ft.Row([input_nova_categoria, ft.ElevatedButton("Adicionar", bgcolor="#A076F9", color="white", on_click=adicionar_categoria)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(), listview_categorias
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ABA DO CARDÁPIO DIGITAL TOTALMENTE VISUAL COM FOTOS
    # --- LAYOUT DA ABA CARDÁPIO ATUALIZADO COM FILTROS ---
    tela_cardapio = ft.Row([
        # Coluna da Esquerda: Formulário de Envio (Totalmente Corrigido e Alinhado)
        # Coluna da Esquerda: Formulário de Envio
        ft.Column([
            ft.Text("🚀 DISPARADOR DE CARDÁPIO", size=16, weight="bold", color="#6F42C1"),
            dropdown_clientes_cardapio,  # 🎯 IMPORTANTE: É aqui que o novo dropdown é desenhado na tela!
            input_tel_cliente,           # O telefone vai pular aqui dentro sozinho
            input_msg_promo,
            input_link_foto,
            ft.ElevatedButton(
                "Enviar Cardápio por WhatsApp 🚀",
                bgcolor="#A076F9",
                color="white",
                icon=ft.Icons.SEND,
                on_click=disparar_cardapio
            )
        ], alignment=ft.MainAxisAlignment.START, spacing=15),
        # Coluna da Direita: Visualizador Móvel Inteligente
        ft.Column([
            ft.Text("📱 PREVIEW DISPOSITIVO MÓVEL", size=14, weight="bold", color="grey700"),
            
            # 🎯 BARRA DE FILTROS DO APP (Alinhados horizontalmente)
            ft.Row([
                dropdown_filtro_categoria_cardapio,
                switch_apenas_promocao
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            
            # Corpo do Celular Lilás
            ft.Container(
                content=container_celular_feed,
                width=360, height=640,
                bgcolor="#F3E5F5",
                border_radius=30,
                padding=20,
                border=ft.Border.all(5, "#6F42C1"),
                shadow=ft.BoxShadow(blur_radius=15, color="#E0E0E0")
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, expand=True)

    tela_vendas_relatorio = ft.Column([
        ft.Text("Faturamento & Lançamento de Vendas", size=18, weight="bold", color="#6F42C1"),
        ft.Column([
            dropdown_venda_cliente,  # O novo dropdown de clientes que criamos
            ft.Row([dropdown_venda_produto, input_venda_qtd], alignment="center", spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        ft.Container(height=5),
        ft.ElevatedButton("Registrar Nova Venda", bgcolor="#A076F9", color="white", width=400, on_click=realizar_venda),
        ft.Divider(),
        ft.Row([
            ft.Container(content=ft.Column([ft.Text("Faturamento Total", size=12), card_faturamento], horizontal_alignment="center"), bgcolor="#E8F5E9", padding=15, border_radius=10, width=240),
            ft.Container(content=ft.Column([ft.Text("Custo Operacional", size=12), card_custo_total], horizontal_alignment="center"), bgcolor="#FFEBEE", padding=15, border_radius=10, width=240),
            ft.Container(content=ft.Column([ft.Text("Lucro Líquido Real", size=12), card_lucro_real], horizontal_alignment="center"), bgcolor="#E3F2FD", padding=15, border_radius=10, width=240),
        ], alignment="center"),
        ft.Container(content=ft.Column([ft.Text("⏱️ Últimas Vendas", weight="bold"), grid_historico_vendas]), padding=10, width=740)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ALWAYS)
    
    # 🎯 RECONSTRUÍDA AQUI: A Tela de cadastros de Usuários e Clientes que estava faltando!
    tela_seguranca_usuarios = ft.Row([
        # --- Primeiro Bloco: Mudar Senha (pode continuar igual) ---
        ft.Container(content=ft.Column([ft.Text("🔐 MUDAR SENHA", weight="bold"), input_senha_atual_me, input_nova_senha_me, txt_status_me, ft.ElevatedButton("Atualizar Senha", bgcolor="#A076F9", color="white", on_click=alterar_minha_senha)], horizontal_alignment="center"), padding=20, border=ft.Border.all(1, "#E3F2FD"), border_radius=10, width=390),
        
        # --- Segundo Bloco: Cadastro e Lista (Aqui adicionamos o Scroll!) ---
        ft.Container(content=ft.Column([
            ft.Text("👥 NOVO CADASTRO (OPERADOR / CLIENTE)", weight="bold"), 
            input_novo_user, 
            dropdown_tipo_contato,  
            input_tel_cliente,
            input_cep_cliente,
            input_endereco_cliente,
            input_bairro_cliente,
            input_estado_cliente,
            input_nova_senha, 
            dropdown_perfil_user, 
            txt_status_usuarios,    
            ft.ElevatedButton("Salvar", bgcolor="#6F42C1", color="white", on_click=executar_cadastro_usuario), 
            ft.Divider(), 
            listview_operadores
        ], 
        horizontal_alignment="center", 
        spacing=8,
        scroll=ft.ScrollMode.AUTO,  # 👈 1. ATIVA O SCROLL DE MOUSE AQUI!
        expand=True                 # 👈 2. DIZ PARA A COLUNA SE AJUSTAR À ALTURA MÁXIMA
        ), padding=20, border=ft.Border.all(1, "#E3F2FD"), border_radius=10, width=390, height=520) if pode_excluir else ft.Container(ft.Text("Restrito ao Admin"))
        
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, width=780)

    # --- LAYOUT DA ABA CRM & FIDELIZAÇÃO ---
    tela_crm = ft.Column([
        ft.Text("🎯 GESTÃO DE RELACIONAMENTO (CRM) 🎯", size=18, weight="bold", color="#6F42C1"),
        ft.Text("Monitore clientes sumidos e reative o contato pelo WhatsApp", size=12, color="grey600"),
        ft.Container(height=10),
        dropdown_filtro_dias,
        input_mensagem_crm,
        ft.Divider(),
        ft.Text("👥 CLIENTES DETECTADOS NO FILTRO:", size=14, weight="bold"),
        grid_clientes_sumidos
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ALWAYS)

    # --- INTERFACE MASTER ---
    header_sistema = ft.Container(
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT, colors=["#D8B4F8", "#A076F9", "#6F42C1"]),
        content=ft.Row([
            ft.Column([ft.Text("Angelicia", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), ft.Text(f"Operador: {usuario_logado.upper()} ({perfil_logado.upper()})", size=12, color=ft.Colors.WHITE70)], expand=True),
            ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, on_click=realizar_logoff)
        ]), padding=20, border_radius=10, width=780
    )
    
    conteudo_atual = ft.Container(content=tela_produtos, expand=True, width=780)

    def deletar_usuario_ou_contato(e):
        # 1. Identifica o ID recebido
        if isinstance(e, int) or isinstance(e, str):
            item_id = e
        elif hasattr(e, "control") and e.control.data:
            item_id = e.control.data
        else:
            return

        try:
            # 2. Deleta do banco de dados
            deletar_usuario_banco(item_id) 
            
            txt_status_usuarios.value = "🗑️ Registro deletado com sucesso!"
            txt_status_usuarios.color = "green_700"
            
            # 3. 🎯 REMOÇÃO FORÇADA NA TELA (Garante o sumiço na hora!)
            # Vamos reconstruir a lista visual excluindo o container que tem esse ID
            try:
                novos_controles = []
                for container in listview_operadores.controls:
                    # Se o container tiver o ID que acabou de ser deletado, a gente pula ele (remove)
                    if hasattr(container, "data") and container.data == item_id:
                        continue
                    novos_controles.append(container)
                
                # Aplica a nova lista limpa no visual
                listview_operadores.controls = novos_controles
                listview_operadores.update()
            except Exception as e_visual:
                print(f"Erro na remoção visual direta: {e_visual}")
            
            # 4. Manda a lista oficial se reconstruir do banco por garantia
            try:
                recarregar_lista_usuarios()
            except: pass
            
            # 5. Atualiza os dropdowns das outras abas
            try:
                recarregar_dropdown_clientes_venda()
            except: pass
            
        except Exception as erro:
            txt_status_usuarios.value = f"❌ Erro ao deletar: {erro}"
            txt_status_usuarios.color = "red_700"
            
        page.update()

    # ─────────────────────────────────────────────────────────────────
    # SISTEMA DE NAVEGAÇÃO COMPLETO COM CRM INTEGRADO
    # ─────────────────────────────────────────────────────────────────
    def navegar(tela, btn_ativo):
        for btn in botoes_menu: btn.style = ft.ButtonStyle(bgcolor="#D8B4F8", color="#6F42C1")
        btn_ativo.style = ft.ButtonStyle(bgcolor="#6F42C1", color="white")
        conteudo_atual.content = tela
        page.update()

    btn_aba_prod = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.CAKE, size=14), ft.Text("Produtos")]), width=145, height=45, on_click=lambda e: navegar(tela_produtos, btn_aba_prod), style=ft.ButtonStyle(bgcolor="#6F42C1", color="white"))
    btn_aba_cat = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.CATEGORY, size=14), ft.Text("Categorias")]), width=145, height=45, on_click=lambda e: navegar(tela_categorias, btn_aba_cat))
    btn_aba_card = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.SHARE, size=14), ft.Text("Cardápio")]), width=145, height=45, on_click=lambda e: navegar(tela_cardapio, btn_aba_card))
    btn_aba_venda = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.MONETIZATION_ON, size=14), ft.Text("Vendas")]), width=145, height=45, on_click=lambda e: navegar(tela_vendas_relatorio, btn_aba_venda))
    
    # 🎯 NOVO BOTÃO DA ABA CRM (Estilizado seguindo o seu padrão)
    btn_aba_crm = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.MARK_CHAT_READ_ROUNDED, size=14), ft.Text("Fidelização")]), width=145, height=45, on_click=lambda e: navegar(tela_crm, btn_aba_crm))
    
    btn_aba_seguranca = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.LOCK, size=14), ft.Text("Usuários")]), width=145, height=45, on_click=lambda e: navegar(tela_seguranca_usuarios, btn_aba_seguranca))

    # Montagem da lista de botões na barra superior
    botoes_menu = [btn_aba_prod]
    if pode_excluir: botoes_menu.append(btn_aba_cat)
    
    # Encaixando o novo botão de Fidelização na barra de abas
    botoes_menu.extend([btn_aba_card, btn_aba_venda, btn_aba_crm, btn_aba_seguranca])

    # Aumentei um pouco a largura máxima para acomodar o novo botão confortavelmente
    barra_navegacao = ft.Row(botoes_menu, alignment=ft.MainAxisAlignment.CENTER, width=820)

    page.clean()
    page.add(ft.Column([header_sistema, ft.Container(height=5), barra_navegacao, ft.Container(height=10), conteudo_atual], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True))
    # ─────────────────────────────────────────────────────────────────

    recarregar_categorias()
    recarregar_lista_produtos()
    recarregar_relatorios()
    recarregar_lista_usuarios()

#    🎯 ADICIONE ESSA LINHA BEM AQUI:
    recarregar_dropdown_produtos_venda()

    listar_fotos_da_pasta_assets() # <-- ADICIONE ESSA LINHA EXATAMENTE AQUI!
    #recarregar_crm()
    recarregar_dropdown_clientes_venda() # 🎯 ADICIONE ESSA LINHA AQUI!
    page.update()