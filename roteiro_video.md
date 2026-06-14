# Roteiro do Vídeo — Pentest CVE-2007-2447 Samba

**Duração total:** ~20 minutos
**Formato:** Seções teóricas (explicação em voz + slides/tela) intercaladas com gravações de execução (terminal ao vivo).

> **Nota sobre as gravações de execução (EnzoTM):** cada gravação será feita separadamente e inserida pelo grupo na edição. O roteiro detalhado de fala para cada gravação será documentado em um arquivo separado (`roteiro_execucao_enzotm.md`). O que consta aqui é apenas a descrição do que será mostrado e o tom geral esperado.

---

## Seção 1 — Introdução e Contexto Ético
**Tipo:** Teórica
**Tempo estimado:** 0–2 min
**Responsável:** Integrante 1

### O que abordar:

**O que é pentest:**
Explicar que pentest (*penetration test*) é um processo metodológico e autorizado de avaliação de segurança que simula o comportamento de um atacante real. Diferentemente de um ataque malicioso, o pentest tem escopo definido, autorização formal e propósito construtivo: identificar vulnerabilidades antes que agentes mal-intencionados o façam. As fases clássicas são reconhecimento, enumeração, exploração, pós-exploração e relatório.

**Ética e escopo deste trabalho:**
Reforçar que todo o experimento ocorreu em ambiente 100% local e isolado — uma rede Docker criada exclusivamente para o laboratório, sem conexão com redes externas. O alvo foi um container `metasploitable2`, imagem propositalmente vulnerável criada para fins educacionais. Não houve ataque a sistemas de terceiros, coleta de dados reais, persistência, movimentação lateral nem exfiltração. O objetivo foi estritamente didático e defensivo.

**Por que este tema:**
Apresentar brevemente o processo de escolha: foram avaliadas três vulnerabilidades (vsftpd backdoor, Tomcat WAR upload e Samba CVE-2007-2447). A CVE-2007-2447 foi escolhida por reunir as melhores características didáticas — não depende de senha, tem causa técnica clara e explicável, usa o Metasploit como ferramenta central e permite uma defesa prática que mantém o serviço ativo.

---

## Seção 2 — Fundamentação Teórica: Samba, SMB e a Vulnerabilidade
**Tipo:** Teórica
**Tempo estimado:** 2–8 min
**Responsável:** Integrante 2

### O que abordar:

**Samba e o protocolo SMB/CIFS:**
Explicar que o Samba é uma implementação livre dos protocolos SMB (*Server Message Block*) e CIFS (*Common Internet File System*) para sistemas Unix/Linux. Ele permite que máquinas Linux compartilhem arquivos e impressoras com clientes Windows, funcionando como ponte de interoperabilidade. O daemon principal é o `smbd`. As portas associadas são TCP/139 (NetBIOS Session Service) e TCP/445 (SMB direto sobre TCP). Contextualizar que o SMB é amplamente usado em redes corporativas, o que torna falhas nesse serviço especialmente críticas.

**A diretiva `username map script` — origem do problema:**
Entrar em detalhes sobre o arquivo de configuração `smb.conf` e a opção `username map script`. Essa diretiva permite que o administrador delegue o mapeamento de nomes de usuário a um script externo: quando um cliente SMB fornece um nome de usuário, o Samba invoca esse script passando o nome como entrada, e o script retorna o nome de usuário local correspondente. A ideia original era oferecer flexibilidade administrativa. O problema está em que **o nome de usuário é uma entrada controlada pelo cliente** — e ele chegava ao script sem sanitização adequada. Quando o Samba montava a linha de comando para invocar o script, metacaracteres de shell presentes no nome de usuário podiam ser interpretados pelo interpretador de comandos.

