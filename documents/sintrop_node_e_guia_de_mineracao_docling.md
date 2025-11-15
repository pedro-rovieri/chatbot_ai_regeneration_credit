## SINTROP IMPACT BLOCKCHAIN

## Guia de mineração solo xecução de node da Sintrop

No Ubuntu

<!-- image -->

| Resources.................................................................................................................................................3           |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Sintrop core........................................................................................................................................................3 |
| Network status...................................................................................................................................................3    |
| Sintrop explorer.................................................................................................................................................4    |
| Hardware requirements......................................................................................................................... 5                      |
| Equipments........................................................................................................................................................ 5  |
| Basically assembly instructions.................................................................................................................... 6                 |
| Running a Sintrop Node......................................................................................................................... 7                     |
| Download GO-SINTROP................................................................................................................................. 7                |
| Run Sintrop.........................................................................................................................................................8 |
| Blockchain synchronization..........................................................................................................................10                |
| 12                                                                                                                                                                    |
| Mining with CPU....................................................................................................................................                   |
| Start mining with CPU.................................................................................................................................... 12          |
| Mining with GPU....................................................................................................................................13                 |
| Install appropriate drivers............................................................................................................................. 13           |
| Download a mining software....................................................................................................................... 14                  |
| Overclock the GPU.........................................................................................................................................15          |
| Start mining.......................................................................................................................................................16 |
| Troubleshooting.....................................................................................................................................18                |
| Peers connection lost.................................................................................................................................... 18          |
| Miner connection lost.................................................................................................................................... 19          |
| Head state missing........................................................................................................................................20          |
| No mining work available..............................................................................................................................21              |
| Energy source.........................................................................................................................................21              |
| 21                                                                                                                                                                    |
| The business model.......................................................................................................................................             |
| Step 1: Prepare the Installation Media......................................................................................................22                        |
| Option A: Raspberry Pi Imager (Windows, macOS, Linux)...........................................................22                                                    |
| Option C: Rufus (Windows Only).........................................................................................................23                             |
| Step 2: Boot From the USB Drive..............................................................................................................23                       |
| Step 3: Install Ubuntu....................................................................................................................................24          |
| Step-by-step instructions:.....................................................................................................................25                     |

## Recursos

Antes de começar o tutorial, aqui está uma lista de recursos úteis para nodes e mineradores.

## Sintrop core

Software central da blockchain Sintrop. Para acessá-lo, baixe a versão mais recente na página de recursos  do  site  ou  no  repositório  do  GitHub.  Este  é  o  aplicativo  principal,  onde  você  pode verificar  o  saldo,  enviar  transaçãoes  e  interagir  com  os  projetos  de  impacto  e  contratos inteligentes do sistema.

<!-- image -->

## Status da rede

Uma  página  de  status  da  rede,  onde  informaçãoes  úteis,  como  o  número  do  bloco,  últimos mineradores e outras informaçãoes podem ser encontradas.

<!-- image -->

## Sintrop explorer

Um explorador de blockchain simples para verificar saldo, blocos, contratos e transaçãoes. Ainda esta ém fase inicial de desenvolvimento, mas informaçãoes úteis, como o saldo da sua carteira, podem ser encontradas.

<!-- image -->

## Requisitos de hardware

Um computador simples é necessário para executar um nó e iniciar a mineração. É possível usar o  computador  junto  com  o  nó,  mas  uma  máquina  dedicada  é  recomendada.  Abaixo,  você encontrará uma lista dos componentes de hardware essenciais que você precisará, juntamente com uma breve explicação e instruçãoes básicas de montagem.

## Equipamentos

Fonte de energia (PSU): Este é o coração do seu equipamento, fornecendo energia para todos os componentes. Para mineração, você precisará de uma fonte de alimentação confiável e de alta potência, normalmente 1000 W, se planeja usar várias GPUs, ou uma simples, se usar apenas uma GPU. Procure fontes de alimentação com alta classificação de eficiência (como 80 Plus Gold ou Platinum) para economizar nos custos de eletricidade.

Placa-mãe: A placa-mãe  é a  espinha  dorsal  do  seu  computador,  conectando  todos  os componentes.  Para  um  equipamento  de  mineração,  você  precisará  de  uma  placa-mãe  com vários  slots  PCIe  para  acomodar várias GPUs. Existem placas-mãe específicas para mineração, projetadas para essa finalidade. Ou você pode usar uma placa-mãe simples para minerar com apenas  uma  ou  duas  GPUs.  Você  também  pode  usar  conexões PCI estendidas ao usar uma placa-mãe simples.

