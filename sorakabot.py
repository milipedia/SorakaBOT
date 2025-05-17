import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import re
import google.generativeai as genai

# Função para configurar a API (chamada sempre que necessário)
def configure_genai():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return True
    except streamlit.runtime.secrets.StreamlitSecretNotFoundError:
        st.error("Erro: Chave da API Gemini não encontrada nos segredos do Streamlit.")
        return False
    except Exception as e:
        st.error(f"Ocorreu um erro ao configurar a API Gemini: {e}")
        return False

# Banco de Dados de Emergências
data_emergencias = {
    'palavra_chave': ['corte', 'sangramento', 'engasgo', 'asfixia', 'queimadura'],
    'instrucoes': [
        "Para um corte, siga estes passos: Mantenha a calma e com mãos limpas controle o sangramento, em casos de corte superficial você pode usar água corrente, em cortes maiores considere pegar um pedaço de pano para estancar o ferimento, cubra o local da ferida, preferencialmente com uma gaze limpa e busque atendimento médico.",
        "Em caso de sangramento intenso, Caso o corte possa ser estancável, a indicação é que a pessoa que esteja socorrendo o ferido pressione uma atadura ou um pano limpo e seco sobre a ferida. A compressão sobre a região deve ser feita até o atendimento médico especializado ",
        "Se alguém estiver engasgando, realize a manobra de Heimlich: Posicione-se por trás e enlace a vítima com os braços ao redor do abdome (se for uma criança, ajoelhe-se primeiro), caso ela esteja consciente. Uma das mãos permanece fechada sobre a chamada “boca do estômago” (região epigástrica). A outra mão comprime a primeira, ao mesmo tempo em que empurra a “boca do estômago” para dentro e para cima, como se quisesse levantar a vítima do chão. Faça movimentos de compressão para dentro e para cima (como uma letra “J”), até que a vítima elimine o corpo estranho.",
        "Se a pessoa não conseguir respirar, ligue imediatamente para o 192, inicie a RCP até a chegada do atendimento: Para realizar a RCP (Reanimação Cardiopulmonar) em adultos, comece com 30 compressões torácicas seguidas de 2 respirações de salvamento (proporção 30:2). As compressões devem ser profundas, na região central do tórax, e com uma frequência de 100 a 120 por minuto.",
        "Para queimaduras, resfrie a área com água corrente fria, importante: nunca fure bolhas nem passe produtos caseiros em lesões de queimadura. Mantenha o local hidratado"
    ]
}
df_emergencias = pd.DataFrame(data_emergencias)

