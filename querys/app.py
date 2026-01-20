# app.py - Página principal com navegação LIMPA

import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import io
from io import BytesIO

# ============ CONFIGURAÇÃO ============
st.set_page_config(
    page_title="MySQL System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CONEXÃO MYSQL CENTRALIZADA ============
def conectar_mysql():
    """Função para conectar ao MySQL"""
    try:
        # ALTERE ESTES VALORES PARA SUAS CREDENCIAIS
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", 
            database="" 
        )
        return conexao
    except Error as e:
        st.error(f"Erro ao conectar: {e}")
        return None

def get_conexao():
    """Obtém ou cria conexão com MySQL"""
    # Se não existe conexão ou está fechada, cria nova
    if "conexao_mysql" not in st.session_state:
        with st.spinner("Conectando ao MySQL..."):
            st.session_state.conexao_mysql = conectar_mysql()
    
    # Verifica se a conexão existe e está ativa
    if st.session_state.conexao_mysql:
        try:
            if st.session_state.conexao_mysql.is_connected():
                return st.session_state.conexao_mysql
            else:
                # Reconectar se perdeu conexão
                st.session_state.conexao_mysql = conectar_mysql()
                return st.session_state.conexao_mysql
        except:
            # Se houver erro, tenta reconectar
            st.session_state.conexao_mysql = conectar_mysql()
            return st.session_state.conexao_mysql
    
    return None

# ============ ESTADO DA APLICAÇÃO ============
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

# ============ BARRA LATERAL DE NAVEGAÇÃO LIMPA ============
with st.sidebar:
    # Logo e título limpo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="margin-bottom: 5px;">🗄️</h1>
        <h3 style="margin-top: 0;">MySQL Manager</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Status da conexão compacto
    conexao = get_conexao()
    status_color = "🟢" if conexao and conexao.is_connected() else "🔴"
    status_text = "Conectado" if conexao and conexao.is_connected() else "Desconectado"
    
    st.markdown(f"### {status_color} **{status_text}**")
    
    if conexao and conexao.is_connected():
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT DATABASE()")
            banco = cursor.fetchone()[0] or "Nenhum"
            cursor.close()
            st.caption(f"📁 Banco: **{banco}**")
        except:
            pass
    
    st.markdown("---")
    
    # Menu limpo e organizado
    st.markdown("### 📂 **Menu Principal**")
    
    # Grupos de menu
    st.markdown("**🎓 Aprendizado**")
    
    # Botões do grupo Aprendizado
    if st.button("🏠 Página Inicial", use_container_width=True, 
                type="primary" if st.session_state.pagina == "home" else "secondary"):
        st.session_state.pagina = "home"
        st.rerun()
    
    if st.button("📚 Guia MySQL", use_container_width=True,
                type="primary" if st.session_state.pagina == "manual" else "secondary"):
        st.session_state.pagina = "manual"
        st.rerun()
    
    if st.button("🎯 Exercícios", use_container_width=True,
                type="primary" if st.session_state.pagina == "exercicios" else "secondary"):
        st.session_state.pagina = "exercicios"
        st.rerun()
    
    st.markdown("---")
    st.markdown("**🔧 Ferramentas**")
    
    # Botões do grupo Ferramentas
    if st.button("🔍 Editor SQL", use_container_width=True,
                type="primary" if st.session_state.pagina == "query_editor" else "secondary"):
        st.session_state.pagina = "query_editor"
        st.rerun()
    
    if st.button("📝 Formulários", use_container_width=True,
                type="primary" if st.session_state.pagina == "Formularios" else "secondary"):
        st.session_state.pagina = "Formularios"
        st.rerun()
    
    if st.button("🤖 Query Builder", use_container_width=True,
                type="primary" if st.session_state.pagina == "sql_builder" else "secondary"):
        st.session_state.pagina = "sql_builder"
        st.rerun()
    
    if st.button("✨ Criar Consultas", use_container_width=True,
                type="primary" if st.session_state.pagina == "criar_consultas" else "secondary"):
        st.session_state.pagina = "criar_consultas"
        st.rerun()
    
    st.markdown("---")
    
    # Conexão simplificada
    st.markdown("**🔌 Conexão**")
    col_con1, col_con2 = st.columns(2)
    
    with col_con1:
        if st.button("Conectar", use_container_width=True,
                    type="primary" if not conexao else "secondary"):
            st.session_state.conexao_mysql = conectar_mysql()
            st.rerun()
    
    with col_con2:
        if st.button("Desconectar", use_container_width=True, 
                    disabled=not (conexao and conexao.is_connected())):
            if "conexao_mysql" in st.session_state and st.session_state.conexao_mysql:
                st.session_state.conexao_mysql.close()
                st.session_state.conexao_mysql = None
            st.rerun()
    
    # Botão para ver bancos (apenas se conectado)
    if conexao and conexao.is_connected():
        if st.button("📊 Listar Bancos", use_container_width=True):
            cursor = conexao.cursor()
            cursor.execute("SHOW DATABASES")
            bancos = [b[0] for b in cursor.fetchall() if b[0] not in 
                     ['information_schema', 'mysql', 'performance_schema', 'sys']]
            cursor.close()
            
            st.info(f"**{len(bancos)} bancos disponíveis:**")
            for banco in bancos:
                st.write(f"• {banco}")
    
    st.markdown("---")
    
    # Informações rápidas
    st.caption(f"Página: **{st.session_state.pagina.replace('_', ' ').title()}**")
    st.caption("Versão 2.0 • Desenvolvido com Streamlit")

