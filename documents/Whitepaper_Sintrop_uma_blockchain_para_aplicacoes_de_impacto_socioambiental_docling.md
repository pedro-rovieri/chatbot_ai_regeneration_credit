## Sintrop: Uma Blockchain para Aplicaçãoes de Impacto Socioambiental

André O. Ravagnani 2 de outubro de 2025

## Resumo

A tecnologia da blockchain tem o potencial de impactar significativamente a luta contra as mudanças climáticas e problemas sociais da humanidade, muitas aplicaçãoes diferentes podem ser constrú ıdas com contratos inteligentes. O problema é que blockchains descentralizadas processam poucas transaçãoes por segundo, então projetos com impacto no mundo real precisam competir por transaçãoes com memecoins, NFTs e outros tokens especulativos e projetos de baixo valor. Essa competição aumenta as taxas de gas, limitando o número de modelos de negócios de impacto capazes de operar. O que é necessário é uma infraestrutura de blockchain descentralizada focada em aplicaçãoes que possam tornar o mundo melhor. Propomos uma blockchain pública de impacto, peer-to-peer, rodando com algoritmo de consenso proof-of-work com bjetivo de operar principalmente com energia renovável.

## 1 Por que outra blockchain?

Primeiramente, desenvolvemos o protocolo do Crédito de Regeneração[1], um sistema de financiamento peer-to-peer para incentivar a regeneração de ecossistemas terrestres. Em seguida, tivemos que escolher em qual blockchain lançar o projeto. Ethereum[2] foi nossa primeira opção, as primeiras versões de teste foram lançadas sobre testnets da EVM, a Ethereum Virtual Machine. Mas o Ether é caro. Isso aumenta a barreira financeira para doção da tecnologia pelos usuários, especialmente em aplicaçãoes mais complexas como o Crédito de Regeneração. Infelizmente, lançá-lo na Ethereum foi descartado. Então, recorremos a soluçãoes de segunda camada. O sistema de bridge requer a transferência de ativos de uma cadeia para outra, um passo adicional que é uma barreira para doção do usuário. Mas o maior problema das blockchains de segunda camada é a necessidade de confiança em grupos privados, o que vai contra o princípio fundamental da tecnologia blockchain. Qualquer outra solução que exigisse que o projeto dependesse de instituiçãoes centralizadas para existir, como blockchain-as-a-service, não era uma opção. Também poderíamos desenvolver uma appchain, ou uma blockchain privada, mas, novamente, isso seria contra o valor fundamental do Bitcoin[3]: a descentralização.

Muitas blockchains sacrificam a descentralização para ganhar escalabilidade, e alguns projetos de memecoins, tokens de baixo valor e NFTs vivem de forma especulativa sem agregar valor real ` a sociedade. Existe uma lacuna enorme para aplicaçãoes descentralizadas do mundo real com a intenção de tornar este mundo um lugar melhor. Para preenchê-la, decidimos criar outra rede: uma blockchain para aplicaçãoes de impacto socioambiental.

## 2 Impacto como valor fundamental

A tecnologia blockchain tem o potencial de resolver problemas que podem nos ajudar a combater as mudanças climáticas, a escassez de água, a poluição, a insegurança alimentar e muitas outras questões que nos colocam em risco de extinção de nossa espécie. Herdamos um Planeta com uma quantidade incrível de vida, composto por muitas espécies e funçãoes diferentes. Infelizmente, a humanidade vem destruindo a Natureza a um ritmo alarmante.

A entropia é a medida da desordem em um sistema, a perda de energia que gera um balanço energético negativo. Enquanto a sintropia é a medida da ordem em um sistema, o ganho de energia através de processos. Isso também pode ser traduzido em termos de vida: a entropia ocorre quando

reduzimos a quantidade de vida no Planeta, enquanto a sintropia[4] se refere ao processo de aumentar e complexificar a vida, o processo de evolução natural do Planeta, que tem sido revertido pela exploração massiva de recursos e pela destruição por parte dos seres humanos.

O impacto como valor fundamental refere-se a intenção de contribuir para o aumento da vida neste Planeta. Nosso objetivo é construir um sistema que fomente a vida na Terra através de aplicaçãoes que operem com contratos inteligentes.

Figura 1: Se analisarmos o número de organismos vivos como a soma de todas as espécies multiplicada pelo número de indivíduos vivos, vemos que esse número aumenta naturalmente ao longo do tempo é o processo natural da Terra. No entanto, ele está agora caindo exponencialmente devido ` a exploração humana. Nos últimos séculos, temos destrú ıdo o Planeta como se seus recursos fossem infinitos. Se continuarmos neste ritmo, estamos caminhando para uma extinção em massa global.

