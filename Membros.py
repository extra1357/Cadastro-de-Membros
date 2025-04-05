# Importações principais
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Constantes
CSV_FILE = 'dados_membros.csv'
IMAGES_DIR = 'fotos'
LOGO_PATH = 'logo_igreja.png'  # Certifique-se de ter esse arquivo na pasta

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# Função: Redimensiona imagem para tamanho 3x4 (em pixels)
def redimensionar_foto(imagem):
    return imagem.resize((300, 400))

# Função: Salva dados no CSV
def salvar_dados(dados):
    if os.path.exists(CSV_FILE):
        df_existente = pd.read_csv(CSV_FILE)
        df = pd.concat([df_existente, pd.DataFrame([dados])], ignore_index=True)
    else:
        df = pd.DataFrame([dados])
    df.to_csv(CSV_FILE, index=False)

# Função: Atualiza dados existentes
def atualizar_dados(index, novos_dados):
    df = pd.read_csv(CSV_FILE)
    for key in novos_dados:
        df.at[index, key] = novos_dados[key]
    df.to_csv(CSV_FILE, index=False)

# Função: Gera carteirinha (frente e verso)
def gerar_carteirinha(dados, foto_path):
    largura, altura = (970, 670)
    borda = 100
    verde_oliva = (107, 142, 35)

    carteirinha = Image.new("RGB", (largura + borda * 2, altura + borda * 2), verde_oliva)
    draw = ImageDraw.Draw(carteirinha)

    draw.rectangle([
        (borda, borda),
        (largura + borda, altura + borda)
    ], fill="white")

    foto = Image.open(foto_path).resize((300, 400))
    carteirinha.paste(foto, (borda + 30, borda + 30))

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).resize((300, 300))
        carteirinha.paste(logo, (largura + borda - 330, borda + 30))

    fonte = ImageFont.truetype("times.ttf", 24)
    draw.text((borda + 350, borda + 50), f"Nome: {dados['nome']}", fill="black", font=fonte)
    draw.text((borda + 350, borda + 100), f"Cargo: {dados['cargo']}", fill="black", font=fonte)

    draw.text((borda + 30, altura + borda - 100), f"Assinatura Pastor Presidente: {dados['pastor_presidente']}", fill="black", font=fonte)

    verso = Image.new("RGB", (largura + borda * 2, altura + borda * 2), verde_oliva)
    draw_verso = ImageDraw.Draw(verso)
    draw_verso.rectangle([
        (borda, borda),
        (largura + borda, altura + borda)
    ], fill="white")

    nascimento = dados['nascimento'][:4] if dados['nascimento'] else ''
    validade = (datetime.strptime(dados['data_batismo'], "%Y-%m-%d") + timedelta(days=730)).strftime("%d/%m/%Y")
    expedicao = datetime.now().strftime("%d/%m/%Y")

    draw_verso.text((borda + 50, borda + 50), f"Nome: {dados['nome']}", fill="black", font=fonte)
    draw_verso.text((borda + 50, borda + 100), f"Ano Nascimento: {nascimento}", fill="black", font=fonte)
    draw_verso.text((borda + 50, borda + 150), f"Data Batismo: {dados['data_batismo']}", fill="black", font=fonte)
    draw_verso.text((borda + 50, borda + 200), f"Expedição: {expedicao}", fill="black", font=fonte)
    draw_verso.text((borda + 50, borda + 250), f"Validade: {validade}", fill="black", font=fonte)

    return carteirinha, verso

# INÍCIO DA INTERFACE COM STREAMLIT
st.set_page_config(page_title="Cadastro de Membros - AD Munhoz Jr", layout="wide")
aba = st.sidebar.selectbox("Escolha a aba", ["Cadastro", "Visualizar", "Administração", "Carteirinha", "Aniversariantes"])

