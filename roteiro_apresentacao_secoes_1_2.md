# Roteiro de Apresentação — Seções 1 e 2 (Teóricas)

**Disciplina:** SSC0900 — Engenharia de Segurança
**Tema:** Pentest da CVE-2007-2447 (Samba `username map script`)
**Escopo deste roteiro:** falas das partes teóricas (Seção 1 — Introdução e Contexto Ético;
Seção 2 — Fundamentação Teórica). As gravações de execução entram na edição.

> Este roteiro é uma versão **expandida e pronta para falar** das Seções 1 e 2 do
> `roteiro_video.md`, com mais detalhe sobre o **Samba**, sobre o **Metasploit** e sobre as
> **razões de escolher tanto a vulnerabilidade quanto a ferramenta**.

---

## SEÇÃO 1 — Introdução e Contexto Ético
**Tempo estimado:** 0–2 min · **Responsável:** Integrante 1

### 1.1 — O que é um pentest

> "Antes de falar da vulnerabilidade em si, vale explicar o que é um pentest. Pentest, ou
> *penetration test*, é um processo **metodológico e autorizado** de avaliação de segurança
> que simula o comportamento de um atacante real. A diferença para um ataque malicioso está
> em três pontos: o pentest tem **escopo definido**, tem **autorização formal** e tem um
> **propósito construtivo** — encontrar as vulnerabilidades antes que alguém mal-intencionado
> as encontre. Ele segue fases clássicas: **reconhecimento, enumeração, exploração,
> pós-exploração e relatório**. Neste trabalho vamos passar por todas elas, com foco na
> exploração e na defesa."

### 1.2 — Ética e escopo deste trabalho

> "Sobre a ética: todo o experimento aconteceu em um ambiente **100% local e isolado**.
> Criamos uma rede Docker exclusiva para o laboratório, **sem nenhuma conexão com redes
> externas**. O alvo foi um container `metasploitable2`, que é uma imagem
> **propositalmente vulnerável**, feita justamente para fins educacionais. Ou seja: não
> houve ataque a sistemas de terceiros, não houve coleta de dados reais, não houve
> persistência, movimentação lateral nem exfiltração. O objetivo foi **estritamente didático
> e defensivo** — entender a falha para saber defender."

### 1.3 — Por que este tema (a vulnerabilidade) e por que o Metasploit (a ferramenta)

> "Por que escolhemos justamente essa vulnerabilidade? No processo de escolha, avaliamos
> **três candidatas**: o *backdoor do vsftpd*, o *upload de WAR malicioso no Tomcat* e a
> *CVE-2007-2447 do Samba*. Ficamos com a do Samba porque ela reúne as melhores
> características didáticas:
>
> - **Não depende de senha** — é uma falha de *pré-autenticação*, então o ataque não se
>   confunde com 'senha fraca';
> - tem uma **causa técnica clara e explicável** — dá para mostrar exatamente *por que* a
>   falha existe, linha a linha;
> - usa o **Metasploit como ferramenta central**, que é o framework padrão de mercado para
>   pentest; e
> - permite uma **defesa prática que mantém o serviço ativo** — conseguimos corrigir a falha
>   sem desligar o Samba, o que é o cenário realista de produção."

> "E por que o Metasploit? Porque ele é a ferramenta de referência para esse tipo de
> demonstração. Em vez de escrever o código de ataque do zero, o Metasploit já organiza
> centenas de exploits em **módulos padronizados** — a gente seleciona o módulo, configura o
> alvo e executa. Isso deixa o ataque **reproduzível**: qualquer pessoa roda os mesmos
> comandos e chega ao mesmo resultado. Para uma apresentação, isso é ideal, porque foca a
> atenção na *vulnerabilidade* e não em detalhes de programação. Vamos detalhar o Metasploit
> mais à frente, na fundamentação."

---

## SEÇÃO 2 — Fundamentação Teórica: Samba, SMB e a Vulnerabilidade
**Tempo estimado:** 2–8 min · **Responsável:** Integrante 2

### 2.1 — O que é o Samba (o software)

> "Vamos começar pelo alvo. O **Samba** é um software **livre, de código aberto**, que
> implementa em Linux/Unix os protocolos **SMB** (*Server Message Block*) e **CIFS**
> (*Common Internet File System*) — os mesmos protocolos que o Windows usa para
> compartilhamento em rede. Na prática, o Samba funciona como uma **ponte de
> interoperabilidade**: ele faz uma máquina Linux 'falar a língua' das redes Windows."

> "Com o Samba, um servidor Linux consegue:
> - **compartilhar pastas e arquivos** com máquinas Windows na mesma rede;
> - **compartilhar impressoras**;
> - **aparecer na rede** como se fosse um servidor de arquivos Windows; e
> - em configurações mais avançadas, até atuar como **controlador de domínio**, fazendo
>   autenticação de usuários no estilo Active Directory.
>
> Por isso ele é **extremamente comum em redes corporativas** — e é justamente essa
> onipresença que torna uma falha no Samba tão crítica."