<!-- image -->

## 3 Descentralização como valor central

Em 2009, o Bitcoin[3] foi apresentado ao mundo. Uma tecnologia disruptiva que, pela primeira vez na história, possibilitou uma forma descentralizada de armazenar e transacionar valor entre duas partes sem a necessidade de confiar em uma autoridade central. O propósito principal desta tecnologia foi eliminar as autoridades centrais através da criação de uma rede (P2P) de computadores, onde cada nó armazena uma cópia do histórico de transaçãoes e é capaz de enviar e receber transaçãoes. O nível de descentralização é um espectro, não é um conceito binário de sim ou não. Alguns projetos podem ser mais ou menos descentralizados, sendo o Bitcoin o mais descentralizado de todos. Com o tempo, muitos projetos de blockchain têm priorizado a escalabilidade em detrimento da descentralização. Embora esse trade-off melhore as transaçãoes por segundo (TPS), uma grande limitação do Bitcoin[3] e do Ethereum[5], perde-se o propósito principal da tecnologia. A escalabilidade é definitivamente um grande problema, mas não deve ser obtida sacrificando a descentralização. Blockchains privadas ou permissionadas, onde apenas nós validadores limitados ou selecionados podem proteger a rede, são um bom exemplo desse trade-off .

Adescentralização como valor fundamental significa que compartilhamos a visão original do Bitcoin. A rede é aberta e transparente, qualquer pessoa com o hardware apropriado é bem-vinda para executar um nó e manter a rede. Além disso, a distribuição de tokens é um aspecto fundamental. A criptomoeda Sintrop, o token de utilidade nativo para gas fees do projeto, não será pré-minerada, sendo á unica forma de cunhar novos tokens com a recompensa por bloco ao encontrar novos blocos no sistema Proofof-Work (PoW). Em contratos inteligentes, desencorajamos o uso de contratos ownable em que um endereço de wallet owner específico possui funçãoes de privilégio. Quando tais funçãoes são necessárias para a implantação e configuração do contrato, a função renounceOwnership deve ser chamada para mantê-lo descentralizado.

## 4 Sintrop Virtual Machine

