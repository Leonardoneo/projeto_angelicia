# #main.py
# import flet as ft
# from database.connection import inicializar_banco
# from views.login_view import abrir_tela_login
# from views.cadastro_view import abrir_tela_cadastro

# def main(page: ft.Page):
#     inicializar_banco()
    
#     def login_com_sucesso(perfil, username):
#         abrir_tela_cadastro(page, perfil, username)

#     abrir_tela_login(page, login_com_sucesso)

# if __name__ == "__main__":
#     # CORREÇÃO CRÍTICA: Mapeia a pasta 'assets' para o Flet conseguir ler as imagens das tortas
#     ft.app(target=main, assets_dir="assets")


# main.py
import flet as ft
# 🔗 IMPORTANTE: Adicionamos o 'conectar' aqui no topo!
from database.connection import inicializar_banco, conectar 
from views.login_view import abrir_tela_login
from views.cadastro_view import abrir_tela_cadastro

def main(page: ft.Page):
    inicializar_banco()
    
    # # 💥 ROLO COMPRESSOR: Apaga todos os registros de teste para começar do zero
    # try:
    #     conn = conectar()
    #     cursor = conn.cursor()
        
    #     # 1. Limpa todos os contatos (clientes/operadores que aparecem na lista)
    #     cursor.execute("DELETE FROM contatos")
        
    #     # 2. Limpa todos os usuários (logins antigos, se houver)
    #     cursor.execute("DELETE FROM usuarios")
        
    #     conn.commit()
    #     conn.close()
    #     print("🧼 BANCO TOTALMENTE ZERADO COM SUCESSO!")
    # except Exception as e:
    #     print(f"Erro ao zerar o banco: {e}")
    
# # 💥 ROLO COMPRESSOR ATUALIZADO: Força a atualização do banco de dados
#     try:
#         conn = conectar()
#         cursor = conn.cursor()
        
#         # 🎯 ADICIONE ESTA LINHA AQUI: Ela apaga a tabela velha para a nova ser criada com CEP e Endereço!
#         cursor.execute("DROP TABLE IF EXISTS contatos")
        
#         # Mantém as outras limpezas de segurança
#         cursor.execute("DELETE FROM usuarios")
        
#         conn.commit()
#         conn.close()
#         print("🧼 BANCO DE DADOS ATUALIZADO E ZERADO COM SUCESSO!")
#     except Exception as e:
#         print(f"Erro ao zerar o banco: {e}")

    def login_com_sucesso(perfil, username):
        abrir_tela_cadastro(page, perfil, username)

    abrir_tela_login(page, login_com_sucesso)

# 🚀 O bloco de inicialização fica SEMPRE no final do arquivo!
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")