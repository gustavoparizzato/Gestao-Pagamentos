import streamlit as st
from datetime import date, timedelta
import pandas as pd
from src.menu.menu import menu_navegacao_sidebar
from src.database.autenticacao import exigir_login, usuario_atual
from src.database.recuperar_dados_bd import carregar_cheques, carregar_cheques_filtros
from src.database.persistir_dados_bd import cadastrar_cheque, atualizar_cheque

st.title("Cheques")

exigir_login(["admin", "analista", "viewer"])
u = usuario_atual() or {}
perfil = u.get("perfil") or ""

menu_navegacao_sidebar()

opcoes = ["Listar Cheques"]
if perfil == "admin":
    opcoes.extend(["Cadastrar Cheques", "Realizar Baixas"])
if perfil == "analista":
    opcoes.append("Realizar Baixas")

modo = st.radio("**Ações**", opcoes, key="settings_mode", horizontal= True)

st.markdown("---")

if modo == "Listar Cheques":
    st.subheader("📋 Cheques a Pagar")

    # data_ini e data_fim padrão (últimos 7 dias)
    hoje = date.today()
    data_inicio = hoje.replace(day=1)
    # ultimo dia do mês
    data_fim = hoje.replace(day=1) + timedelta(days=32)
    data_fim = data_fim.replace(day=1) - timedelta(days=1)

    st.markdown("**Campos de Filtros**")

    # Campos de filtro
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        ident_num = st.number_input("Identificador do cheque (sem zeros a esquerda)", key="filtro_identificador_cheque", step=1, format="%d")
        identificador_cheque = None if ident_num == 0 else int(ident_num)
    with colf2:
        nome_cliente = st.text_input("Nome do cliente", key="filtro_nome_cliente").strip() or None
    with colf3:
        data_inicio = st.date_input("Data inicial", value=data_inicio, key="filtro_data_inicio")
    with colf4:
        data_fim = st.date_input("Data final", value=data_fim, key="filtro_data_fim")

    st.markdown("---")

    if data_inicio > data_fim:
        st.error("A data inicial não pode ser maior que a data final.")
        st.stop()

    # Carrega os cheques no período
    cheques_df = carregar_cheques_filtros(data_inicio, data_fim, identificador_cheque, nome_cliente)
    if cheques_df is None or cheques_df.empty:
        st.info("Nenhum cheque encontrado no período selecionado.")
        st.stop()

    # Cabeçalho da tabela
    cols_head = st.columns([1.2, 2.2, 1.5, 1.8, 1.6, 1.6, 1.5, 1.3])
    with cols_head[0]: st.markdown("**Identificador**")
    with cols_head[1]: st.markdown("**Cliente**")
    with cols_head[2]: st.markdown("**Valor (R$)**")
    with cols_head[3]: st.markdown("**Banco**")
    with cols_head[4]: st.markdown("**Data Vencimento**")
    with cols_head[5]: st.markdown("**Data Pagamento**")
    with cols_head[6]: st.markdown("**Criado por**")
    with cols_head[7]: st.markdown("**Ações**")

    # Loop nas linhas (cada cheque)
    for _, row in cheques_df.iterrows():
        cid = row["idCheque"]
        edit_key = f"editing_cheque_{cid}"

        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        # Modo visualização
        if not st.session_state[edit_key]:
            col = st.columns([1.2, 2.2, 1.5, 1.8, 1.6, 1.6, 1.5, 1.3])
            with col[0]: st.write(row["identificadorCheque"])
            with col[1]: st.write(row["nomeCliente"])
            with col[2]: st.write(f"R$ {row['valor']:.2f}")
            with col[3]: st.write(row["banco"])
            with col[4]:
                if pd.notna(row["dataVencimento"]):
                    st.write(row["dataVencimento"].strftime("%d/%m/%Y"))
                else:
                    st.write("—")
            with col[5]:
                if pd.notna(row["dataPagamento"]):
                    st.write(row["dataPagamento"].strftime("%d/%m/%Y"))
                else:
                    st.write("—")
            with col[6]: st.write(row.get("criado_por") or "—")
            with col[7]:
                if perfil in ["admin", "analista"]:
                    if st.button("✏️ Editar", key=f"btn_edit_{cid}", type="primary"):
                        st.session_state[edit_key] = True
                        st.rerun()

        # Modo edição
        else:
            with st.form(f"form_edit_cheque_{cid}", clear_on_submit=False):
                col = st.columns([1.2, 2.2, 1.5, 1.8, 1.6, 1.6, 1.5, 1.3])
                with col[0]:
                    novo_identificador = st.number_input(" ", value=int(row["identificadorCheque"] or 0), step=1, format="%d", key=f"ident_{cid}", label_visibility="collapsed")
                with col[1]:
                    novo_cliente = st.text_input(" ", value=str(row["nomeCliente"]), key=f"cliente_{cid}", label_visibility="collapsed")
                with col[2]:
                    novo_valor = st.number_input(" ", value=float(row["valor"]), min_value=0.01, step=0.01, key=f"valor_{cid}", label_visibility="collapsed")
                with col[3]:
                    novo_banco = st.text_input(" ", value=str(row["banco"]), key=f"banco_{cid}", label_visibility="collapsed")
                with col[4]:
                    valor_venc = row["dataVencimento"]
                    if isinstance(valor_venc, pd.Timestamp):
                        valor_venc = valor_venc.date()
                    novo_vencimento = st.date_input(" ", value=valor_venc, key=f"venc_{cid}", label_visibility="collapsed")
                with col[5]:
                    valor_pag = row["dataPagamento"]
                    if pd.isna(valor_pag):
                        valor_pag = None
                    elif isinstance(valor_pag, pd.Timestamp):
                        valor_pag = valor_pag.date()
                    novo_pagamento = st.date_input(" ", value=valor_pag, key=f"pag_{cid}", label_visibility="collapsed")
                with col[6]:
                    st.write(row.get("criado_por") or "—")
                with col[7]:
                    b1, b2 = st.columns(2)
                    with b1:
                        salvar = st.form_submit_button("✅")
                    with b2:
                        cancelar = st.form_submit_button("❌")

                if cancelar:
                    st.session_state[edit_key] = False
                    st.rerun()

                if salvar:
                    novo_cliente = (novo_cliente or "").strip()

                    if novo_identificador <= 0:
                        st.error("Identificador deve ser maior que zero.")
                        st.stop()

                    if not novo_cliente or novo_valor <= 0:
                        st.error("Cliente e valor são obrigatórios.")
                        st.stop()

                    try:
                        ok = atualizar_cheque(
                            cid,
                            identificadorCheque=novo_identificador,
                            nomeCliente=novo_cliente,
                            banco=novo_banco,
                            valor=novo_valor,
                            dataVencimento=novo_vencimento,
                            dataPagamento=novo_pagamento
                        )
                        if ok:
                            st.success(f"Cheque {cid} atualizado com sucesso!")
                            st.session_state[edit_key] = False
                            st.rerun()
                        else:
                            st.error("Não foi possível atualizar o cheque.")
                    except Exception as e:
                        st.error(str(e))

    st.markdown("---")

    # Expansão: tabela completa
    with st.expander("📊 Visualizar tabela completa (somente leitura)"):
        st.dataframe(
            cheques_df[
                ["identificadorCheque", "nomeCliente", "valor", "banco", "dataVencimento", "dataPagamento", "criado_por", "criado_em", "ultima_modificacao"]
            ],
            hide_index=True,
            column_config={
                "identificadorCheque": st.column_config.NumberColumn("Identificador", format="%d"),
                "nomeCliente":         st.column_config.TextColumn("Cliente"),
                "valor":               st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                "banco":               st.column_config.TextColumn("Banco"),
                "dataVencimento":      st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY"),
                "dataPagamento":       st.column_config.DateColumn("Pagamento", format="DD/MM/YYYY"),
                "criado_por":          st.column_config.TextColumn("Criado por"),
                "criado_em":          st.column_config.DatetimeColumn("Criado em", format="DD/MM/YYYY HH:mm:ss"),
                "ultima_modificacao": st.column_config.DatetimeColumn("Última modificação", format="DD/MM/YYYY HH:mm:ss"),
            },
        )

