import streamlit as st
import json
import re
import os

def sort_users(users_list):
    """
    Organiza a lista de usuários com base nas regras de ordenação:
    1. Nome com 👎.
    2. Nomes com letras/palavras.
    3. Emojis na ordem inversa.
    4. Nomes "Teste" por último, garantido.
    5. Nomes que contêm palavras, ordenados pelo número de palavras (decrescente),
       depois pelo nome (Z-A) e por fim pela URL (Z-A).
    6. Se a prioridade for igual, ordena a URL por ordem alfabética de Z até A.
    """
    def sort_key(user):
        name = user.get('name', '')
        url = user.get('url', '')

        # Regra 1: Se o nome for exatamente "Teste", coloca-o no final.
        if name == 'Teste':
            return (9999, '')

        # Regra 2: Prioriza nomes que contêm o emoji 👎
        if '👎' in name:
            # Prioridade 0, depois por nome e URL (Z-A)
            return (0, name, url[::-1])

        # Regra 3: Prioriza nomes que contêm letras ou palavras
        is_word_name = bool(re.search(r'[a-zA-ZáàâãéèêíïóôõöúüçÇÁÀÂÃÉÈÊÍÏÓÕÖÚÜ]', name))
        if is_word_name:
            # Conta palavras de forma robusta
            word_count = len(re.findall(r'\b\w+\b', name))
            # Prioridade 1, depois por contagem de palavras (desc),
            # nome (Z-A) e URL (Z-A)
            return (1, -word_count, name[::-1], url[::-1])

        # Regra 4: Define a ordem de prioridade para os emojis puros
        order = ['🔥', '💧', '🟢', '🔞', '📺', '❌']
        priority = {emoji: i for i, emoji in enumerate(order[::-1])}

        # Prioridade baseada na lista de emojis, depois por nome (Z-A)
        # e URL (Z-A)
        return (priority.get(name[0], len(order) + 2), name[::-1], url[::-1])

    return sorted(users_list, key=sort_key)

st.set_page_config(page_title="Organizador de Logins", layout="centered")
st.title("Organizador de Logins .dev")
st.markdown("Faça o upload do seu arquivo de backup `.dev` para organizar a lista de logins.")

uploaded_file = st.file_uploader("Escolha um arquivo .dev", type="dev")

if uploaded_file is not None:
    try:
        file_content = uploaded_file.getvalue().decode("utf-8")
        data = json.loads(file_content)

        if "multi_users" in data:
            st.success("Arquivo lido com sucesso! Processando...")

            original_users = data["multi_users"]
            organized_users = sort_users(original_users)

            new_data = {"multi_users": organized_users}

            organized_content = json.dumps(new_data, indent=2, ensure_ascii=False)

            original_file_name, file_extension = os.path.splitext(uploaded_file.name)
            download_file_name = f"{original_file_name}_organized{file_extension}"

            with st.expander("Clique para ver o conteúdo organizado"):
                st.json(new_data)

            st.download_button(
                label="Clique para Baixar o Arquivo Organizado",
                data=organized_content,
                file_name=download_file_name,
                mime="application/octet-stream"
            )

            st.info("Seu novo arquivo `.dev` foi gerado e está pronto para ser baixado. Você pode usá-lo para substituir o arquivo de backup original.")

        else:
            st.error("O arquivo `.dev` não contém a chave 'multi_users'. Por favor, verifique se o arquivo está no formato correto.")

    except json.JSONDecodeError:
        st.error("Erro ao decodificar o arquivo JSON. Certifique-se de que é um arquivo JSON válido.")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
