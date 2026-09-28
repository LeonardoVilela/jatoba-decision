# Candidate descriptions (frozen dictionary `general-candidates-v1`)

Every reported JATOBÁ result used exactly these texts (`benchmark/candidate_dictionary.json`, byte-identical to the frozen file).
They must not be edited: a changed description is a new benchmark version.

**How to read the tables.**
- *Source* says who wrote the text.
- *Caveat* flags anything that could make a task easier than its upstream definition.
- The descriptions were reviewed by two project reviewers (internal Gate H QA). They have **not** been validated by external annotators.

Community Alignment has no fixed candidates: its candidates are the upstream response texts, verbatim.

## Audit findings

- **Mechanical check against the evaluated states.** Every fixed description was compared with every state in `jatoba_id` and `legacy_exposed` (28,296 decisions) for shared 5-word sequences.
  - There is one hit: `massive_ptbr:944:test` shares the generic phrase 'a diferença de horas entre' with the `datetime_convert` description.
  - No description copies an evaluated example.
- **Toxicity (NOUL) and emotion (SCORE):** the candidate texts are generic. They carry no class-specific wording that could leak the label; the property or emotion is stated only in the question.
- **MASSIVE intent descriptions are project-authored, with disambiguating clauses.**
  - Examples: 'sem converter um horário entre fusos' for datetime_query; 'sem apenas ligar, desligar, aumentar ou diminuir' for iot_hue_lightchange.
  - These clauses go beyond the upstream intent names, which carry no definitions. Ten were revised after checking TRAIN utterances; test data was not used.
  - This can make overlapping intents easier to separate than the bare names would. MASSIVE results are reported as LEGACY / previously exposed in any case.
- **Transformation, not upstream text:**
  - the InferBR label definitions;
  - the ASSIN 2 entailment wording (the NOUL 'false' option means *not entailed*, not *false*).

## Fixed-taxonomy candidates

### `massive_intent` (CHOICE)

Question: Qual categoria melhor descreve o pedido do usuário?  
Source: project-authored. Written from the official MASSIVE intent name (MASSIVE publishes no definitions) and checked against TRAIN utterances; 10 of 60 revised during review.

