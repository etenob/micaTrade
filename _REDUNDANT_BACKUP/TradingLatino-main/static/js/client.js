/**
 * Cliente JavaScript avanzado para Jaime Merino Trading Bot
 * Metodología Trading Latino - Análisis Técnico Avanzado
 */

class MerinoTradingClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.symbolsData = new Map();
        this.notifications = [];
        this.settings = {
            autoRefresh: true,
            refreshInterval: 30000,
            soundAlerts: true,
            highProbabilityThreshold: 70,
            showOnlyHighProbability: false,
            favoriteSymbols: ['BTCUSDT', 'ETHUSDT']
        };
        this.chartInstances = new Map();
        this.intervalIds = [];
        
        this.initialize();
    }

    /**
     * Inicializa el cliente
     */
    initialize() {
        console.log('🚀 Inicializando Jaime Merino Trading Client');
        this.loadSettings();
        this.initializeSocket();
        this.setupEventListeners();
        this.startPeriodicTasks();
        
        // Mostrar filosofía inicial
        this.showPhilosophyMessage();
    }

    /**
     * Inicializa la conexión Socket.IO
     */
    initializeSocket() {
        this.socket = io({
            transports: ['websocket', 'polling'],
            timeout: 20000,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5
        });

        // Eventos de conexión
        this.socket.on('connect', () => {
            this.connected = true;
            this.onConnect();
        });

        this.socket.on('disconnect', (reason) => {
            this.connected = false;
            this.onDisconnect(reason);
        });

        this.socket.on('connect_error', (error) => {
            console.error('❌ Error de conexión:', error);
            this.showNotification('Error de conexión al servidor', 'error');
        });

        // Eventos específicos de Merino
        this.setupMerinoSocketEvents();
    }

    /**
     * Configura eventos específicos de la metodología Merino
     */
    setupMerinoSocketEvents() {
        // Bienvenida con metodología
        this.socket.on('merino_welcome', (data) => {
            console.log('📈 Metodología Merino cargada:', data);
            this.showNotification(`Bienvenido - ${data.philosophy}`, 'success');
            this.updateServerInfo(data);
        });

        // Actualización de análisis
        this.socket.on('merino_analysis_update', (data) => {
            this.handleAnalysisUpdate(data);
        });

        // Análisis masivo iniciado
        this.socket.on('merino_bulk_analysis_started', (data) => {
            this.showNotification(`Analizando ${data.total} símbolos según Metodología Merino...`, 'info');
            this.showBulkAnalysisProgress(0, data.total);
        });

        // Análisis masivo completado
        this.socket.on('merino_bulk_analysis_completed', (data) => {
            const message = `✅ Análisis completado: ${data.high_probability_signals} señales de alta probabilidad`;
            this.showNotification(message, 'success');
            this.hideBulkAnalysisProgress();
            
            if (data.high_probability_signals > 0) {
                this.playAlertSound();
            }
        });

        // Estado del servidor
        this.socket.on('merino_server_status', (data) => {
            this.updateServerStatus(data);
        });

        // Precio de Bitcoin
        this.socket.on('btc_price_update', (data) => {
            this.updateBTCPrice(data.price);
        });

        // Sentimiento de mercado
        this.socket.on('market_sentiment', (data) => {
            this.updateMarketSentiment(data.sentiment);
        });

        // Filosofía de Merino
        this.socket.on('merino_philosophy', (data) => {
            this.showPhilosophyModal(data);
        });

        // Cálculo de riesgo
        this.socket.on('risk_calculation', (data) => {
            this.showRiskCalculation(data);
        });

        // Recordatorio filosófico
        this.socket.on('philosophy_reminder', (data) => {
            this.showPhilosophyReminder(data.message);
        });

        // Alertas de mercado
        this.socket.on('market_alert', (data) => {
            this.handleMarketAlert(data);
        });

        // Errores
        this.socket.on('merino_analysis_error', (data) => {
            console.error('❌ Error análisis:', data);
            this.showNotification(`Error analizando ${data.symbol}: ${data.error}`, 'error');
        });
    }

    /**
     * Maneja la conexión exitosa
     */
    onConnect() {
        console.log('✅ Conectado al servidor Merino');
        this.showNotification('Conectado - Metodología Jaime Merino activa', 'success');
        this.updateConnectionStatus(true);
        
        // Solicitar estado inicial
        this.requestServerStatus();
        
        // Configurar preferencias del cliente
        this.sendClientPreferences();
    }

    /**
     * Maneja la desconexión
     */
    onDisconnect(reason) {
        console.warn('❌ Desconectado:', reason);
        this.showNotification('Desconectado del servidor', 'warning');
        this.updateConnectionStatus(false);
        
        if (reason === 'io server disconnect') {
            // Reconnect manually if server disconnected
            this.socket.connect();
        }
    }

    /**
     * Maneja actualizaciones de análisis
     */
    handleAnalysisUpdate(data) {
        const { symbol, data: analysisData, high_probability, cached } = data;
        
        // Actualizar datos locales
        this.symbolsData.set(symbol, {
            ...analysisData,
            timestamp: Date.now(),
            high_probability,
            cached
        });

        // Actualizar UI
        this.updateSymbolCard(symbol, analysisData);
        
        // Notificaciones para señales importantes
        if (high_probability && !cached && this.settings.soundAlerts) {
            const signal = analysisData.signal?.signal || 'UNKNOWN';
            const strength = analysisData.signal?.signal_strength || 0;
            
            this.showNotification(
                `🎯 ALTA PROBABILIDAD: ${symbol} - ${signal} (${strength}%)`,
                'warning'
            );
            
            this.playAlertSound();
            this.highlightSymbolCard(symbol);
        }

        // Log para debugging
        console.log(`📊 Análisis actualizado: ${symbol}`, analysisData);
    }

    /**
     * Actualiza la tarjeta de un símbolo
     */
    updateSymbolCard(symbol, data) {
        let card = document.getElementById(`symbol-${symbol}`);
        
        if (!card) {
            card = this.createSymbolCard(symbol);
        }

        const signal = data.signal || {};
        const currentPrice = data.current_price || 0;
        const signalType = signal.signal || 'NO_SIGNAL';
        const signalStrength = signal.signal_strength || 0;
        const confluenceScore = signal.confluence_score || 0;
        
        // Determinar clase CSS para el tipo de señal
        const signalClass = this.getSignalClass(signalType);
        const strengthColor = this.getStrengthColor(signalStrength);
        
        card.innerHTML = `
            <div class="symbol-header">
                <div class="symbol-name">${symbol}</div>
                <div class="signal-badge ${signalClass}">${signalType}</div>
                ${signalStrength >= this.settings.highProbabilityThreshold ? '<div class="high-probability-indicator">🎯</div>' : ''}
            </div>
            
            <div class="symbol-price">
                <span class="price-value">$${this.formatPrice(currentPrice)}</span>
            </div>
            
            <div class="symbol-metrics">
                <div class="metric">
                    <span class="metric-label">Fuerza:</span>
                    <span class="metric-value">${signalStrength}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Confluencias:</span>
                    <span class="metric-value">${confluenceScore}/4</span>
                </div>
            </div>
            
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${signalStrength}%; background: ${strengthColor};"></div>
            </div>
            
            <div class="symbol-actions">
                <button class="btn-mini" onclick="merinoClient.requestDetailedAnalysis('${symbol}')">
                    <i class="fas fa-chart-line"></i> Detalles
                </button>
                <button class="btn-mini" onclick="merinoClient.calculateRisk('${symbol}', ${signalStrength})">
                    <i class="fas fa-calculator"></i> Riesgo
                </button>
            </div>
            
            <div class="symbol-timestamp">
                Actualizado: ${new Date().toLocaleTimeString()}
            </div>
        `;

        // Aplicar filtros si están activos
        if (this.settings.showOnlyHighProbability && signalStrength < this.settings.highProbabilityThreshold) {
            card.style.display = 'none';
        } else {
            card.style.display = 'block';
        }
    }

    /**
     * Crea una nueva tarjeta de símbolo
     */
    createSymbolCard(symbol) {
        const container = document.getElementById('symbols-container');
        const card = document.createElement('div');
        card.id = `symbol-${symbol}`;
        card.className = 'symbol-card animate__animated animate__fadeInUp';
        container.appendChild(card);
        return card;
    }

    /**
     * Resalta una tarjeta de símbolo
     */
    highlightSymbolCard(symbol) {
        const card = document.getElementById(`symbol-${symbol}`);
        if (card) {
            card.classList.add('highlight-card');
            setTimeout(() => {
                card.classList.remove('highlight-card');
            }, 3000);
        }
    }

    /**
     * Solicita análisis detallado de un símbolo
     */
    requestDetailedAnalysis(symbol) {
        this.socket.emit('request_merino_analysis', { 
            symbol,
            options: { detailed: true }
        });
        this.showNotification(`Solicitando análisis detallado de ${symbol}...`, 'info');
    }

    /**
     * Calcula el riesgo para un símbolo
     */
    calculateRisk(symbol, signalStrength) {
        const capital = prompt('Ingrese su capital total (USD):', '10000');
        if (capital && !isNaN(capital)) {
            this.socket.emit('request_risk_calculator', {
                symbol,
                signal_strength: signalStrength,
                capital: parseFloat(capital)
            });
        }
    }

    /**
     * Muestra el cálculo de riesgo
     */
    showRiskCalculation(data) {
        const modal = this.createModal('Cálculo de Riesgo - Metodología Merino');
        const calc = data.calculation;
        
        let content = `
            <div class="risk-calculation">
                <h3>📊 Análisis para ${data.input.symbol}</h3>
                <div class="risk-philosophy">
                    <em>"${data.philosophy}"</em>
                </div>
        `;

        if (calc.can_trade) {
            content += `
                <div class="risk-details">
                    <div class="risk-row">
                        <span>💰 Capital Disponible:</span>
                        <span>$${calc.available_capital.toLocaleString()}</span>
                    </div>
                    <div class="risk-row">
                        <span>📊 Tamaño Posición:</span>
                        <span>$${calc.position_size.toLocaleString()} (${calc.position_size_pct.toFixed(2)}%)</span>
                    </div>
                    <div class="risk-row">
                        <span>🛑 Riesgo Máximo:</span>
                        <span>$${calc.max_loss.toLocaleString()} (${calc.max_risk_pct.toFixed(2)}%)</span>
                    </div>
                    <div class="risk-row">
                        <span>🎯 Ganancia Potencial:</span>
                        <span>$${calc.total_potential_profit.toLocaleString()}</span>
                    </div>
                    <div class="risk-row">
                        <span>⚖️ Ratio R/R:</span>
                        <span>${calc.risk_reward_ratio.toFixed(2)}:1</span>
                    </div>
                </div>
                <div class="risk-recommendation ${calc.recommendation.includes('EXCELENTE') ? 'excellent' : calc.recommendation.includes('RECHAZAR') ? 'reject' : 'moderate'}">
                    ${calc.recommendation}
                </div>
            `;
        } else {
            content += `
                <div class="risk-rejection">
                    <h4>❌ Operación No Recomendada</h4>
                    <p><strong>Razón:</strong> ${calc.reason}</p>
                    <p><strong>Fuerza mínima requerida:</strong> ${calc.min_required_strength}%</p>
                    <div class="philosophy-note">
                        <em>${calc.philosophy}</em>
                    </div>
                </div>
            `;
        }

        content += '</div>';
        modal.querySelector('.modal-content').innerHTML = content;
        this.showModal(modal);
    }

    /**
     * Solicita análisis de todos los símbolos
     */
    analyzeAllSymbols() {
        this.socket.emit('request_all_merino_symbols');
        this.showNotification('Iniciando análisis masivo según Metodología Merino...', 'info');
    }

    /**
     * Solicita la filosofía de Merino
     */
    requestPhilosophy() {
        this.socket.emit('request_merino_philosophy');
    }

    /**
     * Muestra modal con la filosofía de Merino
     */
    showPhilosophyModal(data) {
        const modal = this.createModal('Filosofía de Jaime Merino');
        
        let content = `
            <div class="philosophy-modal">
                <h3>💡 Principios Fundamentales</h3>
                <div class="philosophy-principles">
        `;

        Object.entries(data.philosophy).forEach(([key, value]) => {
            content += `
                <div class="principle-item">
                    <strong>${key.replace('_', ' ').toUpperCase()}:</strong>
                    <em>"${value}"</em>
                </div>
            `;
        });

        content += `
                </div>
                
                <h3>📊 Estados del Mercado</h3>
                <div class="market-states">
        `;

        Object.entries(data.market_states).forEach(([state, description]) => {
            content += `
                <div class="state-item">
                    <span class="state-name">${state}:</span>
                    <span class="state-desc">${description}</span>
                </div>
            `;
        });

        content += `
                </div>
                
                <h3>🎯 Confluencias Técnicas</h3>
                <ul class="confluences-list">
        `;

        data.confluences.forEach(confluence => {
            content += `<li>${confluence}</li>`;
        });

        content += `
                </ul>
            </div>
        `;

        modal.querySelector('.modal-content').innerHTML = content;
        this.showModal(modal);
    }

    /**
     * Configura listeners de eventos
     */
    setupEventListeners() {
        // Botones principales
        const analyzeAllBtn = document.getElementById('analyze-all-btn');
        if (analyzeAllBtn) {
            analyzeAllBtn.addEventListener('click', () => this.analyzeAllSymbols());
        }

        const btcAnalysisBtn = document.getElementById('btc-analysis-btn');
        if (btcAnalysisBtn) {
            btcAnalysisBtn.addEventListener('click', () => this.requestDetailedAnalysis('BTCUSDT'));
        }

        const philosophyBtn = document.getElementById('philosophy-btn');
        if (philosophyBtn) {
            philosophyBtn.addEventListener('click', () => this.requestPhilosophy());
        }

        // Configuraciones
        document.addEventListener('keydown', (e) => {
            // Atajos de teclado
            if (e.ctrlKey) {
                switch(e.key) {
                    case 'r':
                        e.preventDefault();
                        this.analyzeAllSymbols();
                        break;
                    case 'b':
                        e.preventDefault();
                        this.requestDetailedAnalysis('BTCUSDT');
                        break;
                    case 'p':
                        e.preventDefault();
                        this.requestPhilosophy();
                        break;
                }
            }
        });
    }

    /**
     * Inicia tareas periódicas
     */
    startPeriodicTasks() {
        // Actualización automática del estado del servidor
        this.intervalIds.push(setInterval(() => {
            if (this.connected && this.settings.autoRefresh) {
                this.requestServerStatus();
            }
        }, this.settings.refreshInterval));

        // Rotación de filosofía
        this.intervalIds.push(setInterval(() => {
            this.rotatePhilosophy();
        }, 15000));

        // Limpieza de notificaciones antiguas
        this.intervalIds.push(setInterval(() => {
            this.cleanOldNotifications();
        }, 60000));
    }

    /**
     * Utilidades y helpers
     */
    
    getSignalClass(signalType) {
        const classes = {
            'LONG': 'signal-long',
            'SHORT': 'signal-short',
            'WAIT': 'signal-wait',
            'WAIT_SQUEEZE': 'signal-wait-squeeze',
            'NO_SIGNAL': 'signal-none'
        };
        return classes[signalType] || 'signal-none';
    }

    getStrengthColor(strength) {
        if (strength >= 80) return '#27ae60'; // Verde fuerte
        if (strength >= 60) return '#f39c12'; // Naranja
        if (strength >= 40) return '#e67e22'; // Naranja oscuro
        return '#e74c3c'; // Rojo
    }

    formatPrice(price) {
        if (price >= 1000) {
            return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        return price.toFixed(price < 1 ? 6 : 4);
    }

    showNotification(message, type = 'info') {
        // Implementación de notificaciones (ya está en el HTML)
        const event = new CustomEvent('showNotification', {
            detail: { message, type }
        });
        window.dispatchEvent(event);
    }

    playAlertSound() {
        if (this.settings.soundAlerts) {
            // Crear sonido de alerta
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2);
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        }
    }

    // Métodos de utilidades del modal y UI
    createModal(title) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-content"></div>
            </div>
        `;
        
        modal.querySelector('.modal-close').addEventListener('click', () => {
            this.hideModal(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideModal(modal);
            }
        });
        
        return modal;
    }

    showModal(modal) {
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);
    }

    hideModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                document.body.removeChild(modal);
            }
        }, 300);
    }

    // Otros métodos auxiliares
    requestServerStatus() {
        this.socket.emit('get_merino_server_status');
    }

    sendClientPreferences() {
        this.socket.emit('set_client_preferences', {
            preferences: this.settings
        });
    }

    updateConnectionStatus(connected) {
        // Actualizar UI de estado de conexión
        const statusElements = document.querySelectorAll('.connection-status');
        statusElements.forEach(el => {
            el.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            el.textContent = connected ? 'Conectado' : 'Desconectado';
        });
    }

    loadSettings() {
        const saved = localStorage.getItem('merinoTradingSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }

    saveSettings() {
        localStorage.setItem('merinoTradingSettings', JSON.stringify(this.settings));
    }

    showPhilosophyMessage() {
        setTimeout(() => {
            this.showNotification('💡 "El arte de tomar dinero de otros legalmente" - Jaime Merino', 'info');
        }, 2000);
    }
}

// Inicializar cliente cuando el DOM esté listo
let merinoClient;

document.addEventListener('DOMContentLoaded', function() {
    merinoClient = new MerinoTradingClient();
    
    // Hacer disponible globalmente para uso en HTML
    window.merinoClient = merinoClient;
    
    console.log('🎯 Jaime Merino Trading Client inicializado');
});