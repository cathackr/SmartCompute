#!/usr/bin/env node
/**
 * SmartCompute Industrial - Sistema de Flujo de Aprobaciones Node.js
 * Desarrollado por: ggwre04p0@mozmail.com
 * LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/
 *
 * Módulo Node.js para procesamiento asíncrono de aprobaciones,
 * notificaciones y aprendizaje continuo de la IA.
 */

const express = require('express');
const WebSocket = require('ws');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const jwt = require('jsonwebtoken');

class SmartComputeApprovalSystem {
    constructor() {
        this.app = express();
        this.port = 3000;
        this.wss = null;
        this.clients = new Map();

        // Configuración
        this.config = {
            jwtSecret: process.env.JWT_SECRET || 'smartcompute-secret-key',
            emailConfig: {
                host: 'smtp.gmail.com',
                port: 587,
                secure: false,
                auth: {
                    user: process.env.EMAIL_USER || 'smartcompute@empresa.com',
                    pass: process.env.EMAIL_PASS || 'password'
                }
            }
        };

        // Bases de datos en memoria (en producción usar BD real)
        this.approvalWorkflows = new Map();
        this.approvers = new Map();
        this.notifications = new Map();
        this.aiLearningData = new Map();

        this.initializeServer();
        this.initializeApprovers();
    }

