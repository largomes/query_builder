# Formularios.py - VERSÃO ORGANIZADA
import streamlit as st
import pandas as pd
from datetime import datetime

# ============ FUNÇÕES AUXILIARES DE CONEXÃO ============
def listar_todos_bancos():
    """Lista TODOS os bancos disponíveis no MySQL (sem filtros de sistema)"""
    try:
        # Cria conexão temporária sem banco específico
        import mysql.connector
        from mysql.connector import Error
        
        conexao_temp = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        
        cursor = conexao_temp.cursor()
        cursor.execute("SHOW DATABASES")
        todos_bancos = [db[0] for db in cursor.fetchall()]
        cursor.close()
        conexao_temp.close()
        
        # Filtra bancos de sistema (opcional, mas recomendado)
        bancos_filtrados = [b for b in todos_bancos if b not in [
            'information_schema', 'mysql', 'performance_schema', 'sys'
        ]]
        
        return bancos_filtrados
        
    except Exception as e:
        st.error(f"❌ Erro ao listar bancos: {e}")
        return []
                  

def pagina_formularios():
    """Página de formulários"""
    
    st.title("📋 Formulários")
    
    # ========== SEÇÃO 1: STATUS DA CONEXÃO ==========
    st.markdown("### 🔌 Status da Conexão")
    
    # Verificar se já está conectado via app.py
    conexao = None
    banco_atual_conexao = None
    mensagem_status = ""
    
    if "conexao_mysql" in st.session_state and st.session_state.conexao_mysql:
        try:
            conexao = st.session_state.conexao_mysql
            if conexao.is_connected():
                # Mostrar banco atual
                cursor = conexao.cursor()
                cursor.execute("SELECT DATABASE()")
                banco_atual_conexao = cursor.fetchone()[0]
                cursor.close()
                
                if banco_atual_conexao:
                    mensagem_status = f"✅ Conectado ao banco: **{banco_atual_conexao}**"
                    st.success(mensagem_status)
                else:
                    mensagem_status = "⚠️ Conectado mas sem banco selecionado"
                    st.warning(mensagem_status)
            else:
                mensagem_status = "❌ Conexão perdida"
                st.error(mensagem_status)
                conexao = None
        except Exception as e:
            mensagem_status = f"❌ Erro na conexão: {str(e)[:50]}..."
            st.error(mensagem_status)
            conexao = None
    else:
        mensagem_status = "⚠️ Não conectado via Pagina Inicial"
        st.warning(mensagem_status)
    
    # ========== SEÇÃO 2: SELEÇÃO DO BANCO ==========
    st.markdown("### 📁 Banco de Dados")
    
    # Listar TODOS os bancos disponíveis
    bancos_disponiveis = listar_todos_bancos()
    
    if not bancos_disponiveis:
        st.error("❌ Nenhum banco de dados disponível!")
        st.info("""
        1. Certifique-se que o MySQL está rodando
        2. Crie um banco de dados
        3. Ou conecte-se primeiro na página inicial do app.py
        """)
               
        # Opção para criar banco de teste mesmo sem conexão
        if st.button("📁 Criar Banco de Teste"):
            if criar_banco_teste_direto():
                st.rerun()
        return
    
    # Determinar banco selecionado inicial
    index_inicial = 0
    
    # Se tem banco atual da conexão e ele está na lista
    if banco_atual_conexao and banco_atual_conexao in bancos_disponiveis:
        index_inicial = bancos_disponiveis.index(banco_atual_conexao)
    # Se tem banco atual mas não está na lista
    elif banco_atual_conexao and banco_atual_conexao not in bancos_disponiveis:
        bancos_disponiveis.insert(0, banco_atual_conexao)
        index_inicial = 0
    
    banco_selecionado = st.selectbox(
        "Escolha o banco para trabalhar:",
        bancos_disponiveis,
        index=index_inicial,
        key="select_banco_form"
    )
    
    # Se o usuário selecionou banco diferente do banco atual da conexão
    if banco_atual_conexao and banco_selecionado != banco_atual_conexao:
        st.info(f"ℹ️ Você selecionou **{banco_selecionado}**, mas a conexão do app.py está no **{banco_atual_conexao}**.")
    
    # Botões para gerenciar banco
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("✅ Usar Este Banco", type="primary", use_container_width=True):
            # Se não tem conexão ou conexão está ruim, cria nova
            if not conexao or not conexao.is_connected():
                try:
                    import mysql.connector
                    conexao = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database=banco_selecionado
                    )
                    st.session_state.conexao_mysql = conexao
                except Exception as e:
                    st.error(f"❌ Erro ao conectar: {e}")
                    return
            else:
                # Usa conexão existente, muda de banco
                try:
                    cursor = conexao.cursor()
                    cursor.execute(f"USE {banco_selecionado}")
                    cursor.close()
                    conexao.database = banco_selecionado
                except Exception as e:
                    st.error(f"❌ Erro ao mudar de banco: {e}")
                    return
            
            st.success(f"✅ Banco selecionado: **{banco_selecionado}**")
            st.rerun()
    
    with col_btn2:
        if st.button("➕ Criar Novo Banco", use_container_width=True):
            with st.form("novo_banco_form"):
                nome_novo_banco = st.text_input("Nome do novo banco:")
                if st.form_submit_button("Criar Banco"):
                    if nome_novo_banco:
                        if criar_novo_banco(nome_novo_banco):
                            st.rerun()
    
    # Se não temos uma conexão válida ainda, pedir para selecionar banco primeiro
    if not conexao or not conexao.is_connected():
        st.warning("⏳ Selecione um banco e clique em 'Usar Este Banco' para continuar.")
        st.markdown("---")
        if st.button("🏠 Voltar para Página Inicial", use_container_width=True):
            st.session_state.pagina = "home"
            st.rerun()
        return
    
    # Verificar se o banco selecionado está realmente sendo usado
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT DATABASE()")
        banco_em_uso = cursor.fetchone()[0]
        cursor.close()
        
        if banco_em_uso != banco_selecionado:
            st.warning(f"⚠️ A conexão ainda está no banco **{banco_em_uso}**. Clique em 'Usar Este Banco'.")
            st.markdown("---")
            if st.button("🏠 Voltar para Página Inicial", use_container_width=True, key="btn_voltar_2"):
                st.session_state.pagina = "home"
                st.rerun()
            return
    except:
        st.error("❌ Não foi possível verificar o banco em uso, Clique novamente em 'Voltar' para sair.")
        return
    
    # ========== INTERFACE PRINCIPAL ==========
    st.markdown("---")
    st.title("📝 Formulários MySQL")
    
    # Mostrar status atualizado
    try:
        if conexao.is_connected():
            st.success(f"✅ Conectado ao banco: **{conexao.database}**")
        else:
            st.warning("⚠️ Conexão MySQL não está ativa")
            if st.button("🔄 Atualizar Conexão"):
                st.rerun()
            return
    except Exception as e:
        st.error(f"❌ Erro na conexão: {e}")
        return
    
    # ========== OBTER TABELAS DO BANCO ==========
    try:
        cursor = conexao.cursor()
        cursor.execute("SHOW TABLES")
        tabelas = [tabela[0] for tabela in cursor.fetchall()]
        cursor.close()
        
        if not tabelas:
            st.warning("Nenhuma tabela encontrada neste banco!")
            st.markdown("---")
            if st.button("🏠 Voltar para Página Inicial", use_container_width=True, key="btn_voltar_3"):
                st.session_state.pagina = "home"
                st.rerun()
            return
        
    except Exception as e:
        st.error(f"❌ Erro ao obter tabelas: {e}")
        return
    
    # ========== SELECIONAR TABELA ==========
    col_esq, col_dir = st.columns([1, 3])
    
    with col_esq:
        st.subheader("📊 Tabelas")
        tabela_selecionada = st.selectbox(
            "Selecione uma tabela:",
            tabelas,
            key="select_tabela_form"
        )
        
        # Botão para ver dados existentes
        if st.button("👁️ Ver Dados Existentes", use_container_width=True, key="btn_ver_dados"):
            st.session_state.ver_dados = True
            st.rerun()
    
    # ========== SEÇÃO DE VISUALIZAÇÃO DE DADOS ==========
    if st.session_state.get('ver_dados', False):
        st.markdown("---")
        st.subheader(f"📊 Visualização: `{tabela_selecionada}`")
        
        try:
            cursor = conexao.cursor()
            cursor.execute(f"SELECT * FROM {tabela_selecionada} LIMIT 20")
            dados = cursor.fetchall()
            
            if dados:
                colunas = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(dados, columns=colunas)
                
                # Container dedicado
                with st.container():
                    # Opções de visualização
                    col_view1, col_view2 = st.columns(2)
                    with col_view1:
                        altura = st.slider("Altura da tabela", 200, 800, 400, key="altura_tabela")
                    with col_view2:
                        num_registros = st.slider("Nº de registros", 5, 100, 20, key="num_registros")
                    
                    # Dataframe com altura ajustável
                    st.dataframe(
                        df.head(num_registros), 
                        use_container_width=True,
                        height=altura
                    )
                    
                    # Informações
                    st.info(f"**{len(df)}** registros totais | **{len(df.columns)}** colunas")
                    
                    # Botão para exportar
                    if st.button("📥 Exportar para CSV", key="btn_exportar"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="💾 Baixar CSV",
                            data=csv,
                            file_name=f"{tabela_selecionada}.csv",
                            mime="text/csv",
                            key="btn_download_csv"
                        )
                    
            else:
                st.info("📭 Tabela vazia - Nenhum registro encontrado")
            
            cursor.close()
            
            # Botão para fechar visualização
            if st.button("❌ Fechar Visualização", key="btn_fechar_visualizacao"):
                st.session_state.ver_dados = False
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
            if st.button("🔙 Voltar", key="btn_voltar_erro"):
                st.session_state.ver_dados = False
                st.rerun()
    
    # ========== FORMULÁRIO DE INSERÇÃO (sempre visível) ==========
    else:
        with col_dir:
            if not tabela_selecionada:
                return
            
            # ========== OBTER ESTRUTURA DA TABELA ==========
            try:
                cursor = conexao.cursor()
                cursor.execute(f"DESCRIBE {tabela_selecionada}")
                colunas_info = cursor.fetchall()
                cursor.close()
                
            except Exception as e:
                st.error(f"Erro ao obter estrutura: {e}")
                return
            
            st.subheader(f"📝 Inserir em: `{tabela_selecionada}`")
            
            # ========== CRIAR FORMULÁRIO DINÂMICO ==========
            valores = {}
            
            for coluna in colunas_info:
                nome = coluna[0]
                tipo = coluna[1].lower()
                pode_ser_nulo = coluna[2] == 'YES'
                auto_inc = 'auto_increment' in str(coluna[5]).lower()
                
                # Pular campos auto_increment
                if auto_inc:
                    continue
                
                # Label formatado
                label = f"**{nome}**"
                if not pode_ser_nulo:
                    label += " *"
                
                # Criar widget apropriado baseado no tipo
                if 'int' in tipo or 'decimal' in tipo or 'float' in tipo or 'double' in tipo:
                    # Campo numérico
                    valores[nome] = st.number_input(
                        label, 
                        value=0,
                        key=f"num_{nome}"
                    )
                
                elif 'date' in tipo:
                    # Campo de data
                    valores[nome] = st.date_input(
                        label,
                        key=f"date_{nome}"
                    )
                
                elif 'datetime' in tipo or 'timestamp' in tipo:
                    # Campo de data e hora
                    col1, col2 = st.columns(2)
                    with col1:
                        data = st.date_input(
                            f"{nome} - Data",
                            key=f"dt_date_{nome}"
                        )
                    with col2:
                        hora = st.time_input(
                            f"{nome} - Hora",
                            key=f"dt_time_{nome}"
                        )
                    valores[nome] = datetime.combine(data, hora) if data and hora else None
                
                elif 'time' in tipo:
                    # Campo de hora
                    valores[nome] = st.time_input(
                        label,
                        key=f"time_{nome}"
                    )
                
                elif 'text' in tipo or 'varchar' in tipo or 'char' in tipo:
                    # Campo de texto
                    if 'text' in tipo or 'mediumtext' in tipo or 'longtext' in tipo:
                        # Texto longo
                        valores[nome] = st.text_area(
                            label,
                            height=100,
                            key=f"area_{nome}"
                        )
                    else:
                        # Texto curto
                        valores[nome] = st.text_input(
                            label,
                            key=f"text_{nome}"
                        )
                
                elif 'enum' in tipo or 'set' in tipo:
                    # Campo de seleção (ENUM)
                    # Extrair opções do tipo ENUM('op1','op2')
                    opcoes = tipo.split('(')[1].split(')')[0].replace("'", "").split(',')
                    valores[nome] = st.selectbox(
                        label,
                        options=opcoes,
                        key=f"enum_{nome}"
                    )
                
                else:
                    # Campo genérico para outros tipos
                    valores[nome] = st.text_input(
                        label,
                        key=f"gen_{nome}"
                    )
            
            # ========== BOTÕES DE AÇÃO ==========
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("💾 Inserir Registro", type="primary", use_container_width=True, key="btn_inserir"):
                    inserir_dados(conexao, tabela_selecionada, valores)
            
            with col_btn2:
                if st.button("🔄 Limpar Formulário", use_container_width=True, key="btn_limpar"):
                    st.rerun()
            
            with col_btn3:
                if st.button("📋 Gerar SQL", use_container_width=True, key="btn_gerar_sql"):
                    gerar_sql_insert(tabela_selecionada, valores)
    
    # ========== BOTÃO VOLTAR NO FINAL ==========
    st.markdown("---")
    col_voltar1, col_voltar2, col_voltar3 = st.columns([1, 1, 1])
    
    with col_voltar2:
        if st.button("🏠 Voltar para Página Inicial", use_container_width=True, key="btn_voltar_final"):
            st.session_state.pagina = "home"
            st.rerun()

