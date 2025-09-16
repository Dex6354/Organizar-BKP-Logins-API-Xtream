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
    4. Nome "Teste" por último, garantido.
    """
    def sort_key(user):
        name = user.get('name', '')

        # Ponto 1: Se o nome for exatamente "Teste", coloca-o no final, garantido.
        if name == 'Teste':
            # Usa uma tupla com um valor muito alto para garantir que seja o último.
            return (9999, name)

        # Ponto 2: Prioriza nomes que contêm o emoji 👎
        if '👎' in name:
            return (0, name) # Primeira prioridade

        # Ponto 3: Prioriza nomes que contêm letras ou palavras
        if re.search(r'[a-zA-ZáàâãéèêíïóôõöúüçÇÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜ]', name):
            return (1, name) # Segunda prioridade

        # Ponto 4: Define a ordem de prioridade para os emojis puros
        order = ['🔥', '💧', '🟢', '🔞', '📺', '❌']
        priority = {emoji: i for i, emoji in enumerate(order[::-1])}

        # Ponto 5: Ordena os nomes de emoji puro com base na prioridade inversa
        # Usamos um valor na tupla para que fiquem depois das prioridades anteriores.
        return (priority.get(name[0], len(order) + 2), name)

    return sorted(users_list, key=sort_key)

st.set_page_config(page_title="Organizador de Logins", layout="centered")
st.title("Organizador de Logins .dev")
st.markdown("Faça o upload do seu arquivo de backup `.dev` para organizar a lista de logins.")

uploaded_file = st.file_uploader("Escolha um arquivo .dev", type="dev")

if uploaded_file is not None:
    try:
        # Lê o conteúdo do arquivo
        file_content = uploaded_file.getvalue().decode("utf-8")
        data = json.loads(file_content)

        if "multi_users" in data:
            st.success("Arquivo lido com sucesso! Processando...")

            # Organiza a lista de usuários
            original_users = data["multi_users"]
            organized_users = sort_users(original_users)

            # Cria um novo dicionário com apenas a lista organizada
            new_data = {"multi_users": organized_users}

            # Converte o novo dicionário para JSON formatado
            organized_content = json.dumps(new_data, indent=2)

            # Define o nome do arquivo de download
            original_file_name, file_extension = os.path.splitext(uploaded_file.name)
            download_file_name = f"{original_file_name}_organized{file_extension}"

            # Exibe o JSON recolhido por padrão
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
