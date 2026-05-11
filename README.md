# 💰 Personal Finance Tracker

Sistema de controle financeiro pessoal desenvolvido com **Python**, **Flask**, **SQLAlchemy**, **SQLite**, **PostgreSQL**, **Jinja2**, **CSS**, **Chart.js** e integração com aplicativo mobile em **React Native / Expo**.

O projeto permite organizar receitas e despesas, acompanhar saldo, visualizar gráficos, aplicar filtros avançados, registrar transações recorrentes, definir metas financeiras, receber alertas do mês, exportar dados em CSV, acessar uma conta demo para teste e consumir uma **API REST mobile** integrada a um app Android.

---

## 🔗 Acesse o projeto online

🌐 **Deploy web:** [https://personal-finance-tracker-wrlj.onrender.com](https://personal-finance-tracker-wrlj.onrender.com)

📱 **Repositório mobile:** [https://github.com/Eduardo-S-Balbino/personal-finance-tracker-mobile](https://github.com/Eduardo-S-Balbino/personal-finance-tracker-mobile)

---

## 📌 Sobre o projeto

O **Personal Finance Tracker** foi criado para ajudar usuários a registrarem e acompanharem suas movimentações financeiras de forma simples, clara e organizada.

A aplicação conta com autenticação de usuários, dashboard financeiro, CRUD completo de transações, filtros combinados, busca por título, recorrência mensal, exportação CSV, metas de economia, alertas financeiros e visualização gráfica dos dados.

Além da versão web, o projeto foi evoluído com uma **API REST mobile** consumida por um aplicativo Android desenvolvido com **React Native**, **Expo** e **TypeScript**. O app mobile se comunica com o backend Flask em produção, permitindo listar, criar, editar e excluir transações diretamente pelo celular.

Este projeto faz parte da construção do meu portfólio como desenvolvedor, demonstrando evolução em relação a projetos anteriores ao incluir regras de negócio mais completas, autenticação, banco de dados, dashboard analítico, API REST, integração mobile, deploy em produção e preocupação com responsividade.

---

## 🧱 Visão geral da solução

O projeto atualmente possui duas partes principais:

### 🖥️ Versão web

Aplicação Flask com interface renderizada por templates Jinja2, autenticação de usuários, dashboard financeiro, gráficos com Chart.js e gerenciamento completo de transações.

### 📱 Versão mobile

Aplicativo Android desenvolvido com React Native e Expo, consumindo endpoints REST do backend Flask em produção. A versão mobile possui dashboard financeiro, gráfico simples de despesas por categoria e CRUD completo de transações.

---

## 🚀 Funcionalidades

### 👤 Autenticação de usuários

- Cadastro de conta
- Login
- Logout
- Controle de sessão
- Proteção de rotas privadas
- Tratamento de sessão expirada
- Senhas armazenadas com hash

### 🧪 Usuário demo

O sistema possui uma opção de acesso rápido com usuário demo.

Com ela, é possível testar a aplicação sem criar uma conta manualmente.

### 💸 Gerenciamento de transações

- Adicionar transações
- Editar transações
- Excluir transações
- Listar transações
- Cadastro de receitas
- Cadastro de despesas
- Descrição opcional
- Categorias padronizadas
- Validação de campos obrigatórios

### ♻️ Recorrência mensal

As transações podem ser cadastradas como:

- Única
- Mensal

Transações mensais continuam sendo consideradas nos meses seguintes, permitindo simular receitas e despesas recorrentes como salário, aluguel, internet e assinaturas.

### 📊 Dashboard financeiro

O dashboard apresenta:

- Total de receitas
- Total de despesas
- Saldo final
- Taxa de economia
- Últimas transações
- Resumo financeiro do mês
- Maior categoria de gasto
- Gráfico de evolução mensal
- Gráfico de despesas por categoria

### 🎯 Metas financeiras

O usuário pode escolher uma meta de economia mensal:

- 10%
- 20%
- 30%

O sistema calcula o progresso da meta com base na taxa de economia do mês selecionado.

### ⚠️ Alertas inteligentes

O sistema exibe alertas quando identifica situações importantes, como:

- Gastos maiores que receitas
- Aumento de despesas em relação ao mês anterior
- Categoria concentrando grande parte dos gastos

### 🔎 Filtros e busca

#### No dashboard

- Filtro por mês
- Filtro por ano
- Filtro por tipo
- Filtro por categoria

#### Na página de transações

- Filtro por mês
- Filtro por ano
- Filtro por tipo
- Filtro por categoria
- Busca por título

### 📄 Exportação CSV

O usuário pode exportar as transações filtradas para um arquivo **CSV**.

A exportação respeita os filtros aplicados na tela de transações.

### 📱 Responsividade

A interface foi ajustada para diferentes tamanhos de tela, incluindo desktop e mobile.

Foram feitos ajustes específicos para:

- navegação em telas menores;
- cards do dashboard;
- tabelas com rolagem horizontal;
- gráficos responsivos;
- exibição dos meses no gráfico de evolução mensal.

### 📲 API REST para aplicativo mobile

O backend Flask também disponibiliza endpoints em JSON para consumo por aplicativo mobile.

A API permite:

- carregar dados do dashboard mobile;
- listar transações;
- criar transações;
- editar transações;
- excluir transações;
- retornar dados formatados para visualização no app.

---

## 📱 Aplicativo mobile Android

O projeto possui um app mobile separado desenvolvido com **React Native**, **Expo**, **Expo Router** e **TypeScript**.

O aplicativo consome o backend Flask publicado no Render e permite utilizar o sistema pelo celular.

### Funcionalidades do app mobile

- Dashboard mobile.
- Cards de saldo, receitas e despesas.
- Indicadores financeiros.
- Progresso da meta de economia.
- Alerta financeiro.
- Gráfico simples de despesas por categoria.
- Listagem de transações recentes.
- Listagem completa de transações.
- Criação de transações.
- Edição de transações.
- Exclusão de transações.
- Integração com API REST em produção.
- APK Android gerado com EAS Build.

### Repositório mobile

```text
https://github.com/Eduardo-S-Balbino/personal-finance-tracker-mobile
```

---

## 🔌 Endpoints mobile

Principais endpoints utilizados pelo aplicativo mobile:

```text
GET    /api/mobile/demo-dashboard
GET    /api/mobile/transactions
POST   /api/mobile/transactions
PUT    /api/mobile/transactions/<id>
DELETE /api/mobile/transactions/<id>
```

### Exemplo de resposta do dashboard mobile

```json
{
  "status": "ok",
  "summary": {
    "balance": 2530.0,
    "total_income": 4300.0,
    "total_expense": 1770.0,
    "savings_rate": 58.8,
    "top_category": "Moradia"
  },
  "alerts": [
    "A categoria 'Moradia' representa 67.8% dos seus gastos."
  ],
  "recent_transactions": []
}
```

---

## 🛠️ Tecnologias utilizadas

### Backend / Web

- **Python**
- **Flask**
- **Flask-SQLAlchemy**
- **SQLAlchemy**
- **SQLite**
- **PostgreSQL**
- **HTML5**
- **CSS3**
- **Jinja2**
- **JavaScript**
- **Chart.js**
- **Gunicorn**
- **Render**

### Mobile

- **React Native**
- **Expo**
- **Expo Router**
- **TypeScript**
- **EAS Build**
- **Android APK**
- **API REST**

### Ferramentas

- **Git**
- **GitHub**
- **VS Code**
- **PowerShell**
- **Render**
- **Expo Go**

---

## 📂 Estrutura do projeto web

```text
personal-finance-tracker/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│   ├── 1-home.png
│   ├── 2-dashboard-summary.png
│   ├── 3-dashboard-summary.png
│   ├── 4-dashboard-chart.png
│   ├── 5-dashboard-chart.png
│   ├── 6-transactions.png
│   └── 7-transactions.png
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   ├── edit_transaction.html
│   └── transactions.html
│
└── static/
    └── style.css
```

---

## 📂 Estrutura do projeto mobile

```text
personal-finance-tracker-mobile/
│
├── app/
│   ├── (tabs)/
│   │   ├── index.tsx       # Dashboard mobile
│   │   ├── explore.tsx     # Tela de transações com CRUD
│   │   └── _layout.tsx     # Navegação por abas
│   │
│   ├── _layout.tsx
│   └── modal.tsx
│
├── assets/
│   └── images/
│
├── components/
├── constants/
├── hooks/
├── app.json
├── eas.json
├── package.json
├── package-lock.json
└── README.md
```

---

## ▶️ Como executar o projeto web localmente

### 1. Clone o repositório

```bash
git clone https://github.com/Eduardo-S-Balbino/personal-finance-tracker.git
```

### 2. Entre na pasta do projeto

```bash
cd personal-finance-tracker
```

### 3. Crie um ambiente virtual

```bash
python -m venv venv
```

### 4. Ative o ambiente virtual

No Windows:

```bash
venv\Scripts\activate
```

No Linux/Mac:

```bash
source venv/bin/activate
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

### 6. Execute a aplicação

```bash
python app.py
```

### 7. Abra no navegador

```text
http://127.0.0.1:5000
```

---

## ▶️ Como executar o app mobile localmente

### 1. Clone o repositório mobile

```bash
git clone https://github.com/Eduardo-S-Balbino/personal-finance-tracker-mobile.git
```

### 2. Acesse a pasta

```bash
cd personal-finance-tracker-mobile
```

### 3. Instale as dependências

```bash
npm install
```

### 4. Execute com Expo

```bash
npx expo start
```

### 5. Teste no celular

1. Instale o aplicativo **Expo Go** no celular.
2. Escaneie o QR Code exibido no terminal.
3. Teste as telas de Dashboard e Transações.

> O computador e o celular precisam estar conectados à mesma rede Wi-Fi.

### 6. Teste no navegador

```bash
npm run web
```

ou:

```bash
npx expo start --web
```

---

## 📦 Build Android com EAS

O app mobile está configurado para geração de APK Android usando **EAS Build**.

### Configurar EAS

```bash
eas build:configure
```

### Gerar APK de preview

```bash
eas build -p android --profile preview
```

Após a finalização do build, o Expo fornece um link/QR Code para baixar e instalar o APK no Android.

---

## 🌐 Deploy

O projeto web foi publicado no **Render**.

Em desenvolvimento local, a aplicação utiliza **SQLite**.

Em produção, a aplicação pode utilizar **PostgreSQL** por meio da variável de ambiente `DATABASE_URL`.

Comando de inicialização usado em produção:

```bash
gunicorn app:app
```

---

## 📸 Telas do sistema

O sistema possui as seguintes telas principais:

- Login
- Acesso demo
- Dashboard financeiro
- Meta financeira
- Gráficos financeiros
- Últimas transações
- Lista de transações
- Filtros avançados
- Exportação CSV
- Dashboard mobile
- CRUD mobile de transações
- Gráfico mobile por categoria

---

## 📸 Preview

### Login e acesso demo

![Login e acesso demo](assets/1-home.png)

### Dashboard - Resumo inicial

![Dashboard - Resumo inicial](assets/2-dashboard-summary.png)

### Dashboard - Meta financeira e indicadores

![Dashboard - Meta financeira e indicadores](assets/3-dashboard-summary.png)

### Dashboard - Gráficos financeiros

![Dashboard - Gráficos financeiros](assets/4-dashboard-chart.png)

### Dashboard - Últimas transações

![Dashboard - Últimas transações](assets/5-dashboard-chart.png)

### Transações - Filtros e exportação

![Transações - Filtros e exportação](assets/6-transactions.png)

### Transações - Lista completa

![Transações - Lista completa](assets/7-transactions.png)

---

## 📈 Exemplo de uso

Um usuário pode:

1. Criar uma conta ou entrar como usuário demo.
2. Fazer login no sistema web.
3. Cadastrar receitas e despesas.
4. Definir transações como únicas ou mensais.
5. Visualizar receitas, despesas, saldo e taxa de economia no dashboard.
6. Acompanhar a evolução mensal por gráfico.
7. Ver despesas agrupadas por categoria.
8. Definir uma meta de economia mensal.
9. Receber alertas financeiros automáticos.
10. Aplicar filtros por mês, ano, tipo e categoria.
11. Buscar transações por título.
12. Navegar entre páginas da listagem.
13. Exportar as transações filtradas em CSV.
14. Consumir os dados pela API mobile.
15. Criar, editar e excluir transações pelo aplicativo Android.
16. Atualizar o dashboard mobile com os dados do backend em produção.

---

## 🧠 Regras de negócio implementadas

- Cada usuário visualiza apenas as próprias transações.
- Rotas privadas exigem login.
- Senhas são armazenadas com hash.
- Sessões inválidas ou expiradas são tratadas sem quebrar a aplicação.
- Transações recorrentes mensais continuam impactando meses futuros.
- O dashboard recalcula os valores com base nos filtros selecionados.
- A taxa de economia é calculada com base em receitas, despesas e saldo.
- A meta financeira compara o percentual economizado com o objetivo escolhido.
- Os alertas são gerados com base no comportamento financeiro do mês.
- O gráfico de categorias considera apenas despesas.
- O gráfico de evolução mensal compara receitas e despesas ao longo do ano.
- A exportação CSV respeita os filtros aplicados.
- A busca por título funciona em conjunto com os demais filtros.
- A paginação organiza os resultados sem perder os filtros aplicados.
- A API mobile retorna dados em JSON para integração com o aplicativo.
- O app mobile envia operações de criação, edição e exclusão para o backend em produção.

---

## ✅ Funcionalidades implementadas

- [x] Cadastro de usuário
- [x] Login e logout
- [x] Hash de senha
- [x] Usuário demo
- [x] Proteção de rotas
- [x] Tratamento de sessão expirada
- [x] CRUD completo de transações na web
- [x] Cadastro de receitas
- [x] Cadastro de despesas
- [x] Recorrência mensal
- [x] Dashboard financeiro
- [x] Total de receitas
- [x] Total de despesas
- [x] Saldo final
- [x] Taxa de economia
- [x] Meta financeira mensal
- [x] Alertas inteligentes
- [x] Gráfico de evolução mensal
- [x] Gráfico de despesas por categoria
- [x] Filtro por mês e ano
- [x] Filtro por tipo
- [x] Filtro por categoria
- [x] Busca por título
- [x] Exportação CSV
- [x] Paginação
- [x] Categorias padronizadas
- [x] Responsividade mobile
- [x] Deploy em produção no Render
- [x] API REST para app mobile
- [x] App mobile com React Native e Expo
- [x] Dashboard mobile
- [x] Gráfico mobile de despesas por categoria
- [x] CRUD completo de transações no app mobile
- [x] APK Android gerado com EAS Build

---

## 🧪 Testes realizados

Foram realizados testes manuais na versão web, na API mobile, no navegador, no Expo Go e no APK Android.

Validações realizadas:

- Login e acesso demo.
- Cadastro de transações.
- Edição de transações.
- Exclusão de transações.
- Filtros do dashboard.
- Filtros da tela de transações.
- Exportação CSV.
- Carregamento dos gráficos.
- Consumo dos endpoints mobile.
- Criação de transação via API.
- Edição de transação via API.
- Exclusão de transação via API.
- Integração do app mobile com backend em produção.
- Instalação e execução do APK em celular Android.
- Atualização do dashboard mobile após mudanças nas transações.

---

## 🔮 Melhorias futuras

Algumas melhorias que podem ser adicionadas futuramente:

- Recuperação de senha
- Filtro por intervalo de datas
- Mais tipos de recorrência
- Edição de categorias personalizadas
- Relatórios financeiros mais avançados
- Comparativo entre períodos
- Tema escuro
- Testes automatizados
- Melhorias adicionais de acessibilidade
- Autenticação completa no app mobile
- Login e cadastro no app mobile
- Publicação do app em loja de aplicativos
- Notificações e lembretes financeiros

---

## 📚 Aprendizados com este projeto

Durante o desenvolvimento deste sistema, pratiquei e consolidei conhecimentos em:

- estruturação de aplicações Flask;
- criação de rotas e templates com Jinja2;
- integração com banco de dados usando SQLAlchemy;
- autenticação e controle de sessão;
- proteção de rotas privadas;
- validação de formulários;
- implementação de regras de negócio;
- manipulação de filtros no backend;
- cálculo de indicadores financeiros;
- criação de dashboards;
- uso de gráficos com Chart.js;
- exportação de dados em CSV;
- responsividade com CSS;
- deploy de aplicação Flask no Render;
- criação de endpoints REST para consumo mobile;
- integração entre backend Flask e app React Native;
- envio de requisições GET, POST, PUT e DELETE;
- geração de APK Android com EAS Build;
- organização de projeto para portfólio.

---

## 🎯 Objetivo profissional

Este projeto faz parte do meu processo de evolução como desenvolvedor, com foco em construir aplicações web e mobile cada vez mais completas, organizadas e próximas de cenários reais de uso.

A proposta foi ir além de um CRUD simples, adicionando autenticação, dashboard, recorrência, filtros avançados, exportação, metas financeiras, alertas automáticos, responsividade, API REST, integração mobile e deploy em produção.

---

## 👨‍💻 Autor

**Eduardo da Silva Balbino**

- GitHub: [Eduardo-S-Balbino](https://github.com/Eduardo-S-Balbino)
- LinkedIn: [eduardo-da-silva-balbino-1611b3401](https://www.linkedin.com/in/eduardo-da-silva-balbino-1611b3401/)
- Portfólio: [portfolio-ekgq.onrender.com](https://portfolio-ekgq.onrender.com/)

---

## 📄 Licença

Este projeto foi desenvolvido para fins de estudo, prática e portfólio.