> "Detalhes técnicos importantes: o processo principal do Samba — o *daemon* — chama-se
> **`smbd`**, e é ele quem atende as conexões. O serviço escuta em duas portas:
> **TCP/139**, do antigo NetBIOS Session Service, e **TCP/445**, que é o SMB direto sobre
> TCP. Guardem o `smbd`, porque ele vai ser o centro da história."

### 2.2 — A diretiva `username map script` (a origem do problema)

> "A vulnerabilidade não está no protocolo SMB em si, e sim em uma **opção de configuração**
> do Samba, no arquivo `smb.conf`: a diretiva **`username map script`**.
>
> O que essa diretiva faz? Ela permite que o administrador **delegue a um script externo** a
> tarefa de mapear nomes de usuário. Funciona assim: o cliente SMB envia um nome de usuário,
> o Samba chama esse script passando o nome como entrada, e o script devolve o nome de
> usuário local correspondente. A intenção original era boa — dar **flexibilidade
> administrativa** para traduzir nomes."

> "O problema é conceitual e grave: **o nome de usuário é uma entrada controlada pelo
> cliente** — ou seja, controlada por quem está do outro lado, possivelmente um atacante. E
> esse nome chegava ao script **sem sanitização adequada**. Quando o Samba montava a linha de
> comando para chamar o script, **metacaracteres de shell** que estivessem no nome de usuário
> podiam ser interpretados pelo interpretador de comandos. Em outras palavras: dava para
> esconder um comando dentro de um 'nome de usuário'."

### 2.3 — CVE-2007-2447: o fluxo da exploração

> "Juntando tudo, o fluxo da exploração tem cinco passos:
>
> 1. O cliente SMB inicia a sessão e fornece um **nome de usuário** na mensagem
>    *Session Setup AndX Request*.
> 2. Com o `username map script` ativo, o Samba **invoca o script externo** passando esse nome.
> 3. A montagem da linha de comando **não sanitiza** os metacaracteres de shell.
> 4. Caracteres como os **acentos graves** ` `` ` fazem o shell **interpretar o conteúdo como
>    comando**, em vez de tratá-lo como texto.
> 5. Esse comando é executado no contexto do processo **`smbd` — que roda como `root`**."

> "Dois pontos tornam essa falha especialmente perigosa:
> - **Pré-autenticação:** o nome de usuário é processado *antes* da autenticação. O atacante
>   **não precisa de credencial nenhuma**. É isso que diferencia radicalmente essa falha de
>   um problema de 'senha fraca'.
> - **Execução como root:** como o `smbd` roda com privilégios máximos, o comando injetado
>   **herda esse contexto** — o que significa **impacto máximo** sobre o sistema."

### 2.4 — Metasploit: a ferramenta, o exploit e o payload

> "Agora que entendemos a falha, vale detalhar a ferramenta que usamos para explorá-la: o
> **Metasploit Framework**. Pensem nele como uma **caixa de ferramentas organizada de
> ataques prontos**. Em vez de escrever o código de exploração do zero, ele já traz centenas
> de exploits empacotados em **módulos padronizados**, que a gente seleciona e configura com
> poucos comandos. O fluxo típico é: escolher o módulo, definir o payload, apontar o alvo e
> mandar executar."

> "Para essa CVE existe um módulo específico: **`exploit/multi/samba/usermap_script`**, que
> **automatiza a injeção** no campo de nome de usuário. Dentro do Metasploit, dois conceitos
> são centrais e é importante diferenciá-los:
>
> - O **exploit** é a sequência que *aproveita a falha* — neste caso, a injeção no campo de
>   nome de usuário.
> - O **payload** é *o que acontece depois* que a falha é aberta. Neste trabalho usamos dois:
>   o `cmd/unix/generic`, que apenas executa **um comando único** na vítima, e o
>   `cmd/unix/bind_netcat`, que **abre uma porta de shell** na vítima, dando acesso
>   interativo."

> "Um detalhe que reforça a escolha: esse módulo tem **rank `excellent`** no Metasploit, que
> é a classificação de **altíssima confiabilidade** — ele funciona de forma consistente, sem
> risco de derrubar o serviço. Isso é mais um motivo de ele ser tão didático: o ataque é
> limpo, repetível e previsível."

> "(Transição para a parte prática:) Com a teoria coberta — o que é o Samba, onde está a
> falha, e o que é o Metasploit — partimos agora para a demonstração, começando pela
> preparação do ambiente isolado e pelo reconhecimento do alvo."

---

## Apêndice — Pontos de apoio rápido (para perguntas)

- **Samba ≠ SMB.** SMB/CIFS é o *protocolo*; Samba é a *implementação livre* desse protocolo
  em Linux/Unix.
- **Metasploit, não 'metaexploit'.** O nome vem de *meta* + *exploit*; é um *framework* de
  exploração.
- **"Defesa prática que mantém o serviço ativo"** = corrigir a *causa-raiz* (trocar o
  `username map script` por um `username map` estático) **sem desligar nem desinstalar o
  Samba**. O serviço continua no ar — portas 139/445 abertas e `smbd` rodando — mas o ataque
  deixa de funcionar.
- **Por que não é 'senha fraca'.** A falha ocorre *antes* da autenticação; o campo *Account*
  do pacote carrega um comando, não um nome — é *command injection*, não quebra de senha.