A rede consiste em um conjunto de peers composto por servidores, nós e mineradores. Juntos, eles compõem a SVM, a Sintrop Virtual Machine. Um servidor é um nó publicamente conhecido que pode aceitar novas conexões de peers . Nós são computadores que podem se conectar a servidores públicos, mas não podem receber conexões de outros nós. Tanto servidores quanto nós armazenam uma cópia completa do histórico de transaçãoes da blockchain. Mineradores são computadores que podem executar seus próprios nós, mas também podem minerar em nome de um servidor, contribuindo para o poder de hashing da rede sem precisar armazenar a blockchain completa. Quanto mais nós, servidores e mineradores a rede tiver, mais forte sua descentralização, segurança e resistência ` a censura.

Figura 2: Arquitetura da Sintrop Virtual Machine

<!-- image -->

## 5 Plataforma de contratos inteligentes

A Sintrop Virtual Machine é uma plataforma de smart contract que permite aos desenvolvedores implantar contratos com um conjunto pré-definido de funçãoes e variáveis. Uma vez implantado, um contrato sempre executará conforme programado, permitindo que wallets interajam com suas funçãoes pré-definidas sem a necessidade de uma autoridade central para definir as regras. O valor desta tecnologia é transferir a confiança de grupos centralizados para algoritmos distribuídos de código aberto. Com o tempo, as pessoas perceberão que faz muito mais sentido confiar em contratos inteligentes do que em pessoas.

Figura 3: Deployed smart contract

<!-- image -->

## 6 Por que prova de trabalho?

O consensus mechanism, algoritmo de consenso, é um componente crucial de qualquer blockchain. O Bitcoin introduziu o Proof-of-Work (PoW), um modelo de consenso onde mineradores usam hardware letricidade para competir na busca por blocos e proteger a rede. Posteriormente, alguns projetos adotaram o Proof-of-Stake (PoS), um mecanismo alternativo que depende das moedas do protocolo para validar blocos.

Ambas as abordagens têm seus prós e contras. A maior vantagem do PoS é seu baixo consumo de energia. Como a validação de blocos ocorre por meio de staking , ó unico hardware necessário é para a operação dos nós, sem lta demanda de energia da mineração PoW. No entanto, essa também é sua maior desvantagem. Quando uma rede é protegida por meio de staking, ela requer moedas prémineradas, que são então utilizadas para manter a segurança. Isso pode ser visto como controverso, já que se está criando um ativo e usando o mesmo ativo para validar transaçãoes. Nesse sentido, o PoS se assemelha aos sistemas fiat tradicionais, enquanto o PoW estabelece um sistema de dinheiro eletrônico distribuído e baseado em eletricidade[3]. Embora a mineração PoW possa levar ` a centralização com o desenvolvimento de hardware específico e a montagem em massa de equipamentos, ela é a forma mais justa de distribuição já implementada até hoje. Sem moedas pré-mineradas, apenas o trabalho para encontrar novos blocos.

Tabela 1: SINTROP recompensa por blocos

| Era   | Starts at block   | Block reward   |
|-------|-------------------|----------------|
| 1     | 1                 | 5              |
| 2     | 5.000.001         | 4              |
| 3     | 10.000.001        | 3,2            |
| 4     | 15.000.001        | 2,56           |
| ...   | ...               | ...            |

## 7 Energia Renovável

A necessidade de energia da humanidade tem tanto vantagens quanto desvantagens. Por um lado, reduzir o consumo beneficia o Planeta, já que toda fonte de energia, mesmo as renováveis, possui um impacto ambiental. Por outro lado, a energia impulsiona os avanços tecnológicos que melhoram nossas vidas de inúmeras maneiras. Embora todas as fontes de energia tenham algum impacto negativo, o caminho para um futuro limpo e tecnológico depende de energias renováveis, e devemos nos mover nessa direção. Os combustíveis fósseis são amplamente reconhecidos como um dos principais impulsionadores das mudanças climáticas, levando os críticos a culpar o Bitcoin e outras blockchains por seu alto consumo de energia. No entanto, essa questão se estende a quase todos os setores da economia que dependem de energia. A principal preocupação é de onde vem a energia.

Pela natureza de seu modelo de negócio, os mineradores são incentivizados a buscar a energia mais barata disponível, que frequentemente vem de fontes renováveis, ` as vezes até mesmo de produção própria. Nós incentivamos os nós e mineradores limentar suas máquinas usando fontes de energia solar, é olica, hídrica e outras fontes renováveis de baixo impacto. Nosso objetivo é construir uma infraestrutura de blockchain majoritariamente alimentada por energia renovável. Para promover ainda mais a sustentabilidade, poderá ser desenvolvida uma aplicação que recompense a produção de energia renovável.

Figura 4: Caminho da rede para fontes renováveis

<!-- image -->

## 8 Applications architecture

Em sua essência, uma aplicação consiste em um ou mais contratos inteligentes. Os nós podem interagir com eles diretamente usando a Interface de Linha de Comando (CLI) da blockchain. Embora o software CLI ofereça independência, ele é tecnicamente complexo e pouco amigável para usuários comuns.

Para melhorar cessibilidade, Interfaces Gráficas de Usuário (GUI) podem ser desenvolvidas, permitindo que os usuários interajam com os contratos por meio de um cliente que envia transaçãoes via um servidor RPC. Um cliente nativo opera sem serviços de terceiros. Por exemplo, exploradores de blocos auto-hospedados, que fornecem uma GUI integrada para ler screver nos contratos. As aplicaçãoes também podem desenvolver clientes personalizados para aprimorar a experiência do usuário. Desde que permaneçam de código aberto e livres de serviços centralizados, são considerados um cliente nativo. A camada central (core) e nativa juntas formam a camada resistente ` a censura, que é essencial para manter a descentralização.

