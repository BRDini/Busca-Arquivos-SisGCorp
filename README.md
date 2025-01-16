# Buscador de Arquivos SisGCorp

Este projeto foi desenvolvido com o objetivo de ajudar a comunidade de CACs no Brasil. Ele utiliza métodos já disponíveis e permitidos para acessar documentos no sistema, apenas automatizando o processo para facilitar a vida dos usuários. Nada aqui é ilegal, estamos apenas resolvendo uma limitação do frontend do site.

Por um bug no frontend do website, muitos documentos estão deferidos mas ainda aparecem como "em análise" e não é possível baixar o PDF. Este sistema facilita a busca do local do documento via DevTools e faz o download do documento para o usuário logado.

Utilize o instalador em releases para facilitar a instalação. Caso deseje rodar o script manualmente, siga as instruções abaixo:

## Passos para execução manual:

### 1. Instalar o Python com PATH

Certifique-se de instalar o Python e adicionar o diretório ao PATH durante a instalação.

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv env
env\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install requests customtkinter selenium webdriver-manager
```

### 4. Rode o script

```bash
python SISGCORP.py
```

---

## Funcionalidades

- Busca automática de documentos deferidos que ainda aparecem como "Pronto para Análise, Em análise e Deferido".
- Você pode clicar no botão "iniciar a busca" para buscar todos os documentos da conta ou digitar o número do processo especifico para consulta.
- Integração com DevTools para localizar o documento correto.
- Download automático dos documentos PDF vinculados ao usuário logado.

---

## Como usar

- Abra o programa ou rode o script
- Clique em "Abrir Navegador" para abrir o Edge em modo depuração
- Faça o login na sua conta do SisGCorp
- Clique em "Capturar Cookies" para o sistema conseguir interagir com a página
- Clique em "Iniciar Busca" ou digite um número de processo e clique em "Consultar Processo"

Obs. Caso tenha muitas páginas na sua conta, recomendamos navegar manualmente para a página Listar Processo e no final da página escolher para mostrar tudo ou o máximo possível de processos.


---

## Requisitos do Sistema

- Python 3.8 ou superior
- Sistema operacional Windows
- Navegador Microsoft Edge instalado

---

## Problemas Conhecidos

- O sistema depende do Microsoft Edge e não funciona com outros navegadores.
- Certifique-se de que o DevTools esteja ativado para capturar as informações corretamente.

---

## Contribuições

Sinta-se à vontade para contribuir com melhorias neste projeto. Para isso:

1. Faça um fork do repositório.
2. Crie uma nova branch para sua funcionalidade ou correção de bug.
3. Envie um pull request com uma descrição detalhada das mudanças realizadas.

---

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
