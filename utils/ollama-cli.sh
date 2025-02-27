# Down model
curl http://10.159.11.24:11434/api/generate -d '{"model": "gemma2:latest", "keep_alive": 0}'

# Run model
curl http://10.159.11.24:11434/api/generate -d '{"model": "gemma2:latest", "keep_alive": -1}'

# Call model
curl http://10.159.11.24:11434/api/chat -d '{
  "model": "llama3",
  "messages": [
    {
      "role": "user",
      "content": "Você é um assistente para definição de uma lista de tipos de documentos baseada na área de negócio de uma empresa. Dada uma área de negócio a ser fornecida através de um contexto, sua tarefa é criar uma lista de tipos documentos possíveis para essa área de negócio. Você deve responder em Português do Brasil. Seja preciso e inclua na resposta os campos tipo, descrição e área. Contexto: Minha empresa de contabilidade presta serviços de contabilidade para diversas empresas de ramos diversos e possui as seguintes áreas: registro e escrituração contábil, comercial, Recursos Humanos, Consultoria Tributária e Jurídica."
    },  
    # {
    #   "role": "assistant",
    #   "content": "Você é um assistente para definição de uma lista de tipos de documentos baseada na área de negócio de uma empresa. Dada uma área de negócio a ser fornecida através de um contexto, sua tarefa é criar uma lista de tipos documentos possíveis para essa área de negócio. Você deve responder em Português do Brasil. Seja preciso e inclua na resposta os campos tipo, descrição e área."
    # },
    # {
    #   "role": "user",
    #   "content": "Baseado no contexto, me forneça a lista de tipos de documentos."
    # },      
  ],
  "stream": false
}'