Quanto menos serviços centralizados uma aplicação utiliza, mais forte é sua descentralização. No entanto, para aprimorar a experiência do usuário, algumas aplicaçãoes podem incorporar software de terceiros e bancos de dados privados para o armazenamento de dados de baixo valor, garantindo que as regras centrais e os dados de alto valor permaneçam on-chain. Serviços externos podem ser valiosos no processamento de informaçãoes complexas, embora introduzam centralização e dependência. Por exemplo, no Crédito de Regeneração, os contratos inteligentes gerenciam as regras e os dados centrais, enquanto um componente de software externo poderia ajudar os usuários valiar o impacto ambiental fornecendo imagens e dados de satélite.

Figura 5: Arquitetura das aplicaçãoes. O núcleo de uma aplicação é o conjunto de contratos inteligentes que compõem as regras. Clientes nativos fornecem uma interface gráfica sem software de terceiros. Softwares privados podem fornecer serviços e recursos na camada de terceiros.

<!-- image -->

## 8.1 App Store

Uma característica das blockchains públicas é que as pessoas podem desenvolver qualquer coisa sobre elas. E isso é ótimo, pois nos permite inovar sem censura. Mas há uma desvantagem: muitas aplicaçãoes competem por transaçãoes, aumentando as gas fees para realizar uma ação. Em outras palavras, um projeto do mundo real que agrega valor ` a Natureza e ` a sociedade tem que competir por transaçãoes com memecoins, NFTs e outras aplicaçãoes financeiras não tãó uteis. Um contrato inteligente de loja de aplicativos pode ser desenvolvido para permitir que os usuários votem se uma aplicação está gerando um impacto positivo ou não, o mesmo para o nível de descentralização. Apenas projetos aprovados pela comunidade serão listados na Sintrop App Store e recomendados aos usuários.

## 9 Limitaçãoes

A tecnologia possui algumas limitaçãoes, tanto no nível da blockchain quanto no dos contratos inteligentes. No nível da blockchain, as transaçãoes por segundo (TPS) da rede são uma limitação significativa. Projetos que requerem muitas transaçãoes para operar têm menor probabilidade de sucesso devido ` as altas gas fees cumulativas. Por exemplo, uma rede social totalmente descentralizada, onde postagens, curtidas e comentários exigem transaçãoes em um contrato inteligente, está longe de ser viável, porque os usuários teriam que pagar gas fees para cada interação. No nível dos contratos inteligentes, os contratos têm um tamanho de código limitado; aplicaçãoes de lógica complexa são difíceis de implementar e proteger. Os contratos também têm limitaçãoes em termos de código, sendo o solidity uma linguagem de programação com algumas restriçãoes.

## 10 Aplicaçãoes Possíveis

Fora as limitaçãoes, os contratos inteligentes são ilimitados. Muitas aplicaçãoes incríveis e diversas podem ser constrú ıdas com eles. Aplicaçãoes que podem mudar a forma como os humanos interagem uns com os outros e redefinir a sociedade - há muito potencial a ser explorado. É possível imaginar uma sociedade inteiramente nova governada por código imutável, em vez de pessoas defendendo seus próprios interesses. Podemos ter grupos e comunidades totalmente governados por contratos inteligentes, transferindo a confiança das pessoas para o código de fonte aberta.

Cabe ` a nossa imaginação criar soluçãoes para problemas do mundo real. A chave é o valor armazenado. Uma curtida em uma postagem, por exemplo, é uma transação de valor muito baixo. Uma transação de alto valor ocorre quando uma informação importante é armazenada, principalmente se forem dados de uso comum. Por exemplo, o Crédito de Regeneração armazena o impacto ecossistêmico de áreas regenerativas e seu impacto no carbono e na biodiversidade. Menos transaçãoes são necessárias, valor de cada uma é alto.