# ... (as outras funções permanecem EXATAMENTE iguais - inserir_dados, gerar_sql_insert, criar_novo_banco, criar_banco_teste_direto)              

def inserir_dados(conexao, tabela, dados):
    """Insere dados na tabela MySQL"""
    try:
        # Filtrar dados vazios/nulos
        dados_validos = {}
        for chave, valor in dados.items():
            if valor is None:
                continue
            if isinstance(valor, str) and valor.strip() == "":
                continue
            dados_validos[chave] = valor
        
        if not dados_validos:
            st.warning("⚠️ Nenhum dado para inserir!")
            return
        
        # Construir query SQL
        colunas = ", ".join(dados_validos.keys())
        placeholders = ", ".join(["%s"] * len(dados_validos))
        
        query = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"
        
        # Executar inserção
        cursor = conexao.cursor()
        cursor.execute(query, list(dados_validos.values()))
        conexao.commit()
        
        st.success(f"✅ Registro inserido com sucesso em `{tabela}`!")
        st.balloons()
        
        # Mostrar ID do novo registro (se houver auto_increment)
        if cursor.lastrowid:
            st.info(f"📌 ID do novo registro: **{cursor.lastrowid}**")
        
        cursor.close()
        
    except Exception as e:
        st.error(f"❌ Erro ao inserir dados: {e}")
        st.info("Verifique os tipos de dados e restrições da tabela.")