# ============ PÁGINA: HOME ============
def pagina_home():
    st.title("🏠 Sistema Querys MySQL ")
    st.header(" 🕵️ - Sistema de criação de Querys em Mysql -")
    st.subheader("Mysql Manager - QUERYS")
    
    # Banner
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    ">
        <h2 style="color: white;">Tudo para dominar MySQL</h2>
        <p>Teoria • Prática • Projetos Reais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📚 Guia Completo")
            st.write("Aprenda do zero ao avançado")
            if st.button("Estudar", key="btn_guia_home"):
                st.session_state.pagina = "manual"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🎯 Exercícios")
            st.write("Pratique com desafios")
            if st.button("Praticar", key="btn_exercicios_home"):
                st.session_state.pagina = "exercicios"
                st.rerun()
    
    with col3:
        with st.container(border=True):
            st.markdown("### 🔍 Query Editor Pro")
            st.write("Ambiente real para quem domina o SQL")
            if st.button("Usar Editor", key="btn_editor_home"):
                st.session_state.pagina = "query_editor"
                st.rerun()
    
    # Segunda linha de cards
    col4, col5, col6 = st.columns(3)
    
    with col4:
        with st.container(border=True):
            st.markdown("### 📝 Formulários")
            st.write("Inserir dados no MySQL")
            
            # Verificar conexão
            conexao = get_conexao()
            if conexao and conexao.is_connected():
                if st.button("Acessar", key="btn_form_home", type="primary"):
                    st.session_state.pagina = "Formularios"
                    st.rerun()
            else:
                if st.button("Conectar e Acessar", key="btn_con_form_home"):
                    st.session_state.conexao_mysql = conectar_mysql()
                    if st.session_state.conexao_mysql:
                        st.session_state.pagina = "Formularios"
                    st.rerun()
    
    with col5:
        with st.container(border=True):
            st.markdown("### 🤖 Assistente de Querys para SQL")
            st.write("Consultas em linguagem natural")
            if st.button("Experimentar", key="btn_nlp_home"):
                st.session_state.pagina = "sql_builder"
                st.rerun()
    
    with col6:
        with st.container(border=True):
            st.markdown("### ⚙️ Conexão ")
            st.write("🔌 Conexão do sistema")
            if st.button("Conexão MySQL", key="btn_config_home"):
                # Mostrar informações de conexão
                conexao = get_conexao()
                if conexao:
                    st.info(f"Conectado a: {conexao.database}")
                    cursor = conexao.cursor()
                    cursor.execute("SHOW DATABASES")
                    bancos = cursor.fetchall()
                    st.write(f"Bancos disponíveis: {len(bancos)}")
                    cursor.close()
                else:
                    st.warning("Não conectado")
    
    # Explicação do sistema
    with st.expander("ℹ️ Como usar este sistema", expanded=True):
        st.markdown("""
        ### Estrutura do Sistema:
        
        1. **Página Inicial** (esta) - Visão geral do sistema
        2. **Guia MySQL** (`manual.py`) - Material de estudo completo
        3. **Exercícios** (`exercicios.py`) - Prática com desafios
        4. **Query Editor pro** (`query_editor.py`) - Ambiente de execução SQL
        5. **Formulários** (`Formularios.py`) - Inserir dados no MySQL
        6. **Query Builder** (`sql_builder.py`) - Consultas em linguagem natural
        7. **Criar Consultas** (`criar_consultas.py`) - Construtor visual de SQL
        
        ### 🔌 Conexão MySQL:
        - Conecte-se usando o botão na sidebar
        - Status visível em todas as páginas
        - Conexão compartilhada entre todas as páginas
        
        ### 📁 Arquivos do projeto:
        ```
        seu_projeto/
        ├── app.py              ← Este arquivo (navegação principal)
        ├── manual.py           ← Guia de estudo MySQL
        ├── exercicios.py       ← Exercícios práticos
        ├── query_editor.py     ← Editor SQL completo
        ├── Formularios.py      ← Inserir dados no MySQL
        ├── sql_builder.py      ← Query Builder
        ├── criar_consultas.py  ← Construtor visual de SQL
        └── requirements.txt    ← Dependências
        ```
        """)

