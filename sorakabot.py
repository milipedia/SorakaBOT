import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import re
import google.generativeai as genai
from geopy.geocoders import Nominatim

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
            1. Verifique se a pessoa consegue tossir ou falar.
        
        2. Se não consegue, está com obstrução total:
        Fique atrás da pessoa.
        Posicione uma mão fechada sobre o abdômen (acima do umbigo).
        Com a outra mão por cima, realize compressões abdominais rápidas e para cima (Manobra de Heimlich).
        Repita até o objeto sair ou a pessoa perder a consciência.
        
        3. Se perder a consciência:
        Chame o SAMU (192).
        Inicie RCP
        """,
        """Informações detalhadas sobre como agir em caso de engasgo em bebêsCrianças (1 ano até início da puberdade)\n
        Procedimento semelhante ao do adulto, com menor força.\n
        Evite empurrar demais para evitar fraturas em costelas.\n

        Bebês (<1 ano):
        1. Coloque o bebê de bruços sobre o seu antebraço, com a cabeça mais baixa.
        2. 5 tapotagens nas costas, entre as escápulas.
        3. Vire o bebê de barriga para cima e faça 5 compressões torácicas (dois dedos no esterno).
        4. Repita até expelir o objeto ou perder a consciência.
        5. Se inconsciente: inicie RCP para bebês (ver seção RCP).
        """,
        """Informações detalhadas sobre como lidar com diferentes tipos de cortes e sangramentos.\n
        Avaliação Inicial (válido para todos).\n
        Avalie a segurança do local.\n
        Lave bem as mãos ou use luvas descartáveis.\n
        Verifique o tipo de sangramento:\n
        Arterial: sangue vermelho vivo e em jato — risco alto.\n
        Venoso: sangue escuro e em fluxo contínuo — ainda grave.\n
        Capilar: superficial, escorre lentamente.\n

        Procedimentos

        Adultos, Crianças e Bebês
        1. Pressão Direta: aplique uma gaze/tecido limpo sobre o ferimento e pressione firmemente por pelo menos 5 a 10 minutos.
        2. Elevação: se possível, eleve a parte ferida acima do nível do coração.
        3. Não remova objetos cravados (espinhos, facas): estabilize e leve ao hospital.
        4. Lave com água e sabão se for um corte pequeno e limpo.
        5. Cubra com curativo esterilizado.
        6. Em caso de sangramento persistente ou profundo, leve à emergência.

        Atenção para crianças e bebês:
        Pressão deve ser mais delicada, mas eficaz.
        Nunca use algodão diretamente no corte profundo.
        Não use álcool ou antissépticos agressivos em feridas abertas em bebês.""",
        """Passos básicos da Reanimação Cardiopulmonar (RCP)\n
        RCP em Adultos\n
        1. Compressões torácicas:\n
        Local: centro do peito.\n
        Profundidade: 5 a 6 cm.\n
        Ritmo: 100 a 120 compressões por minuto (use a música “Stayin' Alive” como referência).\n
        Permita o retorno total do tórax.\n
        Relação: 30 compressões : 2 ventilações.\n

        2. Ventilações boca-a-boca:
        Incline a cabeça para trás.
        Tampe o nariz.
        Faça duas insuflações (1 segundo cada).

        RCP em Crianças (1 ano até puberdade)
        Compressões: com uma ou duas mãos, dependendo do tamanho da criança.
        Profundidade: cerca de 5 cm.
        Frequência e relação: igual ao adulto (30:2).

        RCP em Bebês (<1 ano)
        1. Compressões:
        Use dois dedos no centro do peito (abaixo da linha dos mamilos).
        Profundidade: cerca de 4 cm.
        Ritmo: 100 a 120/min.
        2. Ventilações:
        Boca-a-boca e nariz (cubra ambos com sua boca).
        Relação: 30:2 ou 15:2
        """
    ]
}
df_educativo = pd.DataFrame(data_educativo)

# --- Funções ---

def buscar_servicos_emergencia(cep):
    geolocator = Nominatim(user_agent="emergencia_bot")
    try:
        print(f"CEP recebido em buscar_servicos_emergencia: {cep}")  # Log: CEP recebido
        location = geolocator.geocode(f"{cep}, Porto Alegre, RS, Brasil")
        print(f"Resultado da geocodificação: {location}")  # Log: Resultado da geocodificação
        if location:
            latitude = location.latitude
            longitude = location.longitude
            print(f"Latitude: {latitude}, Longitude: {longitude}")  # Log: Coordenadas

            # --- Integração com o Gemini para buscar serviços de emergência ---
            genai.configure(api_key=st.secrets["AIzaSyDWTKse7wvbPt1sgFZb5_0NkFBGKC-hnuA"]) #Removi a quebra de linha
            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""
            Considerando a localização com latitude {latitude} e longitude {longitude},
            liste os endereços de hospitais, delegacias de polícia e corpo de bombeiros
            mais próximos em Porto Alegre, RS. Forneça o nome da instituição e o endereço.
            Limite a resposta a no máximo 5 resultados de cada tipo.
            """
            print(f"Prompt enviado ao Gemini: {prompt}") #log do prompt enviado
            response = model.generate_content(prompt)
            print(f"Resposta do Gemini: {response}")  # Log: Resposta do Gemini

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
                    elif tipo_atual:
                        partes = linha.split('-', 1)
                        if len(partes) == 2:
                            nome = partes[0].strip()
                            endereco = partes[1].strip()
                            servicos[tipo_atual].append(f"{nome} - {endereco}")

                contador = 1
                for tipo, lista in servicos.items():
                    if lista:
                        resultados += f"\n--- {tipo.capitalize()} ---\n"
                        for servico in lista:
                            resultados += f"{contador}. {servico}\n"
                            contador += 1
                print(f"Resultados formatados: {resultados}") #log dos resultados
                if contador > 1:
                    return resultados
                else:
                    return "Não foram encontrados serviços de emergência próximos a esta localização."
            else:
                return "Não foi possível obter informações sobre serviços de emergência."

        else:
            return "CEP inválido ou não encontrado."
    except Exception as e:
        print(f"Erro na função buscar_servicos_emergencia: {e}")  # Log: Exceção
        return f"Ocorreu um erro ao buscar os serviços de emergência: {e}"


def mostrar_educativo(tema_selecionado):
    conteudo = df_educativo[df_educativo['tema'] == tema_selecionado]['conteudo'].iloc[0]
    st.markdown(f"**{tema_selecionado}:**")
    print(f"Conteúdo educativo:\n{conteudo}") # Adicione esta linha para debug
    st.markdown(conteudo)
    # return conteudo

def buscar_servicos_emergencia(cep):
    geolocator = Nominatim(user_agent="emergencia_bot")
    try:
        location = geolocator.geocode(f"{cep}, Porto Alegre, RS, Brasil") # Especificando a região
        if location:
            latitude = location.latitude
            longitude = location.longitude

            # --- Integração com o Gemini para buscar serviços de emergência ---
            genai.configure(api_key=st.secrets["AIzaSyDWTKse7wvbPt1sgFZb5_0NkFBGKC-hnuA"])
            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""
            Considerando a localização com latitude {latitude} e longitude {longitude},
            liste os endereços de hospitais, delegacias de polícia e corpo de bombeiros
            mais próximos em Porto Alegre, RS. Forneça o nome da instituição e o endereço.
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
                    elif tipo_atual:
                        partes = linha.split('-', 1)
                        if len(partes) == 2:
                            nome = partes[0].strip()
                            endereco = partes[1].strip()
                            servicos[tipo_atual].append(f"{nome} - {endereco}")

                contador = 1
                for tipo, lista in servicos.items():
                    if lista:
                        resultados += f"\n--- {tipo.capitalize()} ---\n"
                        for servico in lista:
                            resultados += f"{contador}. {servico}\n"
                            contador += 1

                if contador > 1:
                    return resultados
                else:
                    return "Não foram encontrados serviços de emergência próximos a esta localização."
            else:
                return "Não foi possível obter informações sobre serviços de emergência."

        else:
            return "CEP inválido ou não encontrado."
    except Exception as e:
        return f"Ocorreu um erro ao buscar os serviços de emergência: {e}"

# --- Interface do Streamlit ---
st.title("ChatBot de Emergências Domésticas")

menu_principal = ["Emergência", "Educativo"]
opcao_principal = st.sidebar.selectbox("Selecione uma opção:", menu_principal)

if opcao_principal == "Emergência":
    st.subheader("Descreva sua emergência:")
    mensagem_usuario = st.text_input("")
    if mensagem_usuario:
        resposta = responder_emergencia(mensagem_usuario)
        st.write(f"**Resposta:** {resposta}")

elif opcao_principal == "Educativo":
    st.subheader("Selecione o tema sobre o qual você gostaria de aprender:")
    temas = df_educativo['tema'].tolist()
    tema_selecionado = st.selectbox("", temas)
    if tema_selecionado:
        conteudo_educativo = mostrar_educativo(tema_selecionado)
        st.write(f"**{tema_selecionado}:**")
        st.write(conteudo_educativo)

st.sidebar.info("Este ChatBot é uma ferramenta de auxílio e não substitui o atendimento profissional em emergências graves. Em caso de emergência, ligue para o 192 (SAMU).")