def gerar_sql_insert(tabela, dados):
    """Gera e exibe o comando SQL INSERT"""
    # Filtrar dados vazios/nulos
    dados_validos = {}
    for chave, valor in dados.items():
        if valor is None:
            continue
        if isinstance(valor, str) and valor.strip() == "":
            continue
        dados_validos[chave] = valor
    
    if not dados_validos:
        st.warning("Nenhum dado para gerar SQL!")
        return
    
    # Format valores para SQL
    valores_formatados = []
    for valor in dados_validos.values():
        if isinstance(valor, str):
            # Escapar aspas simples
            valor_esc = valor.replace("'", "''")
            valores_formatados.append(f"'{valor_esc}'")
        elif isinstance(valor, datetime):
            valores_formatados.append(f"'{valor}'")
        elif isinstance(valor, (int, float)):
            valores_formatados.append(str(valor))
        elif valor is None:
            valores_formatados.append("NULL")
        else:
            valores_formatados.append(f"'{str(valor)}'")
    
    colunas_sql = ", ".join(dados_validos.keys())
    valores_sql = ", ".join(valores_formatados)
    
    sql = f"INSERT INTO {tabela} ({colunas_sql}) VALUES ({valores_sql});"
    
    # Exibir código SQL
    st.code(sql, language="sql")
    
    # Botão para copiar
    if st.button("📋 Copiar SQL"):
        st.write("SQL copiado! Use Ctrl+C")
        st.code(sql, language="sql")

