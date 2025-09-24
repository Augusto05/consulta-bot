# ConsultaBot - Automação de Consulta de CNPJ com Selenium + Flet

## 🚀 Visão Geral  
Esta aplicação une automação de navegador (Selenium + ChromeDriver) e interface gráfica desktop (Flet) em tema escuro para:  
- Consultar dados de CNPJ (razão social, e-mail, telefone, CNAE e quadro societário) via API da ReceitaWS  
- Processar e retornar consultas em lote a partir de arquivo TXT  
- Buscar CNPJ associado a um telefone usando pesquisa no Google (Visto que não existe API nativa para busca por telefone)
- Exibir feedback visual com spinners, barras de progresso e notificações  
- Copiar resultados para a área de transferência  
- Executar como aplicativo desktop nativo (janela em modo escuro)

## 🧩 Recursos  
- Consulta única ou em lote de CNPJs  
- Busca de CNPJ por telefone  
- Layout responsivo em modo escuro  
- Janela desktop independente via Flet
- 
## 📋 Pré-requisitos  
- Python 3.8 ou superior  
- Google Chrome instalado  
- Internet ativa para chamadas HTTP

## ⚙️ Instalação  
1. Clone este repositório:  
   git clone https://github.com/SEU_USUARIO/seu-repo.git  
   cd seu-repo  
2. Crie e ative um ambiente virtual:  
   python -m venv .venv  
   # Windows  
   .venv\Scripts\activate  
   # macOS/Linux  
   source .venv/bin/activate  
3. Instale as dependências:  
   pip install --upgrade pip  
   pip install -r requirements.txt

## 🛠️ Configuração do ChromeDriver  
1. No Chrome, abra chrome://settings/help e anote a versão instalada  
2. Baixe o ChromeDriver compatível em https://developer.chrome.com/docs/chromedriver/downloads  
3. Extraia o executável e mova para pasta acessível, por exemplo:  
   Windows: C:\Drivers\chromedriver-win64\chromedriver.exe  
   macOS/Linux: /usr/local/bin/chromedriver  
4. No arquivo app.py, ajuste a constante:  
   CHROMEDRIVER_PATH = r"C:\Drivers\chromedriver-win64\chromedriver.exe"

## ▶️ Execução  
Com o virtualenv ativado e o ChromeDriver configurado, execute:  
   python consultabot.py  
A janela desktop em modo escuro abrirá automaticamente.

## 📂 Estrutura do Projeto  
consultabot.py    # Código principal (Selenium + Flet)  
requirements.txt  # Dependências Python  
cnpjs.txt         # Arquivo para inserir lista de CNPJs
README.md         # Este documento

## 📖 Uso  
1. Consulta por CNPJ (API):  
   - Insira um CNPJ de 14 dígitos e clique em **Consultar**  
   - Ou ative **Modo Lote**, selecione um TXT e clique em **Processar lote**  
2. Consulta por Telefone (Google):  
   - Insira um telefone (10 ou 11 dígitos)  
   - Clique em **Consultar Tel.** para buscar o CNPJ  
3. Copiar Resultado:  
   - Clique em **Copiar** para levar o último resultado ao clipboard

## 🤝 Contribuição  
1. Faça fork deste repositório  
2. Crie uma branch para sua feature:  
   git checkout -b feature/nova-feature  
3. Faça commit das alterações:  
   git commit -m "Adiciona nova feature"  
4. Envie para o remoto:  
   git push origin feature/nova-feature  
5. Abra um Pull Request

