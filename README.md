# SorakaBot – ChatBot de Emergências Domésticas

**SorakaBot** é um assistente virtual desenvolvido em Python com interface via Streamlit, focado em fornecer instruções de primeiros socorros em casos de emergências domésticas. O projeto também possui um modo educativo, com conteúdos detalhados sobre procedimentos básicos de emergência como engasgo, RCP, cortes e queimaduras. 

Além disso, o chatbot é capaz de identificar o CEP informado pelo usuário e, com auxílio da API do Gemini (Google), listar serviços de emergência próximos como hospitais, delegacias e unidades do corpo de bombeiros.

---

## Funcionalidades

- Modo Emergência:
  - Responde a palavras-chave indicando emergências (ex: “sangramento”, “engasgo”).
  - Solicita o CEP para localizar serviços próximos.
  - Integra-se à API do Gemini para obter informações geolocalizadas.

- Modo Educativo:
  - Fornece instruções detalhadas de primeiros socorros em diversos cenários.
  - Conteúdo acessível para leigos e introdutório para estudos básicos em saúde.

- Geolocalização:
  - Usa o `geopy` para converter CEP em coordenadas geográficas.
  - Permite a busca de serviços públicos relevantes por localização.

---

## Objetivos

- Oferecer uma ferramenta de apoio rápido em situações de emergência.
- Divulgar informações educativas acessíveis sobre primeiros socorros.
- Utilizar IA generativa para ampliar a utilidade e dinamismo do chatbot.

---

## Tecnologias Utilizadas

- `Python 3.10+`
- [Streamlit](https://streamlit.io/) – Interface gráfica
- [Pandas](https://pandas.pydata.org/) – Estruturação de dados
- [Geopy](https://geopy.readthedocs.io/) – Geolocalização via CEP
- [Google Generative AI (Gemini)](https://ai.google.dev/) – Consulta de serviços próximos
- `Regex` – Identificação de padrões de texto (como CEP)

---

## Instalação e Execução

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/seu-usuario/SorakaBot.git
   cd SorakaBot