# Banco de Dados Educativo
data_educativo = {
    'tema': ['Engasgo (Adulto)', 'Engasgo (Bebê)', 'Cortes e Sangramentos', 'RCP Básica'],
    'conteudo': [
        """Informações detalhadas sobre como agir em caso de engasgo em adultos:\n
            1. Verifique se a pessoa consegue tossir ou falar.\n
            2. Se não consegue, está com obstrução total:\n
                Fique atrás da pessoa.\n
                Posicione uma mão fechada sobre o abdômen (acima do umbigo).\n
                Com a outra mão por cima, realize compressões abdominais rápidas e para cima (Manobra de Heimlich).\n
                Repita até o objeto sair ou a pessoa perder a consciência.\n
            3. Se perder a consciência:\n
                Chame o SAMU (192).\n
                Inicie RCP\n
        """,
        """Informações detalhadas sobre como agir em caso de engasgo em bebêsCrianças (1 ano até início da puberdade)\n
        Procedimento semelhante ao do adulto, com menor força.\n
        Evite empurrar demais para evitar fraturas em costelas.\n
        \n
        Bebês (<1 ano):\n
        1. Coloque o bebê de bruços sobre o seu antebraço, com a cabeça mais baixa.\n
        2. 5 tapotagens nas costas, entre as escápulas.\n
        3. Vire o bebê de barriga para cima e faça 5 compressões torácicas (dois dedos no esterno).\n
        4. Repita até expelir o objeto ou perder a consciência.\n
        5. Se inconsciente: inicie RCP para bebês (ver seção RCP).\n
        """,
        """Informações detalhadas sobre como lidar com diferentes tipos de cortes e sangramentos.\n
        Avaliação Inicial (válido para todos).\n
        Avalie a segurança do local.\n
        Lave bem as mãos ou use luvas descartáveis.\n
        Verifique o tipo de sangramento:\n
        Arterial: sangue vermelho vivo e em jato — risco alto.\n
        Venoso: sangue escuro e em fluxo contínuo — ainda grave.\n
        Capilar: superficial, escorre lentamente.\n
        \n
        Procedimentos\n
        \n
        Adultos, Crianças e Bebês\n
        1. Pressão Direta: aplique uma gaze/tecido limpo sobre o ferimento e pressione firmemente por pelo menos 5 a 10 minutos.\n
        2. Elevação: se possível, eleve a parte ferida acima do nível do coração.\n
        3. Não remova objetos cravados (espinhos, facas): estabilize e leve ao hospital.\n
        4. Lave com água e sabão se for um corte pequeno e limpo.\n
        5. Cubra com curativo esterilizado.\n
        6. Em caso de sangramento persistente ou profundo, leve à emergência.\n
        \n
        Atenção para crianças e bebês:\n
        Pressão deve ser mais delicada, mas eficaz.\n
        Nunca use algodão diretamente no corte profundo.\n
        Não use álcool ou antissépticos agressivos em feridas abertas em bebês.""",
        """Passos básicos da Reanimação Cardiopulmonar (RCP)\n
        RCP em Adultos\n
        1. Compressões torácicas:\n
            Local: centro do peito.\n
            Profundidade: 5 a 6 cm.\n
            Ritmo: 100 a 120 compressões por minuto (use a música “Stayin' Alive” como referência).\n
            Permita o retorno total do tórax.\n
            Relação: 30 compressões : 2 ventilações.\n
        \n
        2. Ventilações boca-a-boca:\n
            Incline a cabeça para trás.\n
            Tampe o nariz.\n
            Faça duas insuflações (1 segundo cada).\n
        \n
        RCP em Crianças (1 ano até puberdade)\n
        Compressões: com uma ou duas mãos, dependendo do tamanho da criança.\n
        Profundidade: cerca de 5 cm.\n
        Frequência e relação: igual ao adulto (30:2).\n
        \n
        RCP em Bebês (<1 ano)\n
        1. Compressões:\n
            Use dois dedos no centro do peito (abaixo da linha dos mamilos).\n
            Profundidade: cerca de 4 cm.\n
            Ritmo: 100 a 120/min.\n
        2. Ventilações:\n
            Boca-a-boca e nariz (cubra ambos com sua boca).\n
            Relação: 30:2 ou 15:2\n
        """
    ]
}
df_educativo = pd.DataFrame(data_educativo)

def buscar_endereco_por_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção para status de erro
        data = response.json()
        if "erro" not in data:
            return f"{data['logradouro']}, {data['bairro']}, {data['localidade']} - {data['uf']}"
        else:
            return "CEP não encontrado."
    except requests.exceptions.RequestException as e:
        return f"Erro ao consultar o ViaCEP: {e}"