## 10.1 Crédito de Regeneração

A tecnologia blockchain trata da criação de incentivos econômicos, e uma forma de incentivo é reduzir a lacuna entre práticas sustentáveis e não sustentáveis, e usar isso para acelerar a transição. O Crédito de Regeneração é a razão da existência deste projeto. É um sistema de financiamento (P2P) projetado para incentivar a regeneração de ecossistemas. A humanidade vem destruindo a Natureza há séculos, e nossa sobrevivência depende de trazer a vida de volta. O problema é que as pessoas atualmente têm mais incentivos econômicos para desmatar uma área xplorar seus recursos naturais, como madeira, solo e água, do que para regenerá-la. Se, no futuro, gricultura regenerativa se tornar mais lucrativa que gricultura degenerativa, seria um grande passo para acelerar nossa transição para um mundo regenerativo. O projeto visa criar uma renda adicional para pessoas que estão regenerando ecossistemas, para que possam vender a representação digital de seu impacto em troca de novos tokens.

## 10.2 Créditos Sustentáveis

Uma lógica semelhante ` a do Crédito de Regeneração pode ser aplicada a diferentes áreas. Por exemplo, é possível criar um sistema para financiar usinas de energia renovável com tokens, tornando a energia solar, é olica, hídrica e outras fontes renováveis mais lucrativas. O mesmo modelo pode ser aplicado a outros setores, como reciclagem, bioconstrução e vários outros projetos de sustentabilidade.

## 10.3 Recompensas por Serviços

Muitos serviços são de interesse comum a todos, e podemos desenvolver projetos para recompensar esses serviços. Por exemplo, o combate a incêndios de forma independente, onde pessoas com o equipamento apropriado unem forças para combater o fogo, deveria ser um dos serviços mais importantes de todos. Em outras palavras, um sistema de recompensa baseado em contrato inteligente poderia ser usado para incentivar os esforços de combate a incêndios.

## 10.4 Sistemas Educacionais

Infelizmente, as blockchains, pelo menos por enquanto, não armazenam vídeos, fotos e outros tipos de mídia. Elas armazenam apenas números e letras. No entanto, quando combinadas com o armazenamento de dados externo, outras ideias surgem. Algoritmos de hashing e soluçãoes de armazenamento descentralizado, como o IPFS[6], podem ser usados para criar strings únicas que referenciam imagens e vídeos armazenados fora da blockchain. Isso abre novas possibilidades para os contratos inteligentes, incluindo a criação de sistemas educacionais descentralizados.

## 10.5 Comunidades Autônomas Descentralizadas

Duas pessoas que concordam com uma troca de valor podem executar seus próprios nós e fazer transaçãoes sem a necessidade de um terceiro de confiança. O mesmo princípio se aplica a grupos maiores. É possível que um grupo de pessoas estabeleça uma comunidade regida via blockchain. Até mesmo vilas inteiras podem funcionar com base em contratos inteligentes - isso requer apenas o acordo coletivo da comunidade. Quando combinado com utossuficiência, uma nova forma, independente e descentralizada, de relação social entre os seres humanos e a Natureza pode emergir.

Isso leva a várias possibilidades, incluindo mecanismos de votação e governança, onde as pessoas podem exercer seu papel de forma proativa, em vez de votar em um representante que pode defender seus próprios interesses. Os contratos inteligentes da comunidade podem ser desenvolvidos ao longo do tempo, criando um framework que facilite a implementação do sistema por novos projetos.

Outro ponto interessante é que frequentemente vemos uma disputa polarizada entre capitalismo e comunismo, ou direita squerda, ou diversas outras polaridades e divergências. As pessoas tentam impor suas próprias verdades aos outros, e isso, quando combinado com a ganância e a competição por recursos, muitas vezes leva ` a violência. No descentralismo, cada vila poderia ter suas próprias diretrizes e construir contratos de acordo com seu sistema preferido, seja uma abordagem mais 'capitalista' ou mais 'comunista'. Isso permite que os indivíduos escolham viver de acordo com seus próprios ideais, em vez de tê-los impostos pelo sistema.

