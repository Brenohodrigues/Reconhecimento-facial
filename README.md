[README.md](https://github.com/user-attachments/files/32155469/README.md)
# Sistema de Cadastro e Reconhecimento Facial

Sistema local em Python para cadastro de usuários com autenticação facial via webcam, com arquitetura pronta para migrar de SQLite para PostgreSQL no futuro.

## Estrutura do projeto

```
projeto/
├── main.py                          # Interface gráfica (Tkinter) e orquestração
├── requirements.txt                 # Dependências do projeto
├── data/                             # Onde o arquivo do banco SQLite é criado
│
├── database/
│   ├── connection.py                 # Configuração do engine/sessão SQLAlchemy
│   └── models.py                     # Modelo (tabela) User
│
├── authentication/
│   └── auth.py                       # Hash e verificação de senha (bcrypt)
│
├── facial_recognition/
│   ├── register_face.py              # Captura de rosto via webcam (cadastro)
│   └── recognize_face.py             # Reconhecimento facial em tempo real
│
└── services/
    └── user_service.py               # Regras de negócio (validações, cadastro)
```

### O que cada arquivo faz

- **`main.py`**: cria a janela principal, com formulário de cadastro e botões para
  iniciar o cadastro facial e o reconhecimento. Não acessa o banco diretamente —
  delega tudo para `services/user_service.py`.

- **`database/connection.py`**: cria a conexão com o banco (SQLite por padrão) e a
  função `init_db()` que cria as tabelas. É o único arquivo que você precisa mudar
  para migrar de banco de dados.

- **`database/models.py`**: define a tabela `users` (nome, e-mail, hash da senha,
  embedding facial serializado em JSON, data de criação).

- **`authentication/auth.py`**: gera e verifica hashes bcrypt de senha. A senha em
  texto puro nunca é salva nem logada.

- **`facial_recognition/register_face.py`**: abre a webcam, pede 5 amostras do
  rosto (tecla ESPAÇO) e retorna o embedding facial médio (vetor de 128 números).

- **`facial_recognition/recognize_face.py`**: abre a webcam, detecta rostos
  continuamente e compara com os embeddings salvos no banco, exibindo o nome ou
  "Nao cadastrado".

- **`services/user_service.py`**: valida os dados (e-mail válido, não duplicado,
  campos obrigatórios) antes de gravar no banco.

## Instalação

### 1. Pré-requisitos do sistema

A biblioteca `face_recognition` depende do `dlib`, que precisa compilar código C++.
Instale antes:

**Windows:**
- Instale o [CMake](https://cmake.org/download/)
- Instale o "Visual Studio Build Tools" (workload "Desktop development with C++")

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y build-essential cmake libopenblas-dev liblapack-dev libx11-dev
```

**macOS:**
```bash
brew install cmake
```

### 2. Ambiente virtual Python (recomendado)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

> Se a instalação do `dlib`/`face_recognition` falhar no Windows, uma alternativa
> mais simples é instalar via conda: `conda install -c conda-forge dlib` e depois
> `pip install face_recognition`.

## Como executar

```bash
python main.py
```

Isso abrirá a interface gráfica e criará automaticamente o banco SQLite em
`data/app.db` na primeira execução.

## Como testar o cadastro facial

1. Preencha nome, e-mail e senha (mínimo 6 caracteres).
2. Clique em **"1) Iniciar Cadastro Facial"**.
3. Uma janela da webcam abrirá. Posicione seu rosto e pressione **ESPAÇO** 5 vezes
   (varie levemente o ângulo do rosto a cada captura para maior robustez).
4. A janela fecha automaticamente após as 5 capturas. O rótulo na tela deve mudar
   para "Rosto capturado com sucesso!" em verde.
5. Clique em **"2) Finalizar Cadastro do Usuário"**. Você verá uma mensagem de
   sucesso, ou um erro caso o e-mail já exista ou algum campo esteja inválido.

## Como testar o reconhecimento facial

1. Cadastre pelo menos um usuário (passo acima).
2. Clique em **"Iniciar Reconhecimento em Tempo Real"**.
3. A webcam abrirá mostrando um retângulo ao redor de cada rosto detectado:
   - **Verde + nome**: rosto reconhecido como usuário cadastrado.
   - **Vermelho + "Nao cadastrado"**: rosto não corresponde a nenhum cadastro.
4. Pressione **ESC** para encerrar.

## Solução de problemas comuns na instalação (Windows)

- **Erro ao compilar `dlib` (CMake < 3.5 removido)**: não use `pip install dlib`
  nem `dlib-binary` diretamente. Baixe um wheel pré-compilado para sua versão do
  Python em https://github.com/z-mahmud22/Dlib_Windows_Python3.x e instale com
  `pip install caminho\para\o\arquivo.whl`.
- **`ModuleNotFoundError: No module named 'pkg_resources'`**: o
  `face_recognition_models` (dependência do `face_recognition`) ainda depende do
  módulo `pkg_resources`, removido pelo `setuptools` a partir da versão 82.
  Corrija com: `pip install "setuptools<81"`.
- **`Please install face_recognition_models...`**: geralmente é consequência do
  erro de `pkg_resources` acima. Resolva o `pkg_resources` primeiro.

## Migrando para PostgreSQL no futuro

1. Instale o driver: `pip install psycopg2-binary`
2. Defina a variável de ambiente antes de rodar o programa:
   ```bash
   export DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost:5432/facial_db"
   ```
3. Rode `python main.py` normalmente — as tabelas serão criadas no PostgreSQL
   automaticamente, sem alterar nenhum código do projeto.

## Segurança e privacidade (dados biométricos).

Este projeto trabalha com dados sensíveis (biometria facial) e senhas. Pontos
importantes já implementados e recomendações adicionais:

- **Senhas**: armazenadas apenas como hash bcrypt, nunca em texto puro.
- **Dados faciais**: armazenamos apenas o *embedding* (vetor matemático de 128
  números), não a imagem do rosto. Não é possível reconstruir uma foto
  reconhecível a partir desse vetor, mas ele ainda é um dado biométrico sensível
  e deve ser tratado como tal (ex.: LGPD/GDPR classificam biometria como dado
  sensível).
- **Consentimento**: em um sistema real, adicione uma tela de consentimento
  explícito antes da captura facial, explicando finalidade, prazo de retenção e
  como solicitar exclusão dos dados.
- **Banco de dados**: em produção, criptografe o arquivo/volume do banco em
  repouso e restrinja o acesso por permissões de sistema operacional/rede.
- **Transmissão**: se este sistema for exposto em rede (ex.: versão web futura),
  use HTTPS/TLS para proteger os dados em trânsito.
- **Exclusão de dados**: implemente uma função de exclusão de usuário (e seu
  embedding facial) para atender pedidos de remoção de dados.
- **Uso exclusivamente autorizado**: o sistema foi desenhado para cadastro
  voluntário do próprio usuário. Não o utilize para capturar rostos de terceiros
  sem consentimento explícito.

## Sugestões de melhorias futuras

- Adicionar tela de login com verificação de senha (`authentication/auth.py` já
  tem `verify_password` pronto para isso).
- Detecção de "vivacidade" (liveness detection) para evitar spoofing com fotos.
- Migrar a interface para Flask/FastAPI + frontend web com WebRTC, se o acesso
  remoto à webcam do cliente for necessário.
- Adicionar logs de auditoria (quem foi reconhecido, quando).
- Permitir múltiplos cadastros faciais por usuário (diferentes ângulos/óculos).
- Criptografar o campo `face_encoding` no banco antes de salvar.
- Implementar exclusão/atualização de cadastro (LGPD: direito de exclusão).
- Adicionar testes automatizados para `services/user_service.py` e `auth.py`.