def criar_novo_banco(nome_banco):
    """Cria um novo banco de dados"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Conectar sem banco específico
        conexao_temp = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        
        cursor = conexao_temp.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nome_banco}")
        cursor.close()
        conexao_temp.close()
        
        st.success(f"✅ Banco '{nome_banco}' criado com sucesso!")
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao criar banco: {e}")
        return False

def criar_banco_teste_direto():
    """Cria um banco de dados de teste (sem depender da conexão do app.py)"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Conectar sem banco específico
        conexao_temp = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        
        cursor = conexao_temp.cursor()
        
        # Cria banco
        cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_mysql")
        cursor.execute("USE sistema_mysql")
        
        # Cria tabelas de exemplo
        tabelas = [
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                idade INT,
                cidade VARCHAR(50),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                preco DECIMAL(10,2) NOT NULL,
                quantidade INT DEFAULT 0,
                categoria VARCHAR(50),
                descricao TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                produto_id INT,
                quantidade INT NOT NULL,
                data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('pendente', 'processando', 'concluido') DEFAULT 'pendente',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
            """
        ]
        
        for tabela_sql in tabelas:
            cursor.execute(tabela_sql)
        
        # Insere dados de exemplo
        cursor.execute("""
            INSERT IGNORE INTO usuarios (nome, email, idade, cidade) VALUES
            ('Ana Silva', 'ana@email.com', 28, 'São Paulo'),
            ('Carlos Santos', 'carlos@email.com', 35, 'Rio de Janeiro'),
            ('Mariana Lima', 'mariana@email.com', 22, 'Belo Horizonte')
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO produtos (nome, preco, quantidade, categoria) VALUES
            ('Notebook Dell', 3500.00, 10, 'Eletrônicos'),
            ('Mouse Wireless', 120.50, 50, 'Acessórios'),
            ('Teclado Mecânico', 450.00, 25, 'Acessórios'),
            ('Monitor 24"', 890.00, 15, 'Monitores')
        """)
        
        conexao_temp.commit()
        cursor.close()
        conexao_temp.close()
        
        # Atualiza a conexão no session_state se existir
        if "conexao_mysql" in st.session_state and st.session_state.conexao_mysql:
            try:
                st.session_state.conexao_mysql.database = "sistema_mysql"
            except:
                pass
        
        st.success("✅ Banco 'sistema_mysql' criado com 3 tabelas de exemplo!")
        st.balloons()
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao criar banco: {e}")
        return False
    
   
    
# Função para compatibilidade
if __name__ == "__main__":
    st.set_page_config(page_title="Formulários MySQL", layout="wide")
    pagina_formularios()