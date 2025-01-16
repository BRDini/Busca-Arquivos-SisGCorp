Busca Arquivos SisGCorp

Por um bug no frontend do website, muitos documentos estão deferidos mas ainda aparecem como em análise e não é possivel baixar o pdf, esse sistema facilita a busca do local do documento via devtools e baixa automaticamente para o usuário logado.

Utilize o instalador para facilitar a instalação, caso deseja rodar o script manualmente siga as instruções abaixo:

1 - Instalar o Python com PATH

2 - Crie e ative um ambiente virtual (opcional, mas recomendado).

python -m venv env
source env/bin/activate  # No Windows, use `env\Scripts\activate`

3 - Instale as dependências

pip install requests customtkinter selenium webdriver-manager

4 - Rodo o script

python SISGCORP.py