Processador (CPU): Minerar com a CPU não faz o trabalho pesado; as GPUs fazem. Portanto, um processador  básico  e  moderno,  como  um  Intel  Core  i3  ou um AMD Ryzen 3, é mais do que suficiente. Você não precisa investir em uma CPU de ponta.

Memória Ram (RAM): Assim como a CPU, a RAM não é um componente crítico para o processo de  mineração  em  si.  Um  único  pente  de  8  GB  de  RAM  DDR4  geralmente  é  suficiente  para executar o sistema operacional software de mineração sem problemas.

Placa de vídeo (GPU): Este  é  o  componente mais crucial para a mineração. A GPU realiza os cálculos  complexos  necessários  para  minerar  novos  blocos.  Para  a  blockchain  Sintrop,  você precisará de uma GPU com uma boa quantidade de VRAM (pelo menos 6 a 8 GB) e uma alta taxa de hash. Escolhas populares incluem as séries GeForce RTX 30 e 40 da NVIDIA. Você pode usar qualquer  GPU  para  minerar,  mas  quanto  maior  a  taxa  de  hash  da  placa,  maior  a  chance de encontrar blocos e ser recompensado.

Armazenamento (SSD): Você precisará de um disco rígido para instalar o sistema operacional software de mineração. Recomenda-se um pequeno SSD (Solid State Drive) de 120 a 240 GB para começar. O blockchain crescerá com o tempo, portanto, no futuro, poderá ser necessário ter SSDs maiores para armazenar a cópia completa do blockchain.

## Instruçãoes de montagem

## 1. Prepare a placa mãe:

- Desembale  cuidadosamente  a  placa-mãe  e  coloque-a  em  sua  embalagem antiestática sobre uma superfície plana e não metálica.
- Abra lavanca  do  soquete  da  CPU, encaixe a CPU com cuidado no soquete (alinhando os triângulos da CPU e do soquete) e feche lavanca para fixá-la.
- Instale o(s) pente(s) de RAM nos slots de RAM. Eles se encaixam no lugar com um clique quando inseridos corretamente.
2. Instale a placa mãe:
- Se  você  estiver  usando  um  gabinete  ou  estrutura  de  mineração,  parafuse  a placa-mãe nos espaçadores designados.

## 3. Instale as placas de vídeo:

- Se você estiver usando cabos riser PCIe (comuns em plataformas de mineração), conecte uma extremidade a um slot PCIe na placa-mãe e a outra à sua GPU.
- Prenda as GPUs à estrutura de mineração, deixando espaço suficiente entre elas para um fluxo de ar adequado.
4. Conecte a fonte de energia (PSU):
- Conecte o cabo de alimentação principal de 24 pinos da placa-mãe cabo de alimentação de 8 pinos da CPU da fonte de alimentação à placa-mãe.
- Conecte  os  cabos  de  alimentação  PCIe  da  fonte  de  alimentação  a cada GPU. Cada GPU provavelmente precisará de um ou dois conectores de alimentação de 6+2 pinos.
- Conecte limentação à sua unidade de armazenamento.

## 5. Conexões finais:

- Conecte sua unidade de armazenamento a uma porta SATA na placa-mãe.
- Conecte um monitor, teclado e mouse para a configuração inicial.

Depois  que  todos  os  componentes  estiverem  conectados,  você  poderá  instalar  o  sistema operacional  de  sua  preferência.  Por  enquanto,  sugerimos  usar  o  Ubuntu  para  executar  seu próprio nó. É o sistema operacional mais adequado para executar um nó Sintrop.

<!-- image -->

Exemplo de configuração simples de computador com SSD, CPU, GPU, PSU e memória.

## Executando um node Sintrop

Guia  para  executar  um  nó  blockchain  completo  no  Ubuntu.  Para  isso,  você  precisa  baixar  o software  go-sintrop. Se precisar instalar o Ubuntu primeiro, confira as instruçãoes abaixo sobre como instalar o Ubuntu em um computador.

## Download GO-SINTROP

Baixe a versão mais recente do go-sintrop no repositório do projeto sintrop/go-sintrop.

## https://github.com/Sintrop/go-sintrop/releases

Clique na aba "Versões" para baixar a versão mais recente. Escolha o arquivo correto de acordo com o seu sistema operacional. No momento, a mineração solo funciona melhor no Ubuntu, mas sinta-se à vontade para experimentar outros sistemas operacionais.

<!-- image -->

<!-- image -->

## Executar o node Sintrop

Extraia o arquivo e acesse o caminho do projeto.

<!-- image -->

Abra  a  pasta  no  terminal.  Você  pode fazer isso clicando manualmente com o botão direito e abrindo-a diretamente, ou pode abrir um terminal xecutar o comando para acessar o caminho.