| id | public description | review | previous text |
|---|---|---|---|
| `datetime_query` | consultar data ou hora: perguntar a data, o dia/calendário ou a hora em um local, sem converter um horário entre fusos | REVISED | consultar data ou hora: perguntar a data, o dia ou a hora atual, inclusive em outro lugar |
| `iot_hue_lightchange` | configurar iluminação: definir cor, tonalidade, ambiente ou nível específico das luzes inteligentes, sem apenas ligar, desligar, aumentar ou diminuir | REVISED | ajustar a iluminação: mudar a cor, a tonalidade ou o ajuste das luzes inteligentes |
| `transport_ticket` | comprar passagem: procurar ou reservar passagem de trem, avião, ônibus ou outro transporte | APPROVED |  |
| `takeaway_query` | consultar entrega ou retirada de comida: consultar opções, disponibilidade, recomendações ou status/prazo de comida para entrega ou retirada, sem efetuar o pedido | REVISED | consultar pedido de comida: perguntar sobre pedido de comida para entrega ou retirada, como status, prazo ou se o restaurante oferece o serviço |
| `qa_stock` | consultar bolsa de valores: perguntar sobre cotações de ações ou novidades do mercado financeiro | APPROVED |  |
| `general_greet` | cumprimentar: saudação ou conversa de cortesia com o assistente | APPROVED |  |
| `recommendation_events` | sugerir eventos: pedir sugestões de eventos ou do que está acontecendo por perto | APPROVED |  |
| `music_dislikeness` | não gostar da música: dizer que não gosta da música que está tocando ou de uma música | APPROVED |  |
| `iot_wemo_off` | desligar tomada inteligente: desligar uma tomada inteligente | APPROVED |  |
| `cooking_recipe` | pedir receita específica: pedir ingredientes, tempo ou instruções para preparar um prato específico | REVISED | pedir receita: pedir uma receita, os ingredientes ou o modo de preparo de um prato |
| `qa_currency` | consultar câmbio: perguntar a cotação de uma moeda ou converter valores entre moedas | APPROVED |  |
| `transport_traffic` | consultar trânsito: perguntar como está o trânsito em um trajeto ou região | APPROVED |  |
| `general_quirky` | conversa ou pedido incomum: interação geral, excêntrica ou não coberta pelas funções específicas do assistente | REVISED | conversa aleatória: comentário ou pergunta solta, fora dos demais assuntos, sem pedido de ação específico |
| `weather_query` | consultar o tempo: perguntar a previsão do tempo, a temperatura ou as condições climáticas | APPROVED |  |
| `audio_volume_up` | aumentar o volume: pedir para aumentar o volume ou falar mais alto | APPROVED |  |
| `email_addcontact` | adicionar contato de e-mail: adicionar um contato ou um endereço de e-mail à agenda | APPROVED |  |
| `takeaway_order` | pedir comida: fazer um pedido de comida para entrega ou retirada | APPROVED |  |
| `email_querycontact` | consultar contato: localizar ou consultar dados de uma pessoa na lista de contatos, como telefone ou e-mail | REVISED | consultar dados de contato: perguntar dados de um contato, como telefone, e-mail ou cargo |
| `iot_hue_lightup` | aumentar a luminosidade: deixar as luzes inteligentes mais fortes | APPROVED |  |
| `recommendation_locations` | sugerir lugares: pedir sugestões de lugares, como restaurantes, lojas ou pontos turísticos | APPROVED |  |
| `play_audiobook` | tocar audiolivro: iniciar, retomar ou avançar um audiolivro | APPROVED |  |
| `lists_createoradd` | criar lista ou adicionar item: criar uma lista ou incluir um item em uma lista | APPROVED |  |
| `news_query` | consultar notícias: pedir notícias ou atualizações sobre um assunto | APPROVED |  |
| `alarm_query` | consultar alarmes: perguntar quais alarmes estão definidos | APPROVED |  |
| `iot_wemo_on` | ligar tomada inteligente: ligar uma tomada inteligente | APPROVED |  |
| `general_joke` | contar piada: pedir ao assistente que conte uma piada | APPROVED |  |
| `qa_definition` | pedir definição: perguntar o significado ou a definição de uma palavra ou conceito | APPROVED |  |
| `social_query` | consultar redes sociais: perguntar sobre novidades, tendências ou atividade nas redes sociais | APPROVED |  |
| `music_settings` | configurar reprodução de música: mudar o modo de reprodução de música, como repetir, modo aleatório ou outras configurações | APPROVED |  |
| `audio_volume_other` | ajustar volume: alterar ou definir o volume de forma genérica, sem especificar aumentar, diminuir ou silenciar | REVISED | outros ajustes de som: ajustar ou consultar o volume e o som, exceto aumentar, diminuir ou silenciar |
| `calendar_remove` | remover evento da agenda: apagar ou cancelar um compromisso ou evento da agenda | APPROVED |  |
| `iot_hue_lightdim` | diminuir a luminosidade: deixar as luzes inteligentes mais fracas | APPROVED |  |
| `calendar_query` | consultar agenda: perguntar sobre compromissos, reuniões ou lembretes marcados | APPROVED |  |
| `email_sendemail` | enviar e-mail ou mensagem direta: redigir, ditar ou enviar uma mensagem diretamente a um destinatário, sem publicar em rede social | REVISED | enviar e-mail ou mensagem: escrever ou enviar um e-mail ou uma mensagem |
| `iot_cleaning` | acionar limpeza: ligar o robô aspirador ou iniciar a limpeza da casa | APPROVED |  |
| `audio_volume_down` | diminuir o volume: pedir para abaixar o volume | APPROVED |  |
| `play_radio` | tocar rádio: tocar uma estação ou serviço de rádio | APPROVED |  |
| `cooking_query` | tirar dúvida culinária: fazer pergunta geral sobre o que cozinhar, técnicas ou substituição de ingredientes, em vez de solicitar apenas uma receita específica | REVISED | pergunta sobre culinária: perguntar o que cozinhar, como preparar algo ou como substituir um ingrediente |
| `datetime_convert` | converter fuso horário: converter um horário entre fusos ou perguntar a diferença de horas entre lugares | APPROVED |  |
| `qa_maths` | fazer um cálculo: pedir o resultado de uma conta matemática | APPROVED |  |
| `iot_hue_lightoff` | apagar as luzes: desligar as luzes inteligentes | APPROVED |  |
| `iot_hue_lighton` | acender as luzes: ligar as luzes inteligentes | APPROVED |  |
| `transport_query` | consultar rota ou direções: pedir direções ou um caminho para chegar a um destino, sem tratar especificamente de trânsito, táxi ou compra de passagem | REVISED | consultar rota ou transporte: pedir direções, rotas ou informações sobre transporte |
| `music_likeness` | gostar da música: dizer que gosta de uma música ou registrar uma preferência musical | APPROVED |  |
| `email_query` | consultar e-mails: verificar a caixa de entrada ou perguntar sobre e-mails recebidos | APPROVED |  |
| `play_music` | tocar música: tocar uma música, um artista, um álbum ou uma playlist | APPROVED |  |
| `audio_volume_mute` | silenciar: pedir para silenciar o som ou para o assistente parar de falar | APPROVED |  |
| `social_post` | publicar em rede social: postar ou enviar algo em uma rede social | APPROVED |  |
| `alarm_set` | criar alarme: definir um alarme para um horário | APPROVED |  |
| `qa_factoid` | pergunta factual: perguntar um fato de conhecimento geral | APPROVED |  |
| `calendar_set` | criar evento ou lembrete: marcar um compromisso ou criar um lembrete na agenda | APPROVED |  |
| `play_game` | jogar: iniciar ou jogar um jogo com o assistente | APPROVED |  |
| `alarm_remove` | remover alarme: cancelar ou apagar um alarme | APPROVED |  |
| `lists_remove` | remover lista ou item: apagar uma lista ou tirar um item de uma lista | APPROVED |  |
| `transport_taxi` | chamar táxi: pedir ou agendar um táxi ou carro por aplicativo | APPROVED |  |
| `recommendation_movies` | sugerir filmes: pedir sugestões de filmes para assistir | APPROVED |  |
| `iot_coffee` | fazer café: pedir para a cafeteira inteligente preparar café | APPROVED |  |
| `music_query` | perguntar sobre a música: perguntar o nome, o artista ou o álbum de uma música | APPROVED |  |
| `play_podcasts` | tocar podcast: tocar, retomar ou avançar um podcast | APPROVED |  |
| `lists_query` | consultar lista: perguntar o que há em uma lista | APPROVED |  |

