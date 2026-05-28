# 🧁 Sistema Confeitaria Angelicia (v2.0)

Um sistema comercial completo e responsivo desenvolvido sob medida para gerenciamento de vendas, cardápio e relacionamento com clientes (CRM) da Confeitaria Angelicia.

## 🚀 Funcionalidades Principais

* **🧁 Gestão de Cardápio:** Cadastro de produtos com cálculo de custo de produção, preço de venda, ingredientes e gerenciamento de promoções dinâmicas.
* **👥 CRM & Controle de Entregas:** Aba dedicada ao cadastro de clientes e operadores, incluindo campos de **CEP, Endereço, Bairro e Estado** para facilitar a logística de entrega das tortas.
* **✏️ Visualização e Edição Rápida:** Painel em formato de lista com pop-ups integrados para consulta rápida de dados residenciais ou atualização cadastral em tempo real.
* **🖥️ Layout Responsivo:** Interface blindada e adaptada para resoluções menores (como notebooks de $1366 \times 768$), utilizando barras de rolagem inteligentes (`ScrollMode.AUTO`) para evitar cortes na tela.
* **💾 Banco de Dados Confiável:** Estrutura em SQLite utilizando travas de segurança (`try/except`) para evitar travamentos ou corrupção de dados visuais.

## 🛠️ Tecnologias Utilizadas

* **Python 3** (Linguagem base)
* **Flet** (Framework para a interface visual moderna e responsiva)
* **SQLite** (Banco de dados local leve e seguro)
* **PyInstaller** (Para compilação e geração do arquivo executável `.exe`)

## 📅 Próximos Passos (Versão 3.0 📈)
* [ ] Separação total da tabela de clientes e operadores no banco de dados.
* [ ] Módulo de exportação de relatórios de fechamento mensal de vendas direto para o **Excel** (`.xlsx`).
* [ ] Calculadora automática de Ficha Técnica (custo de ingredientes por peso/unidade e sugestão de preço com margem de lucro).

---
*Desenvolvido com orgulho por Leonardo de Paula ✨*