<!-- image -->

Você pode executar o comando para acessar a pasta diretamente do terminal. Exemplo: Se baixado da pasta Downloads:

cd Downloads/go-sintrop-alltools-linux-v1.0.0

<!-- image -->

Agora é hora de iniciar o nó. Antes disso, você precisa ter um endereço de carteira para receber a recompensa ao encontrar novos blocos. Caso não tenha, confira o tutorial sobre como criar um novo e insira o endereço da sua carteira no comando abaixo.

Troque miner.etherbase pelo endereço da sua carteira xecute o seguinte comando:

./geth  --identity  Sintrop  --datadir  ./sintrop\_node  --sintrop  --syncmode  "full"  --networkid  250225 --cache=1024 --port 25225  --http.vhosts=* --http.addr "0.0.0.0" --http.port 8545  --http=true --miner.threads=1 --miner.etherbase=0x0000000000000000000000000000000000000000 console

Não se esqueça de alterar o endereço da carteira (vermelho), este será o endereço da carteira que receberá a recompensa ao encontrar novos blocos.

Dica: Salve os comandos em um arquivo .txt no seu computador.

## Blockchain download e sincronização

Após iniciar o blockchain, ele deverá começar a sincronizar automaticamente com a rede.

<!-- image -->

<!-- image -->

<!-- image -->

## Como parar o node

Um passo muito importante é parar o nó corretamente quando você precisar desligá-lo. Para fazer isso, execute o comando no terminal do nó:

ctrl + d;

Com este comando, o nó deve parar sem problemas.

## Minerando com CPU

O software go-sintrop permite minerar diretamente com CPUs. É uma etapa necessária, mesmo que o minerador de nós planeje minerar com GPUs.

## Inicie a mineração com CPU

Para começar a minerar com sua CPU diretamente no go-sintrop, execute o seguinte comando no console geth:

miner.start()

Para interromper a mineração, execute o seguinte comando:

## miner.stop()

<!-- image -->

## Minerando com placa de vídeo (GPU)

Este guia explicará como minerar sintrop usando placas de vídeo.

## Instalar drivers apropriados

Para  minerar  com  placas  de  vídeo,  ou  GPUs,  primeiro  você  precisa instalar o hardware e os drivers. Essa é a mesma abordagem para usar a GPU para qualquer outro uso. Siga as instruçãoes da placa para instalar os drivers.

A  Nvidia  possui  o  software  de  configuração  do  servidor  NVIDIA  X  que  mostra  as  placas disponíveis.  Se  você  optou  por  instalar  os  drivers  ao  instalar  o  Ubuntu,  eles  deverão  ser instalados automaticamente. Caso contrário, você deve acessar o site e os tutoriais da empresa e seguir as instruçãoes de instalação.

<!-- image -->

Se a placa GPU aparecer no programa de configuraçãoes da Nvidia X, os drivers estão instalados corretamente e você está pronto para começar.

## Baixe um software de mineração

Para  minerar  com  GPU,  é necessário usar um software de mineração de terceiros. Há muitas opçãoes  disponíveis projeto  pretende  desenvolver  seu  próprio  software de mineração no futuro.  Para  este  tutorial,  usaremos  o  software  ethminer,  a  mesma  versão  antiga  usada  para minerar Ethereum nos primeiros dias.

Baixe a versão do software no repositório do GitHub:

https://github.com/ethereum-mining/ethminer

Extraia o arquivo e abra a pasta bin no terminal:

<!-- image -->

Se a placa GPU aparecer no programa de configuraçãoes da Nvidia X, os drivers estão instalados corretamente e você está pronto para começar.

## Overclock da GPU

É muito importante fazer overclock para otimizar as configuraçãoes da GPU. O mais importante é o limite  de  potência.  Cada  placa pode variar de uma potência mínima a uma máxima, que está relacionada  ao  consumo  de  energia.  Você  não  quer  desperdiçar  energia  sem  aumentar  a potência de hash.

Em placas Nvidia, execute o seguinte comando para definir o limite de potência mais próximo do valor  mínimo  e,  ao  iniciar  a  mineração,  altere  esse  valor  para  ver  o  impacto  na  taxa  de  hash. Dessa forma, você pode otimizar o consumo de energia. Por exemplo, usando a RTX 3070, o limite de potência ideal é próximo a 130 W. Se você definir um valor menor, a taxa de hash cairá. E se você aumentar o limite de potência, poderá não obter o mesmo aumento na taxa de hash.