Figura 6: Imposição vs. escolha

<!-- image -->

## 10.6 Reforma agrária

No mundo ideal, cada pedaço de terra degradado seria distribuído para que as pessoas vivessem nele enquanto o regenerassem. Mas no mundo capitalista, um 'proprietário de terras'poderia vendê-la em troca de alguns anos recebendo uma taxa de base comum sobre as transaçãoes da vila operada por contratos inteligentes, em um mecanismo de reforma agrária privada.

## 11 Indo além

A tecnologia de blockchain e contratos inteligentes ainda é muito recente, há muito para sua evolução, em tantas direçãoes. No entanto, acredito que haverá um futuro, seja em séculos ou milênios, onde os

contratos inteligentes, ou uma evolução deles, serão tão comuns que as pessoas não entenderão mais como a vida era possível antes deles. Digo isso com a esperança de que a humanidade encontrará uma maneira de evitar sua própria extinção. É por isso que projetos focados em regenerar a vida estão entre os mais cruciais.

Indo além, uma possibilidade é criar um sistema operacional alimentado pela blockchain, onde aplicativos aprovados pela comunidade estarão disponíveis para os usuários. No início, os servidores da rede serão usados para conectar e mostrar os dados da blockchain aos usuários. Num segundo momento, um caminho para a descentralização de nós é o desenvolvimento de nós móveis leves, onde a blockchain pode ser usada como uma camada de dados distribú ıda do sistema operacional para que os usuários possam receber nviar transaçãoes por conta própria.

## 12 Conclusão

Neste trabalho, propusemos uma infraestrutura de contrato inteligente P2P focada em aplicaçãoes sociais e ambientais. Impacto e descentralização são nossos valores centrais. Impacto, porque nossa missão é tornar este mundo um lugar melhor através da tecnologia. E descentralização, porque queremos ser o mais descentralizados possível. A rede é o conjunto de nós, servidores e mineradores. Juntos, eles compõem a Sintrop Virtual Machine, uma plataforma de contrato inteligente e uma blockchain pública. A moeda SINTROP, token de utilidade nativo para gas fees, não será pré-minerada e será distribú ıda ao longo do tempo no consenso Proof-of-Work ao encontrar novos blocos, sendo a mineração á unica forma de obter novas moedas. Nosso objetivo é alimentar os computadores com energia renovável, e incentivamos os nós a gerar sua própria energia renovável. Muitas aplicaçãoes incríveis podem ser criadas com contratos inteligentes, e cabe a nós criar um mundo melhor, combater as mudanças climáticas e devolver o poder ao povo.

## Referências

- [1] A. Ravagnani, 'Regeneration credit: A peer-to-peer nature regeneration system,' Whitepaper , 2025.
- [2] V. Buterin, 'Ethereum: A next-generation smart contract and decentralized application platform.,' Whitepaper , 2014.
- [3] S. Nakamoto, 'Bitcoin: A peer-to-peer electronic cash system,' Whitepaper , 2008.
- [4] D. S. Fernando Rebello, Syntropic Agriculture According to Ernst G¨ otsch . CEPEAS, 2022.
- [5] G. Wood, 'Ethereum: A secure decentralised generalised transaction ledger,' Whitepaper , 2015.
- [6] J. Benet, 'Ipfs - content addressed, versioned, p2p file system,' Whitepaper , 2015.

## Glossário

