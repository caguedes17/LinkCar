# LinkCar 🚗

**Conectando pessoas ao carro ideal.**

O **LinkCar** é um projeto acadêmico de aplicação web que reúne anúncios de veículos, gestão de acesso por função (**RBAC**) e um sistema de **Match por compatibilidade**. O usuário informa suas preferências; o sistema avalia os anúncios disponíveis e apresenta um ranking de adequação.

**Repositório:** https://github.com/caguedes17/LinkCar

## O que o sistema faz

- **Contas e autenticação:** cadastro, login, logout e recuperação de senha por e-mail.
- **Controle de acesso (RBAC):** perfis `Administrador`, `Anunciante` e `Usuario`, com permissões específicas.
- **Anúncios:** cadastro, consulta, edição e desativação lógica de veículos; anúncios associados ao anunciante responsável.
- **Fotos:** envio, substituição e remoção de uma foto principal por veículo. Os arquivos ficam em `static/uploads/veiculos/`; o SQLite armazena o caminho.
- **Catálogo e favoritos:** consulta aos veículos ativos e gerenciamento da lista de favoritos.
- **Match:** ranking percentual baseado nos critérios preenchidos, com explicação dos pontos atendidos e não atendidos.

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Backend e APIs | Python, Flask |
| Banco de dados | SQLite |
| Interface | HTML, CSS e JavaScript |
| Processamento das imagens | Pillow |
| Configuração local | python-dotenv |
| Versionamento | Git e GitHub |

## Como executar

O procedimento completo, com criação do banco, configuração do `.env`, teste de contas e resolução de erros, está em **`Manual_Instalacao_LinkCar.pdf`**, entregue separadamente.

Resumo para quem **já preparou o banco** e o ambiente:

```powershell
python -m pip install -r requirements.txt
python -m flask --app app_frontend run
```

Abra **http://127.0.0.1:5000/** no navegador. Execute os comandos **na pasta raiz do projeto**, onde está `app_frontend.py`.

Para uma **instalação nova**, primeiro crie `linkcar.db`, execute `estrutura.sql` e depois `dados_iniciais.sql` em um **banco vazio**. Configure `FLASK_SECRET_KEY` no `.env` antes de iniciar o Flask. **Nunca execute `estrutura.sql` no seu banco em uso:** o arquivo contém instruções `DROP TABLE IF EXISTS` que apagam tabelas e registros.

## Organização principal

```text
LinkCar/
├── app.py                  # APIs e regras de aplicação
├── app_frontend.py         # Entrada recomendada do Flask
├── frontend_routes.py      # Páginas e serviços do frontend
├── fotos_veiculos_routes.py # Upload e remoção de fotos
├── banco.py                # Conexão com o SQLite
├── cadastro.py / login.py  # Contas e autenticação
├── permissoes.py           # Regras de acesso
├── veiculos.py             # Operações dos anúncios
├── match.py                # Ranking de compatibilidade
├── estrutura.sql           # Criação do esquema (somente banco novo)
├── dados_iniciais.sql      # Funções, permissões e recursos
├── templates/              # Páginas HTML
├── static/css/             # Estilos
├── static/js/              # Comportamento no navegador
├── static/img/             # Imagens ilustrativas da interface
└── static/uploads/veiculos/ # Fotos enviadas (não versionadas)
```

## Perfis de acesso

- **Usuário:** consulta o catálogo, utiliza o Match e gerencia favoritos.
- **Anunciante:** cadastra, edita e desativa seus anúncios, além de consultar veículos.
- **Administrador:** possui permissões de administração e gerenciamento definidas no banco. A atribuição desse perfil não ocorre no cadastro público.

Os dados de referência são carregados pelo script `dados_iniciais.sql`. Ele não cria contas com senhas predefinidas; cadastre um **Usuário** ou **Anunciante** pela interface.

## Como funciona o Match

O sistema considera os critérios preenchidos: preço, carroceria, combustível, motorização, cor, marca, recursos tecnológicos, espaço interno e estilo/design. **Preço máximo é um filtro eliminatório** quando informado; os demais critérios contribuem com pesos para a pontuação. O resultado é apresentado em percentual, ordenado pela compatibilidade e, em caso de empate, pelo menor preço.

## Imagens, segurança e privacidade

- As imagens ilustrativas devem ter autor, fonte e licença registrados em `CREDITOS_DAS_FOTOS.md` (conferir as atribuições de cada arquivo).
- Fotos enviadas pelos anunciantes ficam fora do Git, assim como `.env` e `linkcar.db`.
- O sistema utiliza hashing de senhas com *scrypt*, autorização por perfil e verificação de proprietário nas operações de anúncios.
- **Projeto acadêmico para demonstração local.** Uma disponibilização pública exige revisão adicional de segurança, implantação, testes automatizados, proteção de dados e manutenção.

## Documentação

- **Manual_Instalacao_LinkCar.pdf** — instalação detalhada e solução de problemas.
- **Apresentacao_LinkCar.pptx** — apresentação acadêmica do projeto.
- **CREDITOS_DAS_FOTOS.md** — origem e condições de reutilização das imagens de terceiros.

**LinkCar · Projeto acadêmico PROG II - CAROLINE E ENZO · 2026**

*