if modo == "Cadastrar Cheques":

    st.subheader("📝 Cadastrar novo cheque")

    criado_por = u.get("nome") or "Sistema"

    with st.form("form_cadastrar_cheque"):
        col1, col2 = st.columns(2)
        with col1:
            identificador_cheque: int = st.number_input("Identificador do Cheque (sem zeros a esquerda)", step=1, format="%d")
            nomeCliente = st.text_input("Nome do Cliente")
            banco = st.text_input("Banco")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.00, step=100.00)  
            dataVencimento = st.date_input("Data de Vencimento", value=None, format="DD/MM/YYYY")
            dataPagamento = st.date_input("Data de Pagamento (opcional)", value=None, format="DD/MM/YYYY")

        salvar = st.form_submit_button("💾 Salvar Cheque", type="primary")

        if salvar:
            nomeCliente = nomeCliente.strip()
            if not nomeCliente or valor <= 0:
                st.error("Nome do cliente e valor maior que 0.00 são obrigatórios.")
                st.stop()

            try:
                ok = cadastrar_cheque(
                    identificadorCheque=identificador_cheque,
                    nomeCliente=nomeCliente,
                    valor=valor,
                    banco=banco,
                    dataVencimento=dataVencimento,
                    dataPagamento=dataPagamento if dataPagamento else None,
                    criado_por=criado_por
                )
                if ok:
                    st.success("✅ Cheque cadastrado com sucesso!")
                else:
                    st.error("❌ Não foi possível cadastrar o cheque.")
            except Exception as e:
                st.error(f"Erro ao cadastrar cheque: {e}")