# ============ ROTEADOR PRINCIPAL ============
def main():
    pagina = st.session_state.pagina
    
    # Verificar qual página mostrar
    if pagina == "home":
        pagina_home()
    
    elif pagina == "manual":
        # Importar e executar a página manual.py
        try:
            import manual
            manual.pagina_guia()
        except Exception as e:
            st.error(f"Erro ao carregar a página manual: {e}")
            st.info("Crie o arquivo `manual.py` com a função `pagina_guia()`")
            if st.button("Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
    
    elif pagina == "exercicios":
        # Importar e executar a página exercicios.py
        try:
            import exercicios
            exercicios.pagina_exercicios()
        except Exception as e:
            st.error(f"Erro ao carregar a página exercicios: {e}")
            st.info("Crie o arquivo `exercicios.py` com a função `pagina_exercicios()`")
            if st.button("Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
    
    elif pagina == "query_editor":
        # Importar e executar a página query_editor.py
        try:
            import query_editor
            query_editor.pagina_query_editor()
        except Exception as e:
            st.error(f"Erro ao carregar a página query_editor: {e}")
            st.info("Crie o arquivo `query_editor.py` com a função `pagina_query_editor()`")
            
            if st.button("🏠  Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
    
    elif pagina == "Formularios":
        st.title("🌐 Teste de conexão :")
        st.subheader("📡Garantindo ligação ao(s) Banco(s) :")
        
        # DEBUG: Mostrar status da conexão
        st.write("DEBUG - Status da conexão:")
        if "conexao_mysql" in st.session_state:
            st.write(f"- Existe no session_state: SIM")
            if st.session_state.conexao_mysql:
                try:
                    status = "ATIVA" if st.session_state.conexao_mysql.is_connected() else "INATIVA"
                    st.write(f"- Conexão: {status}")
                    st.write(f"- Banco: {st.session_state.conexao_mysql.database}")
                except:
                    st.write("- Conexão: ERRO")
            else:
                st.write("- Conexão: None")
        else:
            st.write("- Existe no session_state: NÃO")
        
        try:
            import Formularios
            Formularios.pagina_formularios()
            
        except Exception as e:
            st.error(f"Erro ao carregar formulários: {e}")
            
            if st.button("🏠 Voltar para Home"):
                    st.session_state.pagina = "home"               
                    st.rerun()
            
    
    elif pagina == "sql_builder":
        try:
            import sql_builder
            sql_builder.pagina_sql_builder()
        except Exception as e:
            st.error(f"Módulo não encontrado: {e}")
            if st.button("🏠 Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
                
    elif pagina == "criar_consultas":
        try:
            import criar_consultas
            criar_consultas.interface_consulta_visual()
        except Exception as e:
            st.error(f"Módulo não encontrado: {e}")
            if st.button("🏠 Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()            
    
    # Rodapé
    st.markdown("---")
    
    # Status da conexão no rodapé
    conexao = get_conexao()
    if conexao and conexao.is_connected():
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT DATABASE()")
            banco_atual = cursor.fetchone()[0]
            cursor.close()
            
            st.caption(f"✨ Sistema MySQL | Banco: {banco_atual} | Desenvolvido com Streamlit")
        except:
            st.caption("✨ Sistema MySQL | ✅ Conectado | Desenvolvido com Streamlit")
    else:
        st.caption("✨ Sistema MySQL | 🔌 Não conectado | Desenvolvido com Streamlit")

if __name__ == "__main__":
    main()