- blockchain A tecnologia blockchain é uma rede de computadores, onde cada nó armazena uma cópia completa do histórico de transaçãoes, processando e armazenando dados em uma arquitetura distribú ıda. 1
- bridge O termo 'ponte' (bridge) é frequentemente usado por blockchains de segunda camada para se referir ao código e aos contratos inteligentes responsáveis por gerenciar ativos de uma cadeia para outra. 1
- consensus mechanism Um mecanismo de consenso é um protocolo que leva todos os nós de uma rede blockchain distribú ıda a um acordo sobre um único conjunto de dados. 4
- Ether Ether é a criptomoeda nativa para taxas de gás (gas fees) da rede Ethereum. 1
- EVM A Ethereum Virtual Machine (EVM) é o motor de computação para a Ethereum que gerencia o estado da blockchain e habilita a funcionalidade de contratos inteligentes. 1
- fiat Termo usado para se referir ` a moeda emitida pelo governo que não é lastreada por uma commodity f é ısica, como ouro ou prata. É lastreada pelo governo que a emite. 4
- gas fees Gás (Gas) se refere ` a taxa necessária para conduzir com sucesso uma transação em uma blockchain. 2, 5, 6, 8
- memecoins Clones de blockchain de memes ou contratos inteligentes de memes que não possuem utilidade, vivendo em uma base especulativa sobre uma imagem/pessoa/animal. 1, 5
- NFTs Tokens não fungíveis, ou NFTs, são tokens únicos baseados em blockchain, comumente usados para representar algo. Não podem ser copiados, substitú ıdos ou subdivididos. 1, 5
- ownable Contrato 'ownable' da OpenZeppelin, um contrato inteligente que define uma carteira (wallet) como proprietária de um contrato após sua implantação, sendo capaz de realizar açãoes privilegiadas. 2
- owner A carteira (wallet) que tem o poder de realizar açãoes privilegiadas ao usar o contrato ownable.sol disponível na OpenZeppelin. Geralmente é a carteira que fez a implantação do contrato. A propriedade pode ser transferida ou renunciada. 2
- peer-to-peer Ponto a ponto (Peer-to-peer), ou P2P, é um tipo de arquitetura de rede distribú ıda na qual os computadores conectados ao sistema também funcionam como servidores, armazenando e processando transaçãoes que ocorrem diretamente entre os usuários, sem a intermediação de um terceiro. 1
- proof-of-work Prova de trabalho (Proof of work) é o mecanismo de consenso criptográfico original, usado pela primeira vez pelo Bitcoin. 1
- renounceOwnership Função do contrato ownable.sol da OpenZeppelin que permite ao proprietário renunciar ao privilégio, transferindo-o para o endereço zero. 2
- Sintrop SINTROP é a criptomoeda de utilidade nativa para taxas de gás (gas fee) da rede Sintrop. 2
- smart contract Pequenos programas de computador, implantados em uma blockchain, que contêm regras e dados e permitem que carteiras (wallets) interajam com eles sem uma autoridade central. 3
- solidity Solidity é uma linguagem orientada a contratos e foi projetada para compilar código para a Ethereum Virtual Machine. 6

- SVM A Sintrop Virtual Machine (SVM) é o motor de computação para a Sintrop que gerencia o estado da blockchain e habilita a funcionalidade de contratos inteligentes. 3

token Unidade de dados de um contrato inteligente, geralmente usada com funçãoes padrão. 1, 2

- wallet Uma carteira (wallet) de criptomoedas é um dispositivo, meio físico, programa ou serviço online que armazena as chaves públicas e/ou privadas para transaçãoes de criptomoedas. 2, 3

## Aviso legal

O token Sintrop foi projetado struturado como um token de utilidade para taxas de gás (gas fees) da rede, servindo como a criptomoeda nativa dentro do ecossistema Sintrop. Ele não se destina a investimento especulativo, nem concede aos seus detentores quaisquer direitos a dividendos, lucros, direitos de voto ou outras características típicas de valores mobiliários. Este documento é fornecido apenas para fins informativos e não constitui uma oferta de investimento, aconselhamento jurídico ou financeiro.