### `assin2_entailment` (NOUL)

Question: A hipótese decorre da premissa?  
Source: project-authored from upstream guidelines. Follows the ASSIN 2 guideline: non-entailment covers neutral and contradiction, so 'false' does not mean the hypothesis is false.

| id | public description |
|---|---|
| `false` | Não — a hipótese não é implicada pela premissa. |
| `true` | Sim — a hipótese é implicada pela premissa. |

### `assin2_similarity` (SCORE)

Question: Qual é o nível de similaridade semântica entre premissa e hipótese?  
Source: upstream (verbatim). ASSIN 2 annotation guideline wording for the 1-5 similarity scale.

| id | public description |
|---|---|
| `1` | similaridade 1 de 5: sentenças completamente diferentes, sobre diferentes temas |
| `2` | similaridade 2 de 5: sentenças não relacionadas, mas sobre o mesmo tema |
| `3` | similaridade 3 de 5: sentenças de certa forma relacionadas: podem descrever fatos diferentes, mas compartilham de alguns detalhes |
| `4` | similaridade 4 de 5: sentenças fortemente relacionadas, mas que diferem em alguns detalhes |
| `5` | similaridade 5 de 5: sentenças significam essencialmente a mesma coisa |

### `homophobia_detection` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `obscene_detection` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `insult_detection` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `racism_detection` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `misogyny_detection` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `xenophobia_detection` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `offensive_language` (NOUL)

Question: (adapter question, see ADAPTER_AUDIT.md)  
Source: project-authored (generic). Generic true/false text shared by every toxicity task; the property itself is named only in the question.

| id | public description |
|---|---|
| `false` | false: não, a afirmação é falsa. a propriedade não está presente |
| `true` | true: sim, a afirmação é verdadeira. a propriedade está presente |

### `inferbr_nli3` (CHOICE)

Question: Qual é a relação entre a premissa e a hipótese?  
Source: project-authored. Short definitions of the three InferBR labels.

| id | public description |
|---|---|
| `implicação` | implicação. a hipótese decorre necessariamente da premissa |
| `neutro` | neutro. a premissa não confirma nem contradiz a hipótese |
| `contradição` | contradição. a hipótese não pode ser verdadeira se a premissa for verdadeira |

### `anger_intensity` (SCORE)

Question: Qual é a intensidade de raiva expressa no texto?  
Source: project-authored (generic rubric). Same four-level rubric for every emotion; the emotion is named only in the question.

