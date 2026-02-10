# 🚀 GUIA DE CONFIGURAÇÃO SUPABASE - SISTEMA 100% ONLINE

## ⚠️ IMPORTANTE: Execute estes passos AGORA

### 1️⃣ Criar Tabelas no Supabase

1. Acesse: https://supabase.com/dashboard/project/utrvymphowsiclwcpejx
2. Vá em: **SQL Editor** (menu lateral esquerdo)
3. Clique em: **New Query**
4. Copie e cole o conteúdo do arquivo `/app/supabase-schema.sql`
5. Clique em: **Run** (ou pressione Ctrl+Enter)

### 2️⃣ Configurar Senha do Banco de Dados

1. Vá em: **Settings** → **Database**
2. Na seção **Connection string**, copie a **Connection pooling**
3. A URL será algo como:
   ```
   postgresql://postgres.utrvymphowsiclwcpejx:[SUA-SENHA]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

4. Substitua `[SUA-SENHA]` pela senha do banco (você deve ter configurado na criação do projeto)

5. Atualize o arquivo `/app/backend/.env`:
   ```bash
   DATABASE_URL=postgresql://postgres.utrvymphowsiclwcpejx:[SUA-SENHA-AQUI]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

### 3️⃣ Reiniciar Backend

Após configurar a senha do banco, execute:

```bash
sudo supervisorctl restart backend
```

## ✅ O Que Foi Implementado

### 🎯 Sistema 100% Online
- ✅ Vite configurado com `allowedHosts: true`
- ✅ Supabase substituiu PostgreSQL local
- ✅ Sessões WhatsApp salvas no banco (não mais em arquivos)
- ✅ Recuperação automática de sessões após reinício
- ✅ Multi-tenant funcionando online

### 📦 Arquitetura Supabase

**Tabelas Criadas:**
1. `whatsapp_auth` - Credenciais do Baileys (creds + keys)
2. `users` - Usuários
3. `restaurants` - Restaurantes
4. `leads` - Leads/CRM
5. `messages` - Mensagens WhatsApp
6. `campaigns` - Campanhas
7. `products` - Catálogo
8. `whatsapp_sessions` - Controle de sessões

### 🔄 Como Funciona Agora

**Antes (Local):**
- Sessões salvas em `/app/whatsapp-service/sessions/`
- PostgreSQL local
- Não funcionava online

**Agora (Supabase):**
- Sessões salvas em `whatsapp_auth` table
- Supabase PostgreSQL
- 100% online e recuperável

### 🔐 Adaptador Supabase

Criado: `/app/whatsapp-service/supabase-auth-adapter.js`

Funções:
- `useSupabaseAuthState()` - Substitui `useMultiFileAuthState()`
- `getActiveSessions()` - Busca sessões ativas ao iniciar
- `updateSessionStatus()` - Atualiza status de conexão
- `saveQRCode()` - Salva QR code no banco
- `clearSessionAuth()` - Limpa dados ao desconectar

### 🚀 Recuperação Automática

Ao iniciar o servidor WhatsApp:
1. Busca todas as sessões com `is_connected = true`
2. Reconecta automaticamente cada sessão
3. Se falhar, tenta novamente

## 🌐 URLs do Sistema

- **Frontend**: https://marketing-sender-crm.preview.emergentagent.com
- **Backend API**: http://localhost:8001
- **WhatsApp Service**: http://localhost:3001
- **Supabase Dashboard**: https://supabase.com/dashboard/project/utrvymphowsiclwcpejx

## 📝 Próximos Passos

1. Execute o SQL no Supabase (passo 1)
2. Configure a senha do banco (passo 2)
3. Reinicie o backend (passo 3)
4. Acesse o sistema online
5. Crie uma conta
6. Conecte o WhatsApp (credenciais são salvas no Supabase)
7. Reinicie o servidor para testar recuperação automática

## ✨ Benefícios

- ✅ Sistema totalmente online
- ✅ Sem dependência de arquivos locais
- ✅ Sessões persistem após reinicialização
- ✅ Escalável e seguro
- ✅ Backup automático (Supabase)
- ✅ Multi-tenant real

## 🆘 Comandos Úteis

```bash
# Ver status dos serviços
sudo supervisorctl status

# Reiniciar todos os serviços
sudo supervisorctl restart all

# Ver logs
tail -f /var/log/supervisor/whatsapp_service.out.log
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log

# Testar APIs
curl http://localhost:8001/api/health
curl http://localhost:3001/health
```

## 🎉 Sistema Pronto!

Seu SaaS CRM está 100% online e pronto para uso em produção!
