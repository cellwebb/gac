# Solução de problemas do gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | [Tiếng Việt](../vi/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | **Português** | [Norsk](../no/TROUBLESHOOTING.md) | [Svenska](../sv/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md) | [Italiano](../it/TROUBLESHOOTING.md)

Este guia cobre problemas comuns e soluções para instalar, configurar e executar o gac.

## Índice

- [Solução de problemas do gac](#solução-de-problemas-do-gac)
  - [Índice](#índice)
  - [1. Problemas de Instalação](#1-problemas-de-instalação)
  - [2. Problemas de Configuração](#2-problemas-de-configuração)
  - [3. Erros de Provedor/API](#3-erros-de-provedorapi)
  - [4. Problemas de Agrupamento de Commits](#4-problemas-de-agrupamento-de-commits)
  - [5. Segurança e Detecção de Segredos](#5-segurança-e-detecção-de-segredos)
  - [6. Problemas com Hooks do Pre-commit e Lefthook](#6-problemas-com-hooks-do-pre-commit-e-lefthook)
  - [7. Problemas Comuns de Fluxo de Trabalho](#7-problemas-comuns-de-fluxo-de-trabalho)
  - [8. Depuração Geral](#8-depuração-geral)
  - [Ainda em Dúvidas?](#ainda-em-dúvidas)
  - [Onde Obter Ajuda Adicional](#onde-obter-ajuda-adicional)

## 1. Problemas de Instalação

**Problema:** Comando `gac` não encontrado após a instalação

- Certifique-se de que você instalou com `uv tool install gac` ou `uvx gac`
- Se usou `uv tool install`, verifique a instalação com `uv tool list`
- Garanta que `uv` está instalado e no seu `$PATH`
- Reinicie seu terminal após a instalação

**Problema:** Permissão negada ou não consegue escrever arquivos

- Verifique as permissões do diretório
- Tente executar com privilégios apropriados ou altere a propriedade do diretório

## 2. Problemas de Configuração

**Problema:** gac não consegue encontrar sua chave de API ou modelo

- Se você é novo, execute `gac init` para configurar interativamente seu provedor, modelo e chaves de API
- Certifique-se de que seu `.gac.env` ou variáveis de ambiente estão configurados corretamente
- Execute `gac --log-level=debug` para ver quais arquivos de configuração são carregados e depurar problemas de configuração
- Verifique erros de digitação nos nomes das variáveis (ex: `GAC_GROQ_API_KEY`)

**Problema:** Alterações no nível de usuário `$HOME/.gac.env` não são detectadas

- Certifique-se de que você está editando o arquivo correto para o seu SO:
  - No macOS/Linux: `$HOME/.gac.env` (geralmente `/Users/<seu-usuario>/.gac.env` ou `/home/<seu-usuario>/.gac.env`)
  - No Windows: `$HOME/.gac.env` (tipicamente `C:\Users\<seu-usuario>\.gac.env` ou use `%USERPROFILE%`)
- Execute `gac --log-level=debug` para confirmar que a configuração no nível de usuário está carregada
- Reinicie seu terminal ou execute seu shell novamente para recarregar as variáveis de ambiente
- Se ainda não funcionar, verifique erros de digitação e permissões de arquivo

**Problema:** Alterações no nível de projeto `.gac.env` não são detectadas

- Certifique-se de que seu projeto contém um arquivo `.gac.env` no diretório raiz (ao lado da sua pasta `.git`)
- Execute `gac --log-level=debug` para confirmar que a configuração no nível de projeto está carregada
- Se você editar `.gac.env`, reinicie seu terminal ou execute seu shell novamente para recarregar as variáveis de ambiente
- Se ainda não funcionar, verifique erros de digitação e permissões de arquivo

**Problema:** Não consegue definir ou alterar idioma para mensagens de commit

- Execute `gac language` (ou `gac lang`) para selecionar interativamente entre 25+ idiomas suportados
- Use o flag `-l <idioma>` para substituir o idioma para um único commit (ex: `gac -l zh-CN`, `gac -l Spanish`)
- Verifique sua configuração com `gac config show` para ver a configuração atual de idioma
- A configuração de idioma é armazenada em `GAC_LANGUAGE` no seu arquivo `.gac.env`

## 3. Erros de Provedor/API

**Problema:** Erros de autenticação ou API

- Garanta que você definiu as chaves de API corretas para seu modelo escolhido (ex: `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Verifique novamente sua chave de API e status da conta do provedor
- Para Ollama e LM Studio, confirme que a URL da API corresponde à sua instância local. Chaves de API são necessárias apenas se você ativou a autenticação.
- **Para problemas de OAuth do Claude Code**, consulte o [guia de configuração do Claude Code](CLAUDE_CODE.md) para ajuda com autenticação e expiração de token.

**Problema:** Modelo não disponível ou não suportado

- Streamlake usa IDs de endpoint de inferência em vez de nomes de modelo. Garanta que você forneceu o ID do endpoint do console deles.
- Verifique se o nome do modelo está correto e suportado pelo seu provedor
- Verifique a documentação do provedor para modelos disponíveis

## 4. Problemas de Agrupamento de Commits

**Problema:** Flag `--group` não funcionando como esperado

- A flag `--group` analisa automaticamente as alterações em staging e pode criar múltiplos commits lógicos
- O LLM pode decidir que um único commit faz sentido para seu conjunto de alterações em staging, mesmo com `--group`
- Este é comportamento intencional - o LLM agrupa alterações com base em relacionamentos lógicos, não apenas quantidade
- Garanta que você tenha múltiplas alterações não relacionadas em staging (ex: correção de bug + adição de funcionalidade) para melhores resultados
- Use `gac --show-prompt` para depurar o que o LLM está vendo

**Problema:** Commits agrupados incorretamente ou não agrupados quando esperado

- O agrupamento é determinado pela análise do LLM de suas alterações
- O LLM pode criar um único commit se determinar que as alterações estão logicamente relacionadas
- Tente adicionar dicas com `-h "dica"` para guiar a lógica de agrupamento (ex: `-h "separar correção de bug de refatoração"`)
- Revise os grupos gerados antes de confirmar
- Se o agrupamento não funcionar bem para seu caso de uso, faça commits das alterações separadamente

## 5. Segurança e Detecção de Segredos

**Problema:** Falso positivo: verificação de segredos detecta não-segredos

- O verificador de segurança procura padrões que se assemelham a chaves de API, tokens e senhas
- Se você está fazendo commit de código de exemplo, fixtures de teste ou documentação com chaves de placeholder, você pode ver falsos positivos
- Use `--skip-secret-scan` para ignorar a verificação se tiver certeza de que as alterações são seguras
- Considere excluir arquivos de teste/exemplo dos commits, ou use placeholders claramente marcados

**Problema:** Verificação de segredos não detectando segredos reais

- O verificador usa correspondência de padrões e pode não pegar todos os tipos de segredos
- Sempre revise suas alterações em staging com `git diff --staged` antes de fazer commit
- Considere usar ferramentas de segurança adicionais como `git-secrets` ou `gitleaks` para proteção abrangente
- Relate quaisquer padrões perdidos como issues para ajudar a melhorar a detecção

**Problema:** Precisa desativar verificação de segredos permanentemente

- Defina `GAC_SKIP_SECRET_SCAN=true` no seu arquivo `.gac.env`
- Use `gac config set GAC_SKIP_SECRET_SCAN true`
- Nota: Desative apenas se você tiver outras medidas de segurança em vigor

## 6. Problemas com Hooks do Pre-commit e Lefthook

**Problema:** Hooks do pre-commit ou lefthook estão falhando e bloqueando commits

- Use `gac --no-verify` para ignorar temporariamente todos os hooks do pre-commit e lefthook
- Corrija os problemas subjacentes que estão fazendo os hooks falharem
- Considere ajustar sua configuração do pre-commit ou lefthook se os hooks forem muito restritivos

**Problema:** Hooks do pre-commit ou lefthook estão demorando muito ou interferindo no fluxo de trabalho

- Use `gac --no-verify` para ignorar temporariamente todos os hooks do pre-commit e lefthook
- Considere configurar hooks do pre-commit em `.pre-commit-config.yaml` ou hooks do lefthook em `.lefthook.yml` para serem menos agressivos para seu fluxo de trabalho
- Revise sua configuração de hooks para otimizar o desempenho

## 7. Problemas Comuns de Fluxo de Trabalho

**Problema:** Nenhuma alteração para fazer commit / nada em staging

- gac requer alterações em staging para gerar uma mensagem de commit
- Use `git add <arquivos>` para colocar alterações em staging, ou use `gac -a` para colocar todas as alterações em staging automaticamente
- Verifique `git status` para ver quais arquivos foram modificados
- Use `gac diff` para ver uma view filtrada de suas alterações

**Problema:** Mensagem de commit não é o que eu esperava

- Use o sistema de feedback interativo: digite `r` para reroll, `e` para editar, ou forneça feedback em linguagem natural
- Adicione contexto com `-h "sua dica"` para guiar o LLM
- Use `-o` para mensagens mais simples de uma linha ou `-v` para mensagens mais detalhadas
- Use `--show-prompt` para ver quais informações o LLM está recebendo

**Problema:** gac está muito lento

- Use `gac -y` para ignorar o prompt de confirmação
- Use `gac -q` para modo silencioso com menos saída
- Considere usar modelos mais rápidos/baratos para commits de rotina
- Use `gac --no-verify` para ignorar hooks se estiverem atrasando você

**Problema:** Não consigo editar ou fornecer feedback após a geração da mensagem

- No prompt, digite `e` para entrar no modo de edição (suporta keybindings vi/emacs)
- Digite `r` para regenerar sem feedback
- Ou simplesmente digite seu feedback diretamente (ex: "torne mais curto", "foco na correção do bug")
- Pressione Enter na entrada vazia para ver o prompt novamente

## 8. Depuração Geral

- Use `gac init` para redefinir ou atualizar sua configuração interativamente
- Use `gac --log-level=debug` para saída de depuração detalhada e logging
- Use `gac --show-prompt` para ver qual prompt está sendo enviado para o LLM
- Use `gac --help` para ver todos os flags de linha de comando disponíveis
- Use `gac config show` para ver todos os valores de configuração atuais
- Verifique logs para mensagens de erro e stack traces
- Verifique o [README.md](../README.md) principal para recursos, exemplos e instruções de início rápido

## Ainda em Dúvidas?

- Pesquise issues existentes ou abra uma nova no [repositório GitHub](https://github.com/cellwebb/gac)
- Inclua detalhes sobre seu SO, versão do Python, versão do gac, provedor e saída de erro
- Quanto mais detalhes você fornecer, mais rápido sua issue poderá ser resolvida

## Onde Obter Ajuda Adicional

- Para recursos e exemplos de uso, veja o [README.md](../README.md) principal
- Para prompts de sistema personalizados, veja [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Para diretrizes de contribuição, veja [CONTRIBUTING.md](../CONTRIBUTING.md)
- Para informações de licença, veja [../LICENSE](../LICENSE)