def buscar_servicos_emergencia(cep):
    endereco_info = buscar_endereco_por_cep(cep)
    if "Erro" not in endereco_info and "não encontrado" not in endereco_info:
        geolocator = Nominatim(user_agent="emergencia_bot")
        try:
            location_data = geolocator.geocode(endereco_info, timeout=3)
            if location_data:
                latitude = location_data.latitude
                longitude = location_data.longitude

                if configure_genai():  # Configura a API antes de usar
                    model = genai.GenerativeModel('gemini-2-pro')  # Usando um modelo específico

                    prompt = f"""
                    Considerando a localização com o endereço: {endereco_info} (latitude: {latitude}, longitude: {longitude}),
                    liste os endereços de hospitais, delegacias de polícia e corpo de bombeiros
                    mais próximos. Forneça o nome da instituição e o endereço.
                    Limite a resposta a no máximo 5 resultados de cada tipo.
                    """
                    response = model.generate_content(prompt)

                    if response.text:
                        resultados = "Serviços de emergência próximos:\n"
                        servicos = {"hospitais": [], "delegacias": [], "bombeiros": []}
                        linhas = response.text.split('\n')
                        tipo_atual = None

                        for linha in linhas:
                            linha = linha.strip()
                            if not linha:
                                continue
                            if "hospital" in linha.lower():
                                tipo_atual = "hospitais"
                            elif "delegacia" in linha.lower() or "polícia" in linha.lower():
                                tipo_atual = "delegacias"
                            elif "bombeiro" in linha.lower():
                                tipo_atual = "bombeiros"
                            elif tipo_atual and "-" in linha:
                                partes = linha.split('-', 1)
                                if len(partes) == 2:
                                    nome = partes[0].strip()
                                    endereco = partes[1].strip()
                                    servicos[tipo_atual].append(f"{nome} - {endereco}")

                        output = resultados
                        for tipo, lista in servicos.items():
                            if lista:
                                output += f"\n--- {tipo.capitalize()} ---\n"
                                for i, servico in enumerate(lista):
                                    output += f"{i+1}. {servico}\n"
                        return output
                    else:
                        return "Não foi possível obter informações sobre serviços de emergência."
                else:
                    return None  # Retorna None se a configuração da API falhar
            else:
                return "Não foi possível localizar as coordenadas para o endereço fornecido."
        except Exception as e:
            return f"Ocorreu um erro ao buscar serviços de emergência: {e}"
    else:
        return endereco_info

def responder_emergencia(mensagem):
    mensagem = mensagem.lower()
    cep_match = re.search(r'\d{5}-\d{3}|\d{8}', mensagem)
    if cep_match:
        cep = cep_match.group(0)
        return buscar_servicos_emergencia(cep)
    elif re.search(r'\b(cep)\b', mensagem, re.IGNORECASE):
        return "Por favor, digite o CEP para buscar os serviços de emergência próximos."
    elif any(palavra in mensagem for palavra in ['grave', 'urgente', 'inconsciente', 'não respira']):
        return "Esta parece ser uma emergência grave! Ligue imediatamente para o SAMU (192)."
    else:
        for index, row in df_emergencias.iterrows():
            if row['palavra_chave'] in mensagem:
                return row['instrucoes']
        return "Desculpe, não entendi a emergência. Por favor, seja mais específico."

def mostrar_educativo(tema_selecionado):
    conteudo = df_educativo[df_educativo['tema'] == tema_selecionado]['conteudo'].iloc[0]
    st.markdown(f"**{tema_selecionado}:**")
    st.markdown(conteudo)

# --- Interface do Streamlit ---
st.title("ChatBot de Emergências Domésticas")

menu_principal = ["Emergência", "Educativo"]
opcao_principal = st.sidebar.selectbox("Selecione uma opção:", menu_principal)

if opcao_principal == "Emergência":
    st.subheader("Descreva sua emergência ou digite o CEP para buscar serviços:")
    mensagem_usuario = st.text_input("")
    if mensagem_usuario:
        resposta = responder_emergencia(mensagem_usuario)
        if resposta:  # Certifica-se de que há uma resposta para mostrar
            st.write(f"**Resposta:** {resposta}")

elif opcao_principal == "Educativo":
    st.subheader("Selecione o tema sobre o qual você gostaria de aprender:")
    temas = df_educativo['tema'].tolist()
    tema_selecionado = st.selectbox("", temas)
    if tema_selecionado:
        mostrar_educativo(tema_selecionado)

st.sidebar.info("Este ChatBot é uma ferramenta de auxílio e não substitui o atendimento profissional em emergências graves. Em caso de emergência, ligue para o 192 (SAMU).")
