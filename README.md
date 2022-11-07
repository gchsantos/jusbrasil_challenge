# Desafio-JusBrasil!


Olá! Meu nome é Gabriel Cesar Hilario dos Santos, dono do presente projeto. Através desse ReadMe farei o possível para que você consiga subir toda a estrutura desenvolvida para o desafio de forma simples e eficiente (Com apenas um comando 😉)!

  
# Sobre a API

Esta API foi solicitada por meio de um desafio técnico pela equipe de Recrutamento e Seleção da JusBrasil, tem como principal funcionalidade a inserção de Números CNJ (numeração única), estes que serão inseridos em uma fila para que posteriormente sejam capturados e persistidos no banco de dados através de [Celery](https://gist.github.com/Bgouveia/9e043a3eba439489a35e70d1b5ea08ec).

  
# Clonando O Repositório

Primeiramente, teremos que clonar o repositório, dessa forma todos os arquivos necessários para o funcionamento do projeto ficarão armazenados em um diretório local. Para isso é só executar o seguinte comando no seu terminal:

    git clone https://github.com/gchsantos/jusbrasil_challenge.git

  # Criando variável de ambiente
  
Será necessário criar um arquivo **.env** no diretório raiz da aplicação, para isso acesse o diretório do repositório:

    cd jusbrasil_challenge
    
Logo após crie o arquivo **.env** com as seguintes variáveis:

    SECRET_KEY=django-insecure--n^2)m36f)9q%&k)rd+modpybs**i&e(g)lcxwpg=z&_fse77p
    POSTGRES_USER=gchsantos
    POSTGRES_PASSWORD=itawesome
    POSTGRES_DB=jusbrasil_challenge
    DATABASE_HOST=postgres
    TZ=America/Sao_Paulo
    RABBITMQ_DEFAULT_USER=gchsantos
    RABBITMQ_DEFAULT_PASS=itawesome
    RABBITMQ_HOST=rabbitmq
    RABBITMQ_PORT=5672


# Subindo o ambiente 😉
Chegamos na melhor parte do projeto! Como estamos utilizando o querido ***docker-compose***, precisaremos apenas de um único comando para termos todo o ambiente em funcionamento. Continue dentro do repositório (**pasta clonada**) e execute o seguinte comando:
 
    docker-compose up -d

## Postgres

Após subirmos a estrutura, surgirá um *container* chamado **jusbrasil_challenge_postgres_1** este que é responsável pelo banco de dados [PostgreSQL](https://www.postgresql.org/about/) da API.


## API

A API surgirá com o *container* denominado **jusbrasil_challenge_api_1**, é nela que iremos realizar as nossas requisições para interagir com a solução.

### Autenticação

Para obtermos autorização e garantirmos que somente pessoas autenticadas possam realizar requisições importantes dentro da API precisaremos **criar um usuário**, execute o seguinte comando em seu terminal:

    curl --location --request POST 'http://localhost:8000/account/register' \
    --header 'accept: application/json' \
    --header 'Content-Type: application/json' \
    --data-raw '{ "username": "sogeking", "password": "lockon", "is_superuser": true}'
 
**Você irá obter o seguinte retorno (200):**

```json
{"username":"sogeking","is_superuser":true}
```

**Agora iremos autenticar o usuário criado para que ele receba um Token liberado para realizar as requisições:**

    curl --location --request POST 'http://localhost:8000/account/auth' \
    --header 'accept: application/json' \
    --header 'Content-Type: application/json' \
    --data-raw '{ "username": "sogeking", "password": "lockon"}'

  
**Seguindo os passos desse tutorial você obterá o seguinte retorno da API você irá obter um retorno parecido com esse:**

```json
 {"token": "9b24c7354e91c2ce4cfb619cacb5affaa3ed4ade"}
```

✨ **Pronto!** ✨ Agora já temos acesso as requisições da API, **guarde o *token* retornado** para as próximas requisições.


## Inserção de CNJS

**Até o momento a API suporta CNJS dos seguintes estados:**
 - Alagoas 
 - Ceará

Iremos agora inserir na fila uma lista de CNJS, para isso realize a seguinte requisição:

    curl --location --request POST 'http://localhost:8000/api/batch' \
    --header 'Authorization: Bearer {TOKEN}' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "cnjs": [
             "0005691-75.2019.8.06.0134",
             "0710802-55.2018.8.02.0001",
             "0070337-91.2008.8.06.0001"
        ],
        "refreshLawsuit": true,
        "publicConsultation": true
    }'

**Não esqueça de substituir {TOKEN} pelo seu token!**

Retorno esperado
```json
	{
	   "type":"BatchInsert",
	   "message":"The solicitation was inserted in queue sucessfuly",
	   "description":"Insertion of lawsuits in the robot's queue through the CNJ",
	   "consultationId":"72d26a60-3112-4de9-9403-6ff0f85cb00f"
	}
```

  Se tudo ocorreu bem você irá receber na resposta o **consultationId**, ele será necessário para consultar o resultado da captura posteriormente.

## Consultar Lote

  Agora iremos **utilizando o consultation_id**, capturar o resultado do nosso lote recém inserido:

    curl --location --request GET 'http://localhost:8000/api/batch/consultation/{CONSULTATION_ID}' \
    --header 'Authorization: Bearer {TOKEN}'

**Não esqueça de substituir {TOKEN} e {CONSULTATION_ID}!**

Retorno esperado:

```json
{
   "type":"BatchConsultation",
   "message":"success capturing consultation information",
   "description":"Get batch's captured information through the consultation_id",
   "consultationId":"72d26a60-3112-4de9-9403-6ff0f85cb00f",
   "batchConsultations":[
      {
         "cnj":"0005691-75.2019.8.06.0134",
         "lineStatus":"SUCCESS",
         "uf":"CE",
         "details":null,
         "createdAt":"2022-11-07T07:12:01.131769Z",
         "updatedAt":"2022-11-07T07:12:04.870974Z",
         "lawsuits":[
            {
               "instance":1,
               "value":"8.350,83",
               "lawsuitClass":"Procedimento Comum Cível",
               "subject":"Licença-Prêmio",
               "distribution":"30/09/2019 às 23:07 - Sorteio",
               "area":"Cível",
               "judge":"Sérgio da Nobrega Farias",
               "parts":[
                  {
                     "participation":"Requerente",
                     "person":"Helena Soares da Costa Araújo",
                     "relateds":[
                        {
                           "person":"Janildo Soares Moreira Fernandes",
                           "participation":"Advogado"
                        }
                     ]
                  },
                  {
                     "participation":"Requerido",
                     "person":"Município de Novo Oriente-ce",
                     "relateds":[
                        {
                           "person":"Francisco Everardo Carvalhedo Sales",
                           "participation":"Advogada"
                        }
                     ]
                  }
               ],
               "movements":[
                  {
                     "date":"22/09/2022",
                     "description":"Remetido Recurso Eletrônico ao Tribunal de Justiça"
                  }
               ]
            }
         ]
      }
   ]
}
```

Muito obrigado! Qualquer dúvida este é meu contato: gchsantos@gmail.com