    initializeServer() {
        // Middleware
        this.app.use(express.json());
        this.app.use(express.static('public'));

        // CORS
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Authorization, Content-Type');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
            next();
        });

        // Rutas
        this.setupRoutes();

        // WebSocket Server
        const server = this.app.listen(this.port, () => {
            console.log(`🚀 SmartCompute Approval System ejecutándose en puerto ${this.port}`);
        });

        this.wss = new WebSocket.Server({ server });
        this.setupWebSocket();
    }

    initializeApprovers() {
        // Inicializar aprobadores de ejemplo
        const approvers = [
            {
                id: 'SUP001',
                name: 'Carlos Supervisor',
                email: 'carlos.supervisor@empresa.com',
                level: 2,
                department: 'Mantenimiento',
                phone: '+54911234567',
                active: true
            },
            {
                id: 'JEF001',
                name: 'Ana Jefe Mantenimiento',
                email: 'ana.jefe@empresa.com',
                level: 3,
                department: 'Mantenimiento',
                phone: '+54911234568',
                active: true
            },
            {
                id: 'DIR001',
                name: 'Roberto Director Técnico',
                email: 'roberto.director@empresa.com',
                level: 4,
                department: 'Dirección',
                phone: '+54911234569',
                active: true
            }
        ];

        approvers.forEach(approver => {
            this.approvers.set(approver.id, approver);
        });

        console.log(`✅ ${approvers.length} aprobadores inicializados`);
    }

    setupRoutes() {
        // Ruta de salud
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime()
            });
        });

        // Crear workflow de aprobación
        this.app.post('/api/workflows', async (req, res) => {
            try {
                const workflow = await this.createApprovalWorkflow(req.body);
                res.json({ success: true, workflow });
            } catch (error) {
                res.status(400).json({ error: error.message });
            }
        });

        // Obtener workflow
        this.app.get('/api/workflows/:id', (req, res) => {
            const workflow = this.approvalWorkflows.get(req.params.id);
            if (!workflow) {
                return res.status(404).json({ error: 'Workflow no encontrado' });
            }
            res.json(workflow);
        });

        // Aprobar/rechazar workflow
        this.app.post('/api/workflows/:id/decision', async (req, res) => {
            try {
                const result = await this.processApprovalDecision(req.params.id, req.body);
                res.json({ success: true, result });
            } catch (error) {
                res.status(400).json({ error: error.message });
            }
        });

        // Obtener workflows pendientes para un aprobador
        this.app.get('/api/approvers/:id/pending', (req, res) => {
            const pending = this.getPendingWorkflowsForApprover(req.params.id);
            res.json(pending);
        });

        // Enviar datos de aprendizaje de IA
        this.app.post('/api/ai/learning', async (req, res) => {
            try {
                await this.processAILearningData(req.body);
                res.json({ success: true });
            } catch (error) {
                res.status(400).json({ error: error.message });
            }
        });

        // Obtener estadísticas del sistema
        this.app.get('/api/stats', (req, res) => {
            const stats = this.getSystemStats();
            res.json(stats);
        });
    }

    setupWebSocket() {
        this.wss.on('connection', (ws, req) => {
            const clientId = crypto.randomUUID();
            this.clients.set(clientId, { ws, connectedAt: new Date() });

            console.log(`📱 Cliente WebSocket conectado: ${clientId}`);

            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    await this.handleWebSocketMessage(clientId, data);
                } catch (error) {
                    ws.send(JSON.stringify({ error: 'Mensaje inválido' }));
                }
            });

            ws.on('close', () => {
                this.clients.delete(clientId);
                console.log(`📱 Cliente WebSocket desconectado: ${clientId}`);
            });

            // Enviar mensaje de bienvenida
            ws.send(JSON.stringify({
                type: 'welcome',
                clientId,
                timestamp: new Date().toISOString()
            }));
        });
    }

    async handleWebSocketMessage(clientId, data) {
        const client = this.clients.get(clientId);
        if (!client) return;

        switch (data.type) {
            case 'subscribe_approvals':
                client.subscribedTo = 'approvals';
                client.approverId = data.approverId;
                break;

            case 'heartbeat':
                client.ws.send(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
                break;

            default:
                client.ws.send(JSON.stringify({ error: 'Tipo de mensaje no reconocido' }));
        }
    }

    async createApprovalWorkflow(workflowData) {
        const workflowId = `WF-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;

        const workflow = {
            id: workflowId,
            requestId: workflowData.requestId,
            operatorId: workflowData.operatorId,
            title: workflowData.title,
            description: workflowData.description,
            actions: workflowData.actions,
            requiredLevel: workflowData.requiredLevel,
            urgency: workflowData.urgency || 'medium',
            status: 'pending',
            createdAt: new Date(),
            approvals: [],
            notifications: [],
            estimatedImpact: workflowData.estimatedImpact || {},
            riskAssessment: workflowData.riskAssessment || {}
        };

        this.approvalWorkflows.set(workflowId, workflow);

        // Identificar aprobadores elegibles
        const eligibleApprovers = this.getEligibleApprovers(workflow.requiredLevel);
        workflow.eligibleApprovers = eligibleApprovers;

        // Enviar notificaciones
        await this.sendApprovalNotifications(workflow);

        // Notificar via WebSocket
        this.broadcastToSubscribedClients('new_approval_request', workflow);

        console.log(`📋 Workflow de aprobación creado: ${workflowId}`);

        return workflow;
    }

    async processApprovalDecision(workflowId, decision) {
        const workflow = this.approvalWorkflows.get(workflowId);
        if (!workflow) {
            throw new Error('Workflow no encontrado');
        }

        if (workflow.status !== 'pending') {
            throw new Error('Workflow ya procesado');
        }

        const approval = {
            approverId: decision.approverId,
            decision: decision.decision, // 'approved' | 'rejected'
            comments: decision.comments || '',
            timestamp: new Date(),
            approverInfo: this.approvers.get(decision.approverId)
        };

        workflow.approvals.push(approval);

        // Determinar estado final
        if (decision.decision === 'rejected') {
            workflow.status = 'rejected';
            workflow.rejectedBy = approval.approverInfo.name;
            workflow.rejectionReason = decision.comments;
        } else if (decision.decision === 'approved') {
            // Verificar si cumple requisitos de aprobación
            const approverLevel = approval.approverInfo.level;
            if (approverLevel >= workflow.requiredLevel) {
                workflow.status = 'approved';
                workflow.approvedBy = approval.approverInfo.name;
                workflow.approvedAt = new Date();
            } else {
                // Necesita aprobación de nivel superior
                workflow.status = 'partial_approval';
            }
        }

        this.approvalWorkflows.set(workflowId, workflow);

        // Enviar notificaciones de decisión
        await this.sendDecisionNotifications(workflow, approval);

        // Notificar via WebSocket
        this.broadcastToSubscribedClients('approval_decision', { workflow, decision: approval });

        // Registrar para aprendizaje de IA
        await this.recordApprovalDecisionForAI(workflow, approval);

        console.log(`✅ Decisión procesada para workflow ${workflowId}: ${decision.decision}`);

        return { workflow, approval };
    }

    getEligibleApprovers(requiredLevel) {
        const eligible = [];
        for (const [id, approver] of this.approvers) {
            if (approver.active && approver.level >= requiredLevel) {
                eligible.push(approver);
            }
        }
        return eligible.sort((a, b) => a.level - b.level); // Menor nivel primero
    }

    async sendApprovalNotifications(workflow) {
        const notifications = [];

        for (const approver of workflow.eligibleApprovers) {
            const notification = {
                id: crypto.randomUUID(),
                workflowId: workflow.id,
                approverId: approver.id,
                type: 'approval_request',
                title: `Aprobación Requerida: ${workflow.title}`,
                message: this.generateApprovalNotificationMessage(workflow),
                createdAt: new Date(),
                status: 'sent'
            };

            notifications.push(notification);
            this.notifications.set(notification.id, notification);

            // Enviar email (simulado)
            await this.sendEmailNotification(approver.email, notification);

            // Enviar notificación push (simulado)
            await this.sendPushNotification(approver.phone, notification);
        }

        workflow.notifications = notifications;
        return notifications;
    }

    generateApprovalNotificationMessage(workflow) {
        return `
Se requiere su aprobación para las siguientes acciones:

Título: ${workflow.title}
Descripción: ${workflow.description}
Nivel requerido: ${workflow.requiredLevel}
Urgencia: ${workflow.urgency}

Acciones propuestas:
${workflow.actions.map((action, i) => `${i + 1}. ${action.action} (${action.priority})`).join('\n')}

Evaluación de riesgo:
- Operacional: ${workflow.riskAssessment.operational || 'No especificado'}
- Seguridad: ${workflow.riskAssessment.safety || 'No especificado'}

Por favor acceda al sistema SmartCompute para revisar y aprobar.
        `;
    }

    async sendEmailNotification(email, notification) {
        // Simulación de envío de email
        console.log(`📧 Email enviado a ${email}: ${notification.title}`);

        // En implementación real:
        /*
        const transporter = nodemailer.createTransporter(this.config.emailConfig);
        await transporter.sendMail({
            from: 'smartcompute@empresa.com',
            to: email,
            subject: notification.title,
            text: notification.message
        });
        */
    }

    async sendPushNotification(phone, notification) {
        // Simulación de notificación push
        console.log(`📱 Push notification enviada a ${phone}: ${notification.title}`);
    }

    async sendDecisionNotifications(workflow, approval) {
        const notificationMessage = `
Decisión tomada en workflow: ${workflow.title}

Decisión: ${approval.decision.toUpperCase()}
Por: ${approval.approverInfo.name}
Fecha: ${approval.timestamp.toLocaleString()}

${approval.comments ? `Comentarios: ${approval.comments}` : ''}

Estado actual: ${workflow.status}
        `;

        // Notificar al operador original
        console.log(`📧 Notificación de decisión enviada para workflow ${workflow.id}`);
    }

    getPendingWorkflowsForApprover(approverId) {
        const pending = [];
        for (const [id, workflow] of this.approvalWorkflows) {
            if (workflow.status === 'pending' || workflow.status === 'partial_approval') {
                const canApprove = workflow.eligibleApprovers.some(a => a.id === approverId);
                if (canApprove) {
                    pending.push(workflow);
                }
            }
        }
        return pending.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    broadcastToSubscribedClients(eventType, data) {
        for (const [clientId, client] of this.clients) {
            if (client.subscribedTo === 'approvals') {
                try {
                    client.ws.send(JSON.stringify({
                        type: eventType,
                        data,
                        timestamp: new Date().toISOString()
                    }));
                } catch (error) {
                    console.log(`❌ Error enviando mensaje a cliente ${clientId}:`, error.message);
                }
            }
        }
    }

    async processAILearningData(learningData) {
        const dataId = crypto.randomUUID();

        const aiData = {
            id: dataId,
            type: learningData.type,
            context: learningData.context,
            decision: learningData.decision,
            outcome: learningData.outcome,
            timestamp: new Date(),
            feedback: learningData.feedback || {},
            metadata: learningData.metadata || {}
        };

        this.aiLearningData.set(dataId, aiData);

        // Procesar datos para mejorar recomendaciones futuras
        await this.updateAIModels(aiData);

        console.log(`🧠 Datos de aprendizaje procesados: ${learningData.type}`);

        return aiData;
    }

    async updateAIModels(aiData) {
        // Simulación de actualización de modelos de IA
        // En implementación real, esto alimentaría los modelos ML

        const patterns = {
            approval_patterns: this.analyzeApprovalPatterns(),
            failure_modes: this.analyzeFailureModes(),
            success_factors: this.analyzeSuccessFactors()
        };

        console.log('🤖 Modelos de IA actualizados con nuevos datos');
        return patterns;
    }

    analyzeApprovalPatterns() {
        const approvals = Array.from(this.approvalWorkflows.values())
            .filter(wf => wf.status === 'approved');

        return {
            total_approved: approvals.length,
            avg_approval_time: this.calculateAverageApprovalTime(approvals),
            common_action_types: this.getCommonActionTypes(approvals)
        };
    }

    analyzeFailureModes() {
        const rejected = Array.from(this.approvalWorkflows.values())
            .filter(wf => wf.status === 'rejected');

        return {
            total_rejected: rejected.length,
            common_rejection_reasons: this.getCommonRejectionReasons(rejected)
        };
    }

    analyzeSuccessFactors() {
        return {
            high_confidence_threshold: 0.85,
            preferred_approval_levels: [3, 4],
            optimal_urgency_handling: 'medium'
        };
    }

    calculateAverageApprovalTime(approvals) {
        if (approvals.length === 0) return 0;

        const totalTime = approvals.reduce((sum, wf) => {
            if (wf.approvedAt && wf.createdAt) {
                return sum + (new Date(wf.approvedAt) - new Date(wf.createdAt));
            }
            return sum;
        }, 0);

        return totalTime / approvals.length / (1000 * 60); // minutos
    }

    getCommonActionTypes(workflows) {
        const actionTypes = {};
        workflows.forEach(wf => {
            wf.actions.forEach(action => {
                const type = action.action.split(' ')[0]; // Primera palabra
                actionTypes[type] = (actionTypes[type] || 0) + 1;
            });
        });
        return actionTypes;
    }

    getCommonRejectionReasons(rejected) {
        const reasons = {};
        rejected.forEach(wf => {
            if (wf.rejectionReason) {
                const key = wf.rejectionReason.substring(0, 50); // Primeras 50 chars
                reasons[key] = (reasons[key] || 0) + 1;
            }
        });
        return reasons;
    }

    getSystemStats() {
        const totalWorkflows = this.approvalWorkflows.size;
        const pending = Array.from(this.approvalWorkflows.values()).filter(wf => wf.status === 'pending').length;
        const approved = Array.from(this.approvalWorkflows.values()).filter(wf => wf.status === 'approved').length;
        const rejected = Array.from(this.approvalWorkflows.values()).filter(wf => wf.status === 'rejected').length;

        return {
            total_workflows: totalWorkflows,
            pending_approvals: pending,
            approved: approved,
            rejected: rejected,
            approval_rate: totalWorkflows > 0 ? (approved / totalWorkflows * 100).toFixed(1) + '%' : '0%',
            active_clients: this.clients.size,
            active_approvers: this.approvers.size,
            uptime: process.uptime(),
            ai_learning_records: this.aiLearningData.size
        };
    }

    // Método para limpiar datos antiguos
    async cleanupOldData() {
        const cutoffDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 días

        let cleaned = 0;
        for (const [id, workflow] of this.approvalWorkflows) {
            if (new Date(workflow.createdAt) < cutoffDate && workflow.status !== 'pending') {
                this.approvalWorkflows.delete(id);
                cleaned++;
            }
        }

        console.log(`🧹 Limpieza completada: ${cleaned} workflows antiguos eliminados`);
    }
}

// Función principal
async function main() {
    console.log('=== SmartCompute Industrial - Sistema de Aprobaciones Node.js ===');
    console.log('Desarrollado por: ggwre04p0@mozmail.com');
    console.log('LinkedIn: https://www.linkedin.com/in/martín-iribarne-swtf/');
    console.log();

    const approvalSystem = new SmartComputeApprovalSystem();

    // Programar limpieza diaria
    setInterval(() => {
        approvalSystem.cleanupOldData();
    }, 24 * 60 * 60 * 1000); // 24 horas

    // Manejar señales de sistema
    process.on('SIGINT', () => {
        console.log('\n🛑 Cerrando sistema de aprobaciones...');
        process.exit(0);
    });

    process.on('uncaughtException', (error) => {
        console.error('❌ Error no capturado:', error);
    });

    console.log('✅ Sistema de aprobaciones iniciado correctamente');
    console.log('📱 WebSocket disponible para notificaciones en tiempo real');
    console.log('🌐 API REST disponible en http://localhost:3000');
}

// Ejecutar si es el archivo principal
if (require.main === module) {
    main().catch(console.error);
}

module.exports = SmartComputeApprovalSystem;