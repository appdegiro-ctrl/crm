-- Tabela para armazenar credenciais e keys do Baileys
CREATE TABLE IF NOT EXISTS whatsapp_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, key)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_auth_session ON whatsapp_auth(session_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_auth_key ON whatsapp_auth(key);

-- Comentários
COMMENT ON TABLE whatsapp_auth IS 'Armazena credenciais e chaves de autenticação do WhatsApp (Baileys)';
COMMENT ON COLUMN whatsapp_auth.session_id IS 'ID da sessão (normalmente restaurant_id)';
COMMENT ON COLUMN whatsapp_auth.key IS 'Chave do dado (creds, key-type-id, etc)';
COMMENT ON COLUMN whatsapp_auth.value IS 'Valor do dado em formato JSON';

-- Se as tabelas já existem do PostgreSQL local, você pode usar estas migrações:
-- Caso contrário, execute o schema completo abaixo:

-- Criar todas as tabelas se ainda não existirem
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superadmin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS restaurants (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    name TEXT NOT NULL,
    description TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    status TEXT DEFAULT 'new',
    notes TEXT,
    whatsapp_id TEXT,
    restaurant_id TEXT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    whatsapp_message_id TEXT,
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    media_url TEXT,
    is_from_me BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'sent',
    restaurant_id TEXT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    name TEXT NOT NULL,
    description TEXT,
    message_template TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    target_count INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    read_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    restaurant_id TEXT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC NOT NULL,
    image_url TEXT,
    category TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    restaurant_id TEXT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS whatsapp_sessions (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    restaurant_id TEXT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE UNIQUE,
    phone_number TEXT NOT NULL,
    session_id TEXT UNIQUE,
    qr_code TEXT,
    is_connected BOOLEAN DEFAULT FALSE,
    last_connected_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_restaurants_owner ON restaurants(owner_id);
CREATE INDEX IF NOT EXISTS idx_leads_restaurant ON leads(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_messages_restaurant ON messages(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_restaurant ON campaigns(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_products_restaurant ON products(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_sessions_restaurant ON whatsapp_sessions(restaurant_id);

-- Comentários nas tabelas
COMMENT ON TABLE users IS 'Usuários do sistema SaaS';
COMMENT ON TABLE restaurants IS 'Restaurantes gerenciados (multi-tenant)';
COMMENT ON TABLE leads IS 'Leads/Clientes do CRM';
COMMENT ON TABLE messages IS 'Histórico de mensagens do WhatsApp';
COMMENT ON TABLE campaigns IS 'Campanhas de marketing';
COMMENT ON TABLE products IS 'Catálogo de produtos';
COMMENT ON TABLE whatsapp_sessions IS 'Sessões ativas do WhatsApp';
