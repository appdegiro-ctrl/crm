import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Adaptador para salvar credenciais e keys do Baileys no Supabase
 * Substitui o useMultiFileAuthState para funcionar 100% online
 */
export async function useSupabaseAuthState(sessionId) {
    // Função para buscar credenciais do banco
    const readData = async (key) => {
        try {
            const { data, error } = await supabase
                .from('whatsapp_auth')
                .select('value')
                .eq('session_id', sessionId)
                .eq('key', key)
                .single();

            if (error || !data) return null;
            return JSON.parse(data.value);
        } catch (err) {
            return null;
        }
    };

    // Função para salvar dados no banco
    const writeData = async (key, value) => {
        try {
            const { error } = await supabase
                .from('whatsapp_auth')
                .upsert({
                    session_id: sessionId,
                    key: key,
                    value: JSON.stringify(value),
                    updated_at: new Date().toISOString()
                }, {
                    onConflict: 'session_id,key'
                });

            if (error) {
                console.error('Error writing to Supabase:', error);
            }
        } catch (err) {
            console.error('Error in writeData:', err);
        }
    };

    // Função para remover dados
    const removeData = async (key) => {
        try {
            await supabase
                .from('whatsapp_auth')
                .delete()
                .eq('session_id', sessionId)
                .eq('key', key);
        } catch (err) {
            console.error('Error removing data:', err);
        }
    };

    // Carregar credenciais
    const creds = await readData('creds') || {};

    // Criar state object compatível com Baileys
    const state = {
        creds: creds,
        keys: {
            get: async (type, ids) => {
                const data = {};
                for (const id of ids) {
                    const key = `key-${type}-${id}`;
                    const value = await readData(key);
                    if (value) {
                        data[id] = value;
                    }
                }
                return data;
            },
            set: async (data) => {
                for (const category in data) {
                    for (const id in data[category]) {
                        const value = data[category][id];
                        const key = `key-${category}-${id}`;
                        if (value) {
                            await writeData(key, value);
                        } else {
                            await removeData(key);
                        }
                    }
                }
            }
        }
    };

    // Função para salvar credenciais
    const saveCreds = async () => {
        await writeData('creds', state.creds);
    };

    return {
        state,
        saveCreds
    };
}

/**
 * Buscar todas as sessões ativas do banco
 */
export async function getActiveSessions() {
    try {
        const { data, error } = await supabase
            .from('whatsapp_sessions')
            .select('*')
            .eq('is_connected', true);

        if (error) {
            console.error('Error fetching sessions:', error);
            return [];
        }

        return data || [];
    } catch (err) {
        console.error('Error in getActiveSessions:', err);
        return [];
    }
}

/**
 * Atualizar status da sessão
 */
export async function updateSessionStatus(restaurantId, isConnected, phoneNumber = null) {
    try {
        const updateData = {
            is_connected: isConnected,
            updated_at: new Date().toISOString()
        };

        if (isConnected) {
            updateData.last_connected_at = new Date().toISOString();
        }

        if (phoneNumber) {
            updateData.phone_number = phoneNumber;
        }

        const { error } = await supabase
            .from('whatsapp_sessions')
            .update(updateData)
            .eq('restaurant_id', restaurantId);

        if (error) {
            console.error('Error updating session status:', error);
        }
    } catch (err) {
        console.error('Error in updateSessionStatus:', err);
    }
}

/**
 * Salvar QR Code
 */
export async function saveQRCode(restaurantId, qrCode) {
    try {
        await supabase
            .from('whatsapp_sessions')
            .update({
                qr_code: qrCode,
                updated_at: new Date().toISOString()
            })
            .eq('restaurant_id', restaurantId);
    } catch (err) {
        console.error('Error saving QR code:', err);
    }
}

/**
 * Limpar dados de autenticação da sessão
 */
export async function clearSessionAuth(sessionId) {
    try {
        await supabase
            .from('whatsapp_auth')
            .delete()
            .eq('session_id', sessionId);
    } catch (err) {
        console.error('Error clearing session auth:', err);
    }
}

export default {
    useSupabaseAuthState,
    getActiveSessions,
    updateSessionStatus,
    saveQRCode,
    clearSessionAuth
};
