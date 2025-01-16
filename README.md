# Buscador de Arquivos SisGCorp

Por um bug no frontend do website, muitos documentos estão deferidos mas ainda aparecem como em análise e não é possível baixar o PDF. Este sistema facilita a busca do local do documento via DevTools e baixa automaticamente para o usuário logado.

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

- Busca automática de documentos deferidos que ainda aparecem como "em análise".
- Integração com DevTools para localizar o documento correto.
- Download automático dos documentos PDF vinculados ao usuário logado.

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