Por exemplo, para definir uma placa Nvidia, na posição 0 (placa-mãe), para 130 W, você pode executar o seguinte comando:

sudo nvidia-smi -i 0 -pl 130

Ao executar um equipamento com vários cartões, altere o valor 0 para os outros IDs.

<!-- image -->

## Iniciar mineração com GPU

Na pasta bin, execute o seguinte comando para iniciar a mineração com GPU:

./ethminer -G -P http://localhost:8545

<!-- image -->

<!-- image -->

A probabilidade de encontrar novos blocos está relacionada à sua taxa de hash e à taxa de hash total da rede. Se você vir a mensagem "Mined potential block" no terminal do nó ou "Accepted" no terminal do software de mineração, você encontrou um bloco e receberá automaticamente a recompensa no endereço da sua carteira.

<!-- image -->

## Resolução de problemas

Infelizmente, muitos problemas são comuns ao executar um nó e minerar. Esta seção discutirá como resolver os mais comuns.

## Conexão de 'peers' perdida

Às  vezes,  o  nó  perde  as  conexões  com  os  pares,  o  que  pode  ser  observado  quando  a mensagem  "looking  for  peers"  é  exibida  com  peercount  =  0.  Este é um dos problemas mais comuns e geralmente está relacionado a problemas de conexão com a internet. Verifique sua conexão e seu provedor de internet se isso continuar acontecendo.

Para resolver este problema, pare o nó com o comando ctrl + d e reinicie-o. Ele deve se conectar aos pares e sincronizar com a rede. Basta parar o nó e reiniciá-lo; isso deve resolver o problema.

<!-- image -->

<!-- image -->

## Conexão perdida no minerador

Às  vezes,  o  minerador  perde  a  conexão  com  o  nó.  Isso  pode  acontecer por vários motivos, muitas vezes relacionados a problemas de conectividade. Para resolver esse problema, verifique se  o  seu  nó  está  funcionando  corretamente.  Caso  contrário,  reinicie-o.  Se  estiver,  reinicie  o minerador le deverá se conectar novamente.

Se o minerador perder a conexão, desligue-o e reinicie-o ou feche o terminal e reinicie tudo.

## Head state missing

'Head  state  missing,  repairing'.  Este  é  um  problema  muito  comum stá  relacionado  ao desligamento incorreto do nó. Se a energia cair repentinamente ou se você fechar o terminal do nó sem o comando "ctrl + d", isso geralmente acontece.

<!-- image -->

Para  resolver  este  problema,  é  necessária  uma  sincronização  completa  novamente.  Exclua  a pasta /sintrop-node e reinicie o sistema.

<!-- image -->

## No mining work available

Quando a mensagem 'No mining work available yet from localhost' aparece, o problema é que o nó local não esta énviando o trabalho ou o bloco para o minerador. Provavelmente, o nó parou de funcionar ou não está minerando com a CPU. Para resolver o problema, acesse o terminal do nó xecute o comando miner.start() e reinicie a mineração com GPU.

<!-- image -->

## Fonte de energia

Pela natureza do modelo de negócio, os mineradores são incentivados a buscar a energia mais barata  disponível,  que  frequentemente  vem  de  fontes  renováveis,  às  vezes  até  mesmo auto produzidas.  Incentivamos  nós  e  mineradores limentar  suas  máquinas  com  energia  solar, eólica,  hidrelétrica  e  outras  fontes  de  energia  renováveis  de  baixo  impacto.  Nosso  objetivo  é construir  uma  infraestrutura  de  blockchain  totalmente  alimentada por energia renovável. Para promover ainda mais a sustentabilidade, pretendemos desenvolver um aplicativo que recompense a produção de energia renovável.

## The business model

O modelo de negócios de mineração pode ser simplificado em:

## + Block reward - energy cost - hardware cost

O  custo  do  hardware  se  deve  ao  computador  e às GPUs, além da depreciação ao longo do tempo. Portanto, para aumentar o lucro, os mineradores devem encontrar a energia mais barata possível. A energia solar produzida por eles mesmos costuma ser a melhor opção.

## Apêndice 1: Installing Ubuntu

This guide will walk you through the simple process of installing Ubuntu on your computer.

## Step 1: Prepare the Installation Media

First, you'll need to create a bootable USB drive with the Ubuntu installation files.

