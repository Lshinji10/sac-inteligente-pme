import json
from google import genai
import pandas as pd
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="SAC Inteligente - Análise de Feedbacks", page_icon="🤖", layout="wide"
)

st.title("🤖 SAC Inteligente & Análise de Sentimento para PMEs")
st.markdown(
    "Esta ferramenta utiliza Inteligência Artificial para ler o feedback de"
    " clientes, classificar o sentimento, identificar a categoria do problema"
    " e alertar caso haja uma situação crítica."
)

# Configuração da Chave da API 
st.sidebar.header("⚙️ Configurações")
api_key = st.sidebar.text_input(
    "Digite sua Gemini API Key",
    type="password",
    help=(
        "Sua chave é processada apenas localmente para fazer a chamada à API."
    ),
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Dica de Apresentação")
st.sidebar.info(
    "Mostre isso para donos de restaurantes, lojas virtuais ou clínicas."
    " Eles economizam horas de triagem diária!"
)

# Área principal de entrada
st.markdown("### 📝 Analisar Feedback Individual")
feedback_input = st.text_area(
    "Cole o comentário ou mensagem do cliente aqui:",
    placeholder=(
        "Ex: Meu pedido atrasou 3 dias, a caixa veio amassada e o suporte não"
        " me responde no WhatsApp! Absurdo!"
    ),
    height=120,
)

if st.button("Executar Análise Inteligente", type="primary"):
  if not api_key:
    st.error("Por favor, insira sua chave da API do Gemini na barra lateral.")
  elif not feedback_input:
    st.warning("Insira algum texto de feedback para analisar.")
  else:
    with st.spinner("A IA está processando o feedback..."):
      try:
        # Inicializa o cliente do Gemini
        client = genai.Client(api_key=api_key)

        prompt = f"""
                Analise o seguinte comentário de um cliente de uma pequena empresa:
                "{feedback_input}"

                Retorne estritamente em formato JSON puro (sem comentários adicionais, sem markdown de bloco se possível, apenas o JSON válido) contendo exatamente estas chaves:
                - "sentimento": ("Positivo", "Neutro" ou "Crítico")
                - "categoria": (Ex: "Entrega", "Atendimento", "Preço", "Qualidade", "Outros")
                - "resumo_uma_linha": (Um resumo curto e direto do problema ou elogio)
                - "requer_atencao_urgente": (true ou false)
                """

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )

        
        texto_resp = response.text.strip()
        if texto_resp.startswith("```json"):
          texto_resp = texto_resp[7:]
        if texto_resp.endswith("```"):
          texto_resp = texto_resp[:-3]

        dados = json.loads(texto_resp.strip())

        
        st.success("Análise concluída com sucesso!")
        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
          sentimento = dados.get("sentimento", "N/A")
          if sentimento == "Positivo":
            st.metric("Sentimento", sentimento, "🟢 Ótimo")
          elif sentimento == "Crítico":
            st.metric("Sentimento", sentimento, "🔴 Atenção")
          else:
            st.metric("Sentimento", sentimento, "🟡 Neutro")

        with col2:
          st.metric("Categoria Identificada", dados.get("categoria", "N/A"))

        with col3:
          urgente = dados.get("requer_atencao_urgente", False)
          if urgente:
            st.error("🚨 Urgente: Sim")
          else:
            st.success("✅ Urgente: Não")

        st.info(
            f"**Resumo Executivo para o Gestor:**"
            f" {dados.get('resumo_uma_linha', '')}"
        )

      except Exception as e:
        st.error(f"Ocorreu um erro ao processar a resposta da IA: {e}")