| id | public description |
|---|---|
| `ausente` | Nível ordinal 0: ausente. a emoção não está presente |
| `baixa` | Nível ordinal 1: baixa. a emoção está presente com baixa intensidade |
| `moderada` | Nível ordinal 2: moderada. a emoção está presente com intensidade moderada |
| `alta` | Nível ordinal 3: alta. a emoção está presente com alta intensidade |

### `disgust_intensity` (SCORE)

Question: Qual é a intensidade de nojo expressa no texto?  
Source: project-authored (generic rubric). Same four-level rubric for every emotion; the emotion is named only in the question.

| id | public description |
|---|---|
| `ausente` | Nível ordinal 0: ausente. a emoção não está presente |
| `baixa` | Nível ordinal 1: baixa. a emoção está presente com baixa intensidade |
| `moderada` | Nível ordinal 2: moderada. a emoção está presente com intensidade moderada |
| `alta` | Nível ordinal 3: alta. a emoção está presente com alta intensidade |

### `fear_intensity` (SCORE)

Question: Qual é a intensidade de medo expressa no texto?  
Source: project-authored (generic rubric). Same four-level rubric for every emotion; the emotion is named only in the question.

| id | public description |
|---|---|
| `ausente` | Nível ordinal 0: ausente. a emoção não está presente |
| `baixa` | Nível ordinal 1: baixa. a emoção está presente com baixa intensidade |
| `moderada` | Nível ordinal 2: moderada. a emoção está presente com intensidade moderada |
| `alta` | Nível ordinal 3: alta. a emoção está presente com alta intensidade |

### `joy_intensity` (SCORE)

Question: Qual é a intensidade de alegria expressa no texto?  
Source: project-authored (generic rubric). Same four-level rubric for every emotion; the emotion is named only in the question.

| id | public description |
|---|---|
| `ausente` | Nível ordinal 0: ausente. a emoção não está presente |
| `baixa` | Nível ordinal 1: baixa. a emoção está presente com baixa intensidade |
| `moderada` | Nível ordinal 2: moderada. a emoção está presente com intensidade moderada |
| `alta` | Nível ordinal 3: alta. a emoção está presente com alta intensidade |

### `sadness_intensity` (SCORE)

Question: Qual é a intensidade de tristeza expressa no texto?  
Source: project-authored (generic rubric). Same four-level rubric for every emotion; the emotion is named only in the question.

| id | public description |
|---|---|
| `ausente` | Nível ordinal 0: ausente. a emoção não está presente |
| `baixa` | Nível ordinal 1: baixa. a emoção está presente com baixa intensidade |
| `moderada` | Nível ordinal 2: moderada. a emoção está presente com intensidade moderada |
| `alta` | Nível ordinal 3: alta. a emoção está presente com alta intensidade |

### `surprise_intensity` (SCORE)

Question: Qual é a intensidade de surpresa expressa no texto?  
Source: project-authored (generic rubric). Same four-level rubric for every emotion; the emotion is named only in the question.

| id | public description |
|---|---|
| `ausente` | Nível ordinal 0: ausente. a emoção não está presente |
| `baixa` | Nível ordinal 1: baixa. a emoção está presente com baixa intensidade |
| `moderada` | Nível ordinal 2: moderada. a emoção está presente com intensidade moderada |
| `alta` | Nível ordinal 3: alta. a emoção está presente com alta intensidade |

### `normastcu_relevance` (SCORE)

Question: Qual é o grau de relevância do documento para a consulta?  
Source: upstream (translated). Portuguese translation of the three relevance definitions in the NormasTCU paper; the original annotation wording is not published.

| id | public description |
|---|---|
| `0` | relevância 0 (irrelevante): o documento não trata do assunto da consulta |
| `1` | relevância 1 (parcialmente relevante): o documento menciona o tema da consulta ou trata de assunto relacionado, mas apenas parcialmente |
| `2` | relevância 2 (relevante): o documento responde diretamente à consulta e contém a informação central solicitada |

### `juristcu_relevance` (SCORE)

Question: Qual é o grau de relevância do documento para a consulta?  
Source: upstream (verbatim). Level definitions from the JurisTCU paper's judging prompt.

| id | public description |
|---|---|
| `0` | relevância 0 (irrelevante): o enunciado não responde a pergunta |
| `1` | relevância 1 (relacionado): o enunciado apenas está no tópico da pergunta |
| `2` | relevância 2 (relevante): o enunciado responde parcialmente a pergunta |
| `3` | relevância 3 (altamente relevante): o enunciado responde a pergunta, tratando completamente de suas nuances |
