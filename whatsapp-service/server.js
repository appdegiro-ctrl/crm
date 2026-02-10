import express from 'express';
import cors from 'cors';
import { Server } from 'socket.io';
import { createServer } from 'http';
import makeWASocket, { 
    DisconnectReason, 
    fetchLatestBaileysVersion
} from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import QRCode from 'qrcode';
import P from 'pino';
import dotenv from 'dotenv';
import {
    useSupabaseAuthState,
    getActiveSessions,
    updateSessionStatus,
    saveQRCode,
    clearSessionAuth
} from './supabase-auth-adapter.js';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST']
    }
});

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

// Logger
const logger = P({ level: 'info' });

// Armazenar sessões ativas
const sessions = new Map();

// Garantir que o diretório de sessões existe
const sessionsDir = path.join(__dirname, 'sessions');
if (!fs.existsSync(sessionsDir)) {
    fs.mkdirSync(sessionsDir, { recursive: true });
}

// Função para criar uma sessão do WhatsApp
async function createWhatsAppSession(restaurantId, phoneNumber) {
    try {
        const sessionPath = path.join(sessionsDir, restaurantId);
        
        // Criar diretório da sessão se não existir
        if (!fs.existsSync(sessionPath)) {
            fs.mkdirSync(sessionPath, { recursive: true });
        }

        const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
        const { version } = await fetchLatestBaileysVersion();

        const sock = makeWASocket({
            version,
            logger,
            printQRInTerminal: false,
            auth: state,
            getMessage: async (key) => {
                // Implementar lógica para recuperar mensagens do banco de dados
                return { conversation: 'Mensagem não encontrada' };
            }
        });

        let qrCode = null;
        let isConnected = false;

        // Eventos do socket
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                // Gerar QR Code
                qrCode = await QRCode.toDataURL(qr);
                
                // Emitir QR Code via Socket.IO
                io.to(restaurantId).emit('qr', { qrCode });
                
                logger.info(`QR Code gerado para restaurante ${restaurantId}`);
            }

            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error instanceof Boom) &&
                    lastDisconnect.error.output?.statusCode !== DisconnectReason.loggedOut;

                logger.info(`Conexão fechada para ${restaurantId}, reconectando: ${shouldReconnect}`);

                if (shouldReconnect) {
                    setTimeout(() => createWhatsAppSession(restaurantId, phoneNumber), 3000);
                } else {
                    sessions.delete(restaurantId);
                }

                isConnected = false;
                io.to(restaurantId).emit('disconnected');
            } else if (connection === 'open') {
                logger.info(`Conexão aberta para restaurante ${restaurantId}`);
                isConnected = true;
                qrCode = null;
                io.to(restaurantId).emit('connected', { phoneNumber: sock.user?.id });
            }
        });

        // Evento de atualização de credenciais
        sock.ev.on('creds.update', saveCreds);

        // Evento de mensagens
        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            try {
                for (const msg of messages) {
                    if (!msg.message) continue;

                    const messageData = {
                        id: msg.key.id,
                        from: msg.key.remoteJid,
                        timestamp: msg.messageTimestamp,
                        message: msg.message,
                        fromMe: msg.key.fromMe
                    };

                    // Emitir mensagem via Socket.IO
                    io.to(restaurantId).emit('message', messageData);

                    // Aqui você pode enviar para o backend para salvar no banco
                    // await saveMessageToBackend(restaurantId, messageData);

                    logger.info(`Mensagem recebida para ${restaurantId}: ${msg.key.id}`);
                }
            } catch (error) {
                logger.error(`Erro ao processar mensagem: ${error.message}`);
            }
        });

        // Salvar sessão
        sessions.set(restaurantId, {
            sock,
            qrCode,
            isConnected,
            phoneNumber
        });

        return {
            success: true,
            session_id: restaurantId,
            qr_code: qrCode,
            is_connected: isConnected
        };

    } catch (error) {
        logger.error(`Erro ao criar sessão: ${error.message}`);
        throw error;
    }
}

// Função para enviar mensagem
async function sendMessage(restaurantId, to, message) {
    const session = sessions.get(restaurantId);
    
    if (!session || !session.isConnected) {
        throw new Error('Sessão não conectada');
    }

    try {
        // Garantir que o número está no formato correto
        const jid = to.includes('@s.whatsapp.net') ? to : `${to}@s.whatsapp.net`;
        
        await session.sock.sendMessage(jid, { text: message });
        
        return { success: true, message: 'Mensagem enviada' };
    } catch (error) {
        logger.error(`Erro ao enviar mensagem: ${error.message}`);
        throw error;
    }
}

// Rotas da API
app.post('/session/create', async (req, res) => {
    try {
        const { restaurant_id, phone_number } = req.body;

        if (!restaurant_id || !phone_number) {
            return res.status(400).json({
                error: 'restaurant_id and phone_number are required'
            });
        }

        // Verificar se já existe uma sessão
        if (sessions.has(restaurant_id)) {
            const session = sessions.get(restaurant_id);
            return res.json({
                session_id: restaurant_id,
                qr_code: session.qrCode,
                is_connected: session.isConnected
            });
        }

        const result = await createWhatsAppSession(restaurant_id, phone_number);
        res.json(result);

    } catch (error) {
        logger.error(`Erro ao criar sessão: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

app.get('/session/status/:session_id', (req, res) => {
    const { session_id } = req.params;
    const session = sessions.get(session_id);

    if (!session) {
        return res.status(404).json({ error: 'Sessão não encontrada' });
    }

    res.json({
        session_id,
        is_connected: session.isConnected,
        qr_code: session.qrCode,
        phone_number: session.phoneNumber
    });
});

app.delete('/session/:session_id', async (req, res) => {
    const { session_id } = req.params;
    const session = sessions.get(session_id);

    if (!session) {
        return res.status(404).json({ error: 'Sessão não encontrada' });
    }

    try {
        // Fazer logout
        await session.sock.logout();
        
        // Remover sessão
        sessions.delete(session_id);

        // Deletar arquivos da sessão
        const sessionPath = path.join(sessionsDir, session_id);
        if (fs.existsSync(sessionPath)) {
            fs.rmSync(sessionPath, { recursive: true, force: true });
        }

        res.json({ success: true, message: 'Sessão deletada' });
    } catch (error) {
        logger.error(`Erro ao deletar sessão: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

app.post('/message/send', async (req, res) => {
    try {
        const { restaurant_id, to, message } = req.body;

        if (!restaurant_id || !to || !message) {
            return res.status(400).json({
                error: 'restaurant_id, to, and message are required'
            });
        }

        const result = await sendMessage(restaurant_id, to, message);
        res.json(result);

    } catch (error) {
        logger.error(`Erro ao enviar mensagem: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        active_sessions: sessions.size
    });
});

// Socket.IO para conexões em tempo real
io.on('connection', (socket) => {
    logger.info(`Cliente conectado: ${socket.id}`);

    socket.on('subscribe', (restaurantId) => {
        socket.join(restaurantId);
        logger.info(`Cliente ${socket.id} inscrito no restaurante ${restaurantId}`);
    });

    socket.on('disconnect', () => {
        logger.info(`Cliente desconectado: ${socket.id}`);
    });
});

// Iniciar servidor
httpServer.listen(PORT, () => {
    logger.info(`WhatsApp Service rodando na porta ${PORT}`);
});
