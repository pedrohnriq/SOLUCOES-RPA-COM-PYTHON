# Consolidação e Envio de Relatório Gerencial por E-mail

Desafio Final — **Desenvolvimento de Soluções RPA com Python**
PUC Minas | Prof.: Leandro Lessa
Autor: Pedro

## Objetivo

Automação em Python, modularizada, que coleta três bases de dados fictícias,
trata as inconsistências encontradas, integra as informações e envia a cada
gestor um e-mail individual com um relatório consolidado da situação dos
projetos e das pendências de treinamento da sua área.

## Bases de dados utilizadas

Localizadas em `Base de Dados de RH/`:

| Arquivo | Conteúdo |
|---|---|
| `gestores_projetos.csv` | Relação de projetos e o gestor responsável por cada um |
| `status_projetos.csv` | Dados brutos de andamento, prazos e orçamento de cada projeto |
| `rh_treinamentos.csv` | Treinamentos obrigatórios dos colaboradores, por área |

## Estrutura do projeto

```
config.py          # parâmetros e caminhos (lê .env)
log_config.py       # configuração de logging (arquivo + console)
extracao.py          # leitura das três bases
tratamento.py        # limpeza e padronização (texto, datas, duplicatas)
integracao.py         # merge de gestores + status dos projetos
regras_negocio.py     # cálculo de status dos projetos e indicadores por gestor
envio_email.py        # geração e disparo dos e-mails (real ou simulado)
main.py               # orquestração do fluxo completo
relatorio_tratamento_dados.docx  # relatório de 1 página (inconsistências e regra de status)
emails_enviados/       # evidência dos e-mails simulados (gerada em tempo de execução)
logs/                   # log de execução (gerado em tempo de execução)
```

## Como rodar

### 1. Instalar dependências

```bash
pip install pandas numpy python-dotenv
```

### 2. Configurar o `.env`

Copie `.env.example` para `.env` (na raiz do projeto) e preencha:

```
SIMULAR_ENVIO=false        # true = não envia de verdade, só grava em emails_enviados/
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USUARIO=seu_email@dominio.com
SMTP_SENHA=sua_senha_ou_senha_de_app
```

O `.env` **não** deve ser commitado (já está no `.gitignore`).

Com `SIMULAR_ENVIO=true` (padrão), nenhum e-mail real é enviado: o conteúdo é
gravado em `emails_enviados/*.txt` e registrado no log — serve como evidência
de envio para os gestores fictícios da base.

### 3. Rodar a automação

```bash
python main.py
```

O fluxo executa, em sequência: extração → tratamento → integração → cálculo
de status e indicadores → envio de e-mail para cada gestor → envio do
relatório de um gestor específico (`GESTOR_ID_RELATORIO_PROFESSOR`, em
`config.py`) para o e-mail real do professor (`EMAIL_DESTINO_PROFESSOR`).

Acompanhe o andamento no console e em `logs/execucao_rpa.log`.

## Regra de cálculo de status dos projetos

Deduzida a partir das datas (`data_inicio`, `data_prevista_fim`,
`data_conclusao`), nunca de um campo de texto pronto:

- **Concluído dentro do prazo** — `data_conclusao` preenchida e ≤ `data_prevista_fim`
- **Concluído com atraso** — `data_conclusao` preenchida e > `data_prevista_fim`
- **Atrasado** — sem `data_conclusao` e `data_prevista_fim` já passou
- **Em andamento** — sem `data_conclusao` e `data_prevista_fim` ainda não chegou

Detalhes sobre as inconsistências encontradas nos dados e como foram
tratadas estão em `relatorio_tratamento_dados.docx`.

## Conteúdo do e-mail por gestor

- **Bloco 1 — Projetos**: total por status, % médio de execução (projetos não
  concluídos), tempo médio de duração (projetos concluídos) e valor total orçado.
- **Bloco 2 — Treinamentos da área**: pendentes, vencidos, % de conformidade
  e lista nominal dos colaboradores com treinamento vencido.

Cada gestor recebe apenas os dados do seu próprio escopo (projetos que
gerencia + área de treinamento sob sua responsabilidade).