**CVE-2007-2447 — análise técnica aprofundada:**
Detalhar o fluxo da exploração:
1. Cliente SMB inicia sessão e fornece um nome de usuário na mensagem *Session Setup AndX Request*.
2. Com `username map script` ativo, o Samba invoca o script externo passando esse nome.
3. A montagem da linha de comando não sanitiza metacaracteres de shell.
4. Caracteres como acentos graves (`` ` ``) fazem o shell interpretar o conteúdo como comando.
5. O comando é executado no contexto do processo `smbd` — que roda como `root`.

Destacar dois pontos críticos:
- **Pré-autenticação:** o nome de usuário é processado *antes* da autenticação. O atacante não precisa de credencial alguma. Isso diferencia radicalmente esta falha de "senha fraca".
- **Execução como root:** o `smbd` roda com privilégios máximos, então o comando injetado herda esse contexto — impacto máximo.

**Metasploit, exploit e payload — conceitos:**
Explicar o Metasploit Framework como plataforma que organiza, por módulos, a execução padronizada de exploits. O módulo `exploit/multi/samba/usermap_script` automatiza a injeção no campo de nome de usuário. Diferenciar:
- *Exploit*: a sequência que aproveita a falha (a injeção no campo de usuário).
- *Payload*: o que acontece depois — neste trabalho foram usados `cmd/unix/generic` (executa um comando único) e `cmd/unix/bind_netcat` (abre uma porta de shell na vítima).
- *Rank excellent*: indica altíssima confiabilidade do módulo.

---

## Gravação 1 — Ambiente Docker e Reconhecimento
**Tipo:** Execução
**Tempo estimado:** 8–11 min
**Responsável:** EnzoTM

### O que será mostrado:
- Criação da rede Docker isolada `pentest_lab`
- Inicialização do container vítima `metasploitable`
- Identificação do IP da vítima
- Varredura Nmap nas portas 139 e 445
- Entrada no container (`docker exec -it`)
- Verificação do processo `smbd` rodando como root
- Versão do Samba (`smbd -V`)
- Confirmação da configuração vulnerável (`grep username map script`)

### Tom esperado:
Explicar brevemente o que cada comando faz conforme executa. Não entrar em teoria profunda — isso já foi coberto. Exemplo: "aqui estou criando uma rede isolada para o laboratório", "o Nmap confirma as portas 139 e 445 abertas", "dentro do container, confirmo que o Samba está rodando como root e que a diretiva vulnerável está ativa".

> Roteiro detalhado de fala em `roteiro_execucao_enzotm.md`.

---

## Seção 3 — Análise da Vulnerabilidade (transição teoria → execução)
**Tipo:** Teórica
**Tempo estimado:** (dentro do bloco 2–8 min, ou breve pausa antes da Gravação 2)**
**Responsável:** Integrante 2

### O que abordar:
Antes de mostrar o exploit, reforçar o mecanismo com o diagrama:

```
Cliente SMB envia nome de usuário malformado
        ↓
Samba chama username map script com essa entrada
        ↓
Metacaracteres de shell são interpretados
        ↓
Comando executa como root na vítima
```

Ressaltar que o módulo do Metasploit vai injetar no campo *Account* do pacote *Session Setup AndX Request* — e que isso ficará visível na captura de pacotes (adiantando o que o Wireshark vai mostrar).

---

## Gravação 2 — Exploit: Prova de Conceito
**Tipo:** Execução
**Tempo estimado:** 11–13 min
**Responsável:** EnzoTM

### O que será mostrado:
- `msfconsole`
- `use exploit/multi/samba/usermap_script`
- `set payload cmd/unix/generic`
- `options` (mostrar as configurações)
- `set CMD touch /tmp/msf_samba_funcionou`
- `set RHOSTS 172.19.0.2` / `set RPORT 139`
- `run`
- No terminal do container: `ls -l /tmp/msf_samba_funcionou` (arquivo criado)

### Tom esperado:
"Agora vamos usar o Metasploit com o módulo específico para essa CVE. O payload genérico vai apenas executar um comando na vítima — o `touch` cria um arquivo vazio. Quando o arquivo aparecer dentro do container, provamos que o comando remoto foi executado."

> Roteiro detalhado de fala em `roteiro_execucao_enzotm.md`.

---

## Gravação 3 — Pós-exploração: Shell, Credenciais e Pacotes
**Tipo:** Execução
**Tempo estimado:** 13–16 min
**Responsável:** EnzoTM

### O que será mostrado:
**Terminal A (host):** `tcpdump` capturando tráfego SMB antes do ataque.

**Terminal B (host — msfconsole):**
- `set payload cmd/unix/bind_netcat` / `run`
- Shell aberto: `id` retorna `uid=0(root)`
- `cat /etc/passwd` — usuários do sistema
- `cat /etc/shadow` — hashes das senhas
- `exit`

**Terminal host:**
- `unshadow passwd.txt shadow.txt > unshadowed.txt`
- `john unshadowed.txt` / `john --show unshadowed.txt` — senhas quebradas

**Análise de pacotes:**
- `sudo tcpdump -r samba_attack.pcap -A | grep -i nohup` — injeção visível em texto
- `wireshark samba_attack.pcap` — mostrar campo *Account* com a injeção

### Tom esperado:
"Trocamos o payload para o `bind_netcat`, que abre uma porta na vítima e nos dá um shell interativo. Com esse shell como root, conseguimos ler o `/etc/shadow` — arquivo que guarda os hashes das senhas. O John the Ripper quebra as senhas fracas em segundos. No Wireshark, podemos ver que a injeção viajou literalmente dentro do campo de nome de usuário do pacote SMB — são esses acentos graves que fazem o shell interpretar o conteúdo como comando."

> Roteiro detalhado de fala em `roteiro_execucao_enzotm.md`.

---

## Seção 4 — Impacto CIA e Análise de Protocolo
**Tipo:** Teórica
**Tempo estimado:** (dentro do bloco 13–16 min, após a Gravação 3)
**Responsável:** Integrante 4

### O que abordar:

**Tríade CIA — impacto detalhado:**
- **Confidencialidade:** afetada diretamente — o atacante leu o `/etc/shadow` e obteve as senhas de todos os usuários sem nunca ter fornecido uma senha válida. Em um ambiente real, isso comprometeria todo o sistema de autenticação.
- **Integridade:** com acesso root, o atacante poderia alterar qualquer arquivo do sistema — configurações, binários, logs. Não realizado neste experimento, mas tecnicamente possível.
- **Disponibilidade:** com privilégios de root, seria possível parar serviços, corromper dados ou derrubar o sistema. Também não realizado.

**Por que não é "senha fraca":**
Aprofundar o argumento: a falha ocorre *antes* da autenticação. No fluxo SMB, o campo de nome de usuário é processado na negociação de sessão, antes de qualquer verificação de senha. A prova está no pacote Wireshark: o campo *Account* carrega o comando shell em vez de um nome — não há troca de senha em nenhum momento. A vulnerabilidade é de *injeção de comando* (*command injection*), uma falha de tratamento inseguro de entrada.

**Hashes MD5-crypt e por que senhas fracas caem rápido:**
Explicar que o Metasploitable2 usa `$1$` (MD5-crypt), algoritmo antigo e computacionalmente barato. O John the Ripper começa pelo *single crack mode* — testa o próprio nome de usuário como senha e variações. Contas como `msfadmin:msfadmin` caem instantaneamente. Contrastar com hashing moderno (`$6$` SHA-512 ou `$y$` yescrypt), onde cada tentativa é ordens de magnitude mais cara.

---

## Gravação 4 — Mitigação
**Tipo:** Execução
**Tempo estimado:** 16–18 min
**Responsável:** EnzoTM

### O que será mostrado:
- No terminal do container: `rm -f /tmp/msf_samba_funcionou` (limpeza)
- `cp /etc/samba/smb.conf /etc/samba/smb.conf.bak` (backup)
- `sed -i ...` (comentar a linha vulnerável)
- `cat > /etc/samba/smbusers` (criar mapeamento estático)
- `grep -q ... || echo ...` (adicionar `username map` estático)
- `grep -n "username map" /etc/samba/smb.conf` (confirmar mudança)
- `/etc/init.d/samba restart` (reiniciar)

### Tom esperado:
"A defesa não é desligar o Samba nem atualizar — é remover a causa-raiz. Comentamos a linha `username map script`, que era quem passava a entrada do cliente para o shell. No lugar, adicionamos um `username map` estático, que mapeia usuários por arquivo de texto fixo — sem invocar script externo, sem passar a entrada do cliente para o interpretador de comandos."

> Roteiro detalhado de fala em `roteiro_execucao_enzotm.md`.

---

## Gravação 5 — Validação da Defesa
**Tipo:** Execução
**Tempo estimado:** 18–20 min
**Responsável:** EnzoTM

### O que será mostrado:
- Repetir exploit com `cmd/unix/generic` → arquivo não criado
- No terminal do container: `ls -l /tmp/msf_samba_funcionou` → não existe
- Repetir com `cmd/unix/bind_netcat` → sem sessão
- `nmap -sV -p 139,445 172.19.0.2` → portas ainda abertas
- No terminal do container: `ps aux | grep smbd` → Samba ainda rodando

### Tom esperado:
"Repetimos o mesmo ataque, com o mesmo módulo e o mesmo alvo. O Metasploit diz que completou, mas o arquivo não foi criado. A tentativa de shell também não abre sessão. E o Samba continua ativo — as portas 139 e 445 estão abertas e o processo está rodando. A defesa funcionou sem tirar o serviço do ar."

> Roteiro detalhado de fala em `roteiro_execucao_enzotm.md`.

---

## Seção 5 — Defesa em Profundidade e Conclusão
**Tipo:** Teórica
**Tempo estimado:** (final — dentro do bloco 18–20 min, ou extensão se houver tempo)
**Responsável:** Integrante 4

### O que abordar:

**Por que a mitigação funcionou — mecanismo exato:**
A defesa não bloqueou o pacote SMB — como visto na análise de rede, o campo *Account* ainda carrega a injeção. O que mudou é que agora o Samba lê um arquivo estático de mapeamento em vez de invocar um script externo. A entrada do cliente nunca chega a um interpretador de comandos. É um exemplo claro de *eliminar a causa-raiz* em vez de contornar o sintoma.

**Defesa em profundidade — camadas adicionais:**
- **Política de senhas fortes:** senhas longas e aleatórias tornam a quebra computacionalmente inviável, mesmo que um hash vaze.
- **Hashing moderno:** substituir `$1$` (MD5) por `$6$` (SHA-512) ou `$y$` (yescrypt) aumenta o custo de cada tentativa de quebra em ordens de magnitude.
- **Princípio do menor privilégio:** se `smbd` não rodasse como root, o comando injetado não teria acesso ao `/etc/shadow`. O impacto foi amplificado pelo serviço rodar com privilégios máximos.
- **Restrição de rede:** `hosts allow`/`hosts deny` no `smb.conf` e regras de firewall limitam quem pode acessar as portas SMB.
- **Monitoramento e IDS:** a injeção é detectável no tráfego — nomes de usuário com metacaracteres de shell em pacotes SMB são assinatura de exploração.
- **Auditoria de configuração:** revisar periodicamente o `smb.conf` em busca de diretivas perigosas como scripts externos alimentados por entrada do cliente.

**Conclusão:**
Retomar a narrativa completa: entramos sem senha (CVE-2007-2447 é pré-autenticação), obtivemos root, lemos o `/etc/shadow`, quebramos as senhas, e mostramos tudo isso acontecendo dentro do pacote SMB. A defesa eliminou a causa-raiz mantendo o serviço ativo. Isso demonstra que segurança não é sobre desligar serviços, mas sobre entender e remover o que os torna exploráveis.

---

## Tabela Resumo das Gravações (EnzoTM)

| Gravação | Seções do relatório | Conteúdo principal | Tempo no vídeo |
|---|---|---|---|
| 1 | 8.1 – 8.8 | Ambiente Docker + reconhecimento | 8–11 min |
| 2 | 10.1 – 10.5 | Exploit prova de conceito | 11–13 min |
| 3 | 11.4 – 11.8 | Shell, credenciais, John, Wireshark | 13–16 min |
| 4 | 12.1 – 12.7 | Mitigação | 16–18 min |
| 5 | 13.1 – 13.4 | Validação da defesa | 18–20 min |