1. Download Ubuntu: Go to the official Ubuntu website (https://ubuntu.com/download/desktop) and download the latest LTS (Long-Term Support) version for stability. This will download an ISO file.
2. Get a USB Drive: Y ou'll  need  a  USB  flash  drive with at least 8 GB of storage. Warning: This process will erase all data on the drive.
3. Create the Bootable Drive: Choose one of the following tools to create your bootable USB drive. All are excellent, reliable options.

## Option A: Raspberry Pi Imager (Windows, macOS, Linux)

Originally  made for Raspberry Pi, this tool is fantastic for creating any bootable USB drive. It's simple, safe, and works on all major operating systems.

1. Download and Install: Go  to the official Raspberry Pi website and download the Imager for your system. Install and open it.
2. Choose OS: Click "Choose OS" .  In the menu that appears, scroll down and select "Use custom" . Find and select the Ubuntu ISO file you downloaded.
3. Choose Storage: Click "Choose Storage" and select your USB drive from the list. Be very careful to select the correct drive.
4. Write: Click the "Write" button and confirm that you want to erase the data on the drive. Wait for the process to complete.

## Option B: Balena Etcher (Windows, macOS, Linux)

Balena Etcher is another excellent cross-platform tool, famous for its simple, three-step interface.

1. Download  and  Install: Go  to  the  Balena  Etcher  website  and  download the version for your operating system. Install and open it.
2. Select Image: Click on "Flash from file" and locate the Ubuntu ISO file you downloaded earlier.
3. Select Target: Click on "Select target" and choose your USB drive.
4. Flash: Click the "Flash!" button. It will take a few minutes to write the ISO to the drive and verify it.

## Option C: Rufus (Windows Only)

Rufus is a powerful and very popular tool for Windows users. It's fast and offers more advanced options (though the defaults are fine for installing Ubuntu).

1. Download and Run: Go to the Rufus website and download the latest version. Rufus is a portable application, so you can run it directly without installation.
2. Device: Open Rufus. It should automatically detect your USB drive under "Device".
3. Boot  Selection: Click  the "SELECT" button  and  choose  the  Ubuntu  ISO  file  you downloaded.
4. Settings: The other settings will usually be set automatically and correctly. You can leave them as they are.
5. Start: Click "START" .  A  pop-up  may  ask  about  the  mode  to  write  the  image  in;  the recommended "ISO Image mode" is fine. Click "OK" to begin.

## Step 2: Boot From the USB Drive

Now you need to tell the computer to start from the USB drive instead of its main hard drive.

1. Insert the USB Drive: Plug the bootable USB drive you just created into the computer you want to install Ubuntu on.
2. Enter the Boot Menu: Turn on the computer and immediately press the boot menu key . This key varies by manufacturer but is commonly F12 , F10 , F2 ,  or ESC .  Y ou  may see a message on the screen indicating the correct key.
3. Select the USB Drive: From the boot menu, use the arrow keys to select your USB drive and press Enter.

Insert the Ubuntu usb drive and start the computer

<!-- image -->

## Step 3: Install Ubuntu

The computer will now load the Ubuntu installer from the USB drive.

1. Try or Install: You will be greeted with a welcome screen. You can "Try Ubuntu" to test it out  without  making  any  changes,  or  you  can  click "Install  Ubuntu" to  begin  the installation.
2. Keyboard Layout: Select your preferred keyboard layout and click "Continue."
3. Updates and Software:
- Choose "Normal installation" for a full-featured desktop experience.
- It's a good idea to check the box for "Download updates while installing Ubuntu" and "Install  third-party  software  for  graphics  and  Wi-Fi  hardware" to  ensure everything works correctly after installation. Click "Continue."

## 4. Installation Type:

- Erase disk and install Ubuntu: This is the simplest option. It will delete everything on  your  computer's  hard  drive  (including  Windows or any other OS) and install Ubuntu. ⚠ Warning: This will erase all your files. Back up your data first.
- If you choose this option, just click "Install Now" and confirm the changes.
5. Location: Select your time zone on the map and click "Continue."
6. Create  Your  Account: Fill  in  your  name,  computer's  name,  a  username,  and  a  strong password. Click "Continue."
7. Installation: The installer will now copy the files to your hard drive. This may take a while, so feel free to grab a coffee ☕ .
8. Restart: Once  the  installation  is  complete,  you'll  be  prompted  to  restart  the  computer. Click "Restart Now" and remove the USB drive when asked.

Your computer will now boot into your new Ubuntu installation. Welcome to the world of Linux! Step-by-step instructions:

<!-- image -->

<!-- image -->

After the loading time, the installation guide screen will appear.

<!-- image -->

Follow the screen instructions to install.

<!-- image -->

It is highly recommended to install the drivers to avoid doing it manually later.

<!-- image -->

Review your choices and install Ubuntu.

Wait the installation time.

<!-- image -->

Ubuntu is ready. Restart the computer, remove the installation media.

<!-- image -->

<!-- image -->