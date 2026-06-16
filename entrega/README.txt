Trabalho Prático - Pentest (Engenharia de Segurança - SSC0900) 

CVE-2007-2447 (Samba)

Integrantes:
- Joao Pedro Alves Notari Godoy - 14582076
- Enzo Tonon Morente - 14568476
- Caue Paiva Lira - 14675416
- Pedro Henrique Ferreira Silva - 14677526

Video: https://youtu.be/huYP4KJ3Sw4?si=RltQfiimVdMxiRw2

Arquivos .rb (modulos nativos do Metasploit):
- usermap_script.rb: exploit da CVE-2007-2447, injeta comando no campo de nome de usuario do Samba (RCE como root).
- generic.rb: payload da prova de conceito, executa um unico comando no alvo.
- bind_netcat.rb: payload da pos-exploracao, abre um shell bind root na vitima.