# ABA DE CADASTRO
if aba == "Cadastro":
    st.title("Cadastro de Membros")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo")
        endereco = st.text_input("Endereço")
        cep = st.text_input("CEP")
        bairro = st.text_input("Bairro")
        cidade = st.text_input("Cidade")
        pais = st.text_input("País", value="Brasil")
        nascimento = st.date_input("Data de nascimento")
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        faixa_etaria = st.selectbox("Faixa etária", ["Adulto", "Adolescente", "Criança"])
        casado = st.radio("Casado?", ["Sim", "Não"])
        data_batismo = st.date_input("Data de batismo")
        tem_cargo = st.radio("Tem cargo?", ["Sim", "Não"])
        cargo = st.selectbox("Cargo", ["", "Pastor Presidente", "Pastor Vice Presidente", "Pastor Auxiliar1", "Pastor Auxiliar2", "Evangelista", "Presbítero", "Diácono", "Missionária", "Missionário", "Cooperador"])
        foto = st.file_uploader("Envie uma foto 3x4", type=["jpg", "png"])
        pastor_presidente = st.text_input("Nome do Pastor Presidente")
        enviar = st.form_submit_button("Salvar Cadastro")

        if enviar:
            if nome and foto:
                img = Image.open(foto)
                img = redimensionar_foto(img)
                foto_path = os.path.join(IMAGES_DIR, f"{nome.replace(' ', '_')}.jpg")
                img.save(foto_path)

                dados = {
                    'nome': nome,
                    'endereco': endereco,
                    'cep': cep,
                    'bairro': bairro,
                    'cidade': cidade,
                    'pais': pais,
                    'nascimento': nascimento.strftime("%Y-%m-%d"),
                    'sexo': sexo,
                    'faixa_etaria': faixa_etaria,
                    'casado': casado,
                    'data_batismo': data_batismo.strftime("%Y-%m-%d"),
                    'tem_cargo': tem_cargo,
                    'cargo': cargo,
                    'foto': foto_path,
                    'pastor_presidente': pastor_presidente
                }
                salvar_dados(dados)
                st.success("Cadastro salvo com sucesso!")
            else:
                st.warning("Preencha o nome e envie uma foto.")

# ABA DE VISUALIZAÇÃO
elif aba == "Visualizar":
    st.title("Membros Cadastrados")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)
    else:
        st.info("Nenhum membro cadastrado ainda.")

# ABA DE ADMINISTRAÇÃO
elif aba == "Administração":
    st.title("Administração de Membros")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        selecionado = st.selectbox("Selecione um membro para editar", df['nome'].tolist())
        membro = df[df['nome'] == selecionado].iloc[0]

        with st.form("editar_form"):
            cidade = st.text_input("Cidade", membro['cidade'])
            cargo = st.selectbox("Cargo", ["", "Pastor Presidente", "Pastor Vice Presidente", "Pastor Auxiliar1", "Pastor Auxiliar2", "Evangelista", "Presbítero", "Diácono", "Missionária", "Missionário", "Cooperador"], index=0)
            pastor_presidente = st.text_input("Nome do Pastor Presidente", membro['pastor_presidente'])
            salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                index = df[df['nome'] == selecionado].index[0]
                atualizar_dados(index, {
                    'cidade': cidade,
                    'cargo': cargo,
                    'pastor_presidente': pastor_presidente
                })
                st.success("Dados atualizados com sucesso!")
    else:
        st.info("Nenhum membro cadastrado.")

# ABA DE CARTEIRINHA
elif aba == "Carteirinha":
    st.title("Gerar Carteirinha")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        membro = st.selectbox("Selecione um membro", df['nome'].tolist())
        dados = df[df['nome'] == membro].iloc[0]
        frente, verso = gerar_carteirinha(dados, dados['foto'])
        st.image(frente, caption="Frente da Carteirinha", use_column_width=True)
        st.image(verso, caption="Verso da Carteirinha", use_column_width=True)
    else:
        st.warning("Nenhum membro cadastrado ainda.")

# ABA DE ANIVERSARIANTES
elif aba == "Aniversariantes":
    st.title("Aniversariantes do Mês")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        mes_atual = datetime.now().month
        df['nascimento'] = pd.to_datetime(df['nascimento'])
        aniversariantes = df[df['nascimento'].dt.month == mes_atual]
        st.dataframe(aniversariantes[['nome', 'nascimento', 'sexo', 'faixa_etaria', 'cargo']])
    else:
        st.info("Nenhum membro cadastrado.")
