[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | **Português** | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Usando Qwen.ai com GAC

O GAC suporta autenticação via Qwen.ai OAuth, permitindo que você use sua conta Qwen.ai para geração de mensagens de commit. Isso usa autenticação de fluxo de dispositivo OAuth para uma experiência de login perfeita.

## O que é Qwen.ai?

Qwen.ai é a plataforma de IA da Alibaba Cloud que fornece acesso à família Qwen de grandes modelos de linguagem. O GAC suporta autenticação baseada em OAuth, permitindo que você use sua conta Qwen.ai sem precisar gerenciar chaves de API manualmente.

## Benefícios

- **Autenticação fácil**: Fluxo de dispositivo OAuth - basta fazer login com seu navegador
- **Sem gerenciamento de chave de API**: A autenticação é tratada automaticamente
- **Acesso aos modelos Qwen**: Use modelos Qwen poderosos para geração de mensagens de commit

## Configuração

O GAC inclui autenticação OAuth integrada para Qwen.ai usando o fluxo de dispositivo. O processo de configuração exibirá um código e abrirá seu navegador para autenticação.

### Opção 1: Durante a configuração inicial (Recomendado)

Ao executar `gac init`, basta selecionar "Qwen.ai (OAuth)" como seu provedor:

```bash
gac init
```

O assistente irá:

1. Pedir para você selecionar "Qwen.ai (OAuth)" na lista de provedores
2. Exibir um código de dispositivo e abrir seu navegador
3. Você se autenticará no Qwen.ai e inserirá o código
4. Salvar seu token de acesso com segurança
5. Definir o modelo padrão

### Opção 2: Mudar para Qwen.ai mais tarde

Se você já configurou o GAC com outro provedor e deseja mudar para o Qwen.ai:

```bash
gac model
```

Então:

1. Selecione "Qwen.ai (OAuth)" na lista de provedores
2. Siga o fluxo de autenticação de código de dispositivo
3. Token salvo com segurança em `~/.gac/oauth/qwen.json`
4. Modelo configurado automaticamente

### Opção 3: Login direto

Você também pode se autenticar diretamente usando:

```bash
gac auth qwen login
```

Isso irá:

1. Exibir um código de dispositivo
2. Abrir seu navegador na página de autenticação do Qwen.ai
3. Após a autenticação, o token é salvo automaticamente

### Usar GAC normalmente

Uma vez autenticado, use o GAC normalmente:

```bash
# Prepare suas alterações
git add .

# Gere e faça commit com Qwen.ai
gac

# Ou substitua o modelo para um único commit
gac -m qwen:qwen3-coder-plus
```

## Modelos disponíveis

A integração Qwen.ai OAuth usa:

- `qwen3-coder-plus` - Otimizado para tarefas de codificação (padrão)

Este é o modelo disponível através do endpoint OAuth portal.qwen.ai. Para outros modelos Qwen, considere usar o provedor OpenRouter, que oferece opções adicionais de modelos Qwen.

## Comandos de autenticação

O GAC fornece vários comandos para gerenciar a autenticação Qwen.ai:

```bash
# Login no Qwen.ai
gac auth qwen login

# Verificar status de autenticação
gac auth qwen status

# Logout e remover token armazenado
gac auth qwen logout

# Verificar status de todos os provedores OAuth
gac auth
```

### Opções de login

```bash
# Login padrão (abre o navegador automaticamente)
gac auth qwen login

# Login sem abrir o navegador (exibe URL para visitar manualmente)
gac auth qwen login --no-browser

# Modo silencioso (saída mínima)
gac auth qwen login --quiet
```

## Solução de problemas

### Token expirado

Se você vir erros de autenticação, seu token pode ter expirado. Reautentique executando:

```bash
gac auth qwen login
```

O fluxo de código de dispositivo será iniciado e seu navegador será aberto para reautenticação.

### Verificar status de autenticação

Para verificar se você está autenticado atualmente:

```bash
gac auth qwen status
```

Ou verifique todos os provedores de uma vez:

```bash
gac auth
```

### Logout

Para remover seu token armazenado:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Autenticação Qwen não encontrada)

Isso significa que o GAC não consegue encontrar seu token de acesso. Autentique executando:

```bash
gac auth qwen login
```

Ou execute `gac model` e selecione "Qwen.ai (OAuth)" na lista de provedores.

### "Authentication failed" (Falha na autenticação)

Se a autenticação OAuth falhar:

1. Certifique-se de ter uma conta Qwen.ai
2. Verifique se o navegador abre corretamente
3. Verifique se você inseriu o código do dispositivo corretamente
4. Tente um navegador diferente se os problemas persistirem
5. Verifique a conectividade de rede com `qwen.ai`

### Código de dispositivo não funcionando

Se a autenticação de código de dispositivo não estiver funcionando:

1. Certifique-se de que o código não expirou (os códigos são válidos por um tempo limitado)
2. Tente executar `gac auth qwen login` novamente para obter um novo código
3. Use o sinalizador `--no-browser` e visite manualmente a URL se a abertura do navegador falhar

## Notas de segurança

- **Nunca faça commit do seu token de acesso** no controle de versão
- O GAC armazena tokens automaticamente em `~/.gac/oauth/qwen.json` (fora do diretório do seu projeto)
- Os arquivos de token têm permissões restritas (legíveis apenas pelo proprietário)
- Os tokens podem expirar e exigirão reautenticação
- O fluxo de dispositivo OAuth foi projetado para autenticação segura em sistemas headless

## Veja também

- [Documentação principal](USAGE.md)
- [Configuração do Claude Code](CLAUDE_CODE.md)
- [Guia de solução de problemas](TROUBLESHOOTING.md)
- [Documentação Qwen.ai](https://qwen.ai)
