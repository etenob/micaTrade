// *** MERINO_DASHBOARD.JS - VERSIÓN CORREGIDA ***
// ================================================

// Variables globales
let socket;
let analysisData = {};
let lastPrices = {};
const philosophyQuotes = [
    "El arte de tomar dinero de otros legalmente",
    "Disciplina vence a emociones en el trading",
    "Preserve capital, gestione riesgo, genere ganancias", 
    "Solo opere con alta probabilidad de éxito",
    "El mercado siempre tiene la razón",
    "Paciencia es la virtud del trader exitoso"
];

// *** FUNCIÓN AGREGADA: Forzar actualización de todas las secciones de futuros ***
function forceUpdateAllFutures() {
    console.log("🔄 Forzando actualización de todas las secciones de futuros...");
    
    if (typeof analysisData !== 'undefined' && typeof updateFuturesSection === 'function') {
        Object.keys(analysisData).forEach(symbol => {
            try {
                updateFuturesSection(symbol, analysisData[symbol]);
                console.log(`✅ ${symbol} actualizado`);
            } catch (error) {
                console.error(`❌ Error actualizando ${symbol}:`, error);
            }
        });
    } else {
        console.log("❌ No se puede forzar actualización - datos no disponibles");
    }
}

// *** INICIALIZACIÓN MEJORADA ***
document.addEventListener('DOMContentLoaded', function() {
    console.log("📄 Página cargada - inicializando dashboard...");
    
    initializeSocket();
    updateServerTime();
    rotatePhilosophy();
    setInterval(updateServerTime, 1000);
    setInterval(rotatePhilosophy, 10000);
    
    // Event listeners para botones
    setupEventListeners();
    
    // Log inicial
    addLogEntry('SISTEMA', 'Dashboard cargado correctamente', 'success');
    
    // *** FIX PRINCIPAL: Auto-actualización al cargar la página ***
    setTimeout(() => {
        console.log("🔄 Ejecutando actualización inicial de futuros...");
        forceUpdateAllFutures();
    }, 3000);
    
    // *** AUTO-ACTUALIZACIÓN CADA 30 SEGUNDOS COMO BACKUP ***
    setInterval(() => {
        if (typeof analysisData !== 'undefined' && Object.keys(analysisData).length > 0) {
            console.log("🔄 Auto-actualización periódica de futuros...");
            forceUpdateAllFutures();
        }
    }, 30000);
});

// Configuración de WebSocket
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        updateConnectionStatus(true);
        addLogEntry('WEBSOCKET', 'Conectado al servidor', 'success');
        
        // Solicitar análisis inicial
        socket.emit('request_all_symbols');
    });

    socket.on('disconnect', function() {
        updateConnectionStatus(false);
        addLogEntry('WEBSOCKET', 'Conexión perdida', 'error');
    });

    // *** WEBSOCKET HANDLER MEJORADO ***
    socket.on('analysis_update', function(data) {
        console.log('📡 Datos recibidos via WebSocket:', data);
        
        if (data.data) {
            // Actualizar datos globales
            analysisData = data.data;
            
            // *** FIX PRINCIPAL: Actualizar cada tarjeta individualmente ***
            Object.keys(data.data).forEach(symbol => {
                try {
                    const symbolData = data.data[symbol];
                    
                    // Actualizar la tarjeta principal
                    updateTradingCard(symbol, symbolData);
                    
                    // *** FORZAR ACTUALIZACIÓN DE LA SECCIÓN DE FUTUROS ***
                    updateFuturesSection(symbol, symbolData);
                    
                    console.log(`🎯 ${symbol} completamente actualizado`);
                    
                } catch (error) {
                    console.error(`❌ Error actualizando ${symbol}:`, error);
                }
            });
            
            // Actualizar estadísticas globales
            updateGlobalStats();
            
            // Mostrar notificación
            showNotification('Análisis actualizado', 'success');
        }
    });

    socket.on('merino_analysis_update', function(data) {
        updateTradingCard(data.symbol, data.data);
        // *** FORZAR ACTUALIZACIÓN DE FUTUROS TAMBIÉN AQUÍ ***
        updateFuturesSection(data.symbol, data.data);
        addLogEntry('ANÁLISIS', `${data.symbol}: ${data.data.signal?.signal || 'UNKNOWN'}`, 'info');
    });

    socket.on('analysis_error', function(data) {
        addLogEntry('ERROR', `Error en análisis: ${data.error}`, 'error');
    });

    socket.on('server_status', function(data) {
        updateServerStats(data);
    });
}

// Configurar event listeners
function setupEventListeners() {
    document.getElementById('analyze-all-btn').addEventListener('click', function() {
        socket.emit('request_all_symbols');
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando...';
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-chart-bar"></i> Analizar Todos';
        }, 3000);
        addLogEntry('USUARIO', 'Solicitud de análisis completo', 'info');
    });

    document.getElementById('btc-analysis-btn').addEventListener('click', function() {
        socket.emit('request_analysis', {symbol: 'BTCUSDT'});
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando BTC...';
        setTimeout(() => {
            this.innerHTML = '<i class="fab fa-bitcoin"></i> Análisis BTC';
        }, 2000);
        addLogEntry('USUARIO', 'Análisis específico de BTCUSDT solicitado', 'info');
    });

    document.getElementById('philosophy-btn').addEventListener('click', function() {
        rotatePhilosophy();
        addLogEntry('FILOSOFÍA', 'Recordatorio de metodología Merino', 'warning');
    });

    document.getElementById('refresh-btn').addEventListener('click', function() {
        location.reload();
    });

    document.getElementById('clear-log-btn').addEventListener('click', function() {
        document.getElementById('console-log').innerHTML = '';
        addLogEntry('SISTEMA', 'Log limpiado', 'info');
    });
}

// *** ACTUALIZAR TARJETA DE TRADING MEJORADA ***
function updateTradingCard(symbol, data) {
    const card = document.getElementById(`card-${symbol}`);
    if (!card) return;

    // Actualizar datos básicos
    const signal = data.signal || {};
    const currentPrice = data.current_price || 0;
    
    // Actualizar precio con animación si cambió
    const priceElement = card.querySelector('.symbol-price');
    if (priceElement) {
        const newPrice = currentPrice.toFixed(2);
        const oldPrice = lastPrices[symbol] || 0;
        
        priceElement.textContent = `${newPrice}`;
        
        if (oldPrice && oldPrice !== currentPrice) {
            if (currentPrice > oldPrice) {
                priceElement.style.color = 'var(--success)';
            } else {
                priceElement.style.color = 'var(--danger)';
            }
            
            setTimeout(() => {
                priceElement.style.color = 'var(--accent-gold)';
            }, 2000);
        }
        
        lastPrices[symbol] = currentPrice;
    }

    // Actualizar signal badge
    const signalBadge = card.querySelector('.signal-badge');
    if (signalBadge) {
        const signalType = signal.signal || 'LOADING';
        signalBadge.textContent = signalType;
        signalBadge.className = `signal-badge signal-${signalType.toLowerCase()}`;
    }

    // Actualizar strength badge
    const strengthBadge = card.querySelector('.strength-badge');
    if (strengthBadge) {
        const strength = signal.signal_strength || 0;
        strengthBadge.textContent = `${strength}%`;
        
        // Cambiar color según fuerza
        if (strength >= 80) {
            strengthBadge.style.borderColor = 'var(--success)';
            strengthBadge.style.color = 'var(--success)';
        } else if (strength >= 60) {
            strengthBadge.style.borderColor = 'var(--warning)';
            strengthBadge.style.color = 'var(--warning)';
        } else {
            strengthBadge.style.borderColor = 'var(--accent-gold)';
            strengthBadge.style.color = 'var(--accent-gold)';
        }
    }

    // *** FORZAR ACTUALIZACIÓN DE FUTUROS SIEMPRE ***
    updateFuturesSection(symbol, data);
    
    // Resaltar tarjeta si es señal de alta probabilidad
    if (signal.signal_strength >= 70) {
        card.classList.add('highlight');
        setTimeout(() => card.classList.remove('highlight'), 2000);
    }
    
    // Guardar datos para estadísticas
    analysisData[symbol] = data;
    updateGlobalStats();
}

// Actualizar sección de futuros (versión mejorada con más debugging)
function updateFuturesSection(symbol, data) {
    console.log(`🔍 Actualizando futuros para ${symbol}:`, data);
    
    const futuresSection = document.getElementById(`futures-${symbol}`);
    const tradingLevels = data.trading_levels;
    const signal = data.signal || {};

    // Debug: Verificar estructura de datos
    console.log(`📊 Trading levels para ${symbol}:`, tradingLevels);
    console.log(`🎯 Signal para ${symbol}:`, signal);

    if (!futuresSection) {
        console.warn(`❌ No se encontró futures-${symbol}`);
        return;
    }

    if (!tradingLevels) {
        console.warn(`❌ No hay trading_levels para ${symbol}`);
        return;
    }

    if (signal.signal === 'NO_SIGNAL' || signal.signal === 'LOADING') {
        console.log(`⏳ Señal no válida para ${symbol}: ${signal.signal}`);
        futuresSection.style.display = 'none';
        return;
    }

    // *** MOSTRAR SECCIÓN DE FUTUROS SIEMPRE ***
    futuresSection.style.display = 'block';
    console.log(`👁️ Sección ${symbol} ahora visible`);

    // ✅ ACTUALIZAR ENTRADA - Versión corregida con fallbacks
    const entryOptimal = document.getElementById(`entry-optimal-${symbol}`);
    const entryRange = document.getElementById(`entry-range-${symbol}`);

    if (entryOptimal) {
        const optimalValue = tradingLevels.entry_optimal;
        if (optimalValue !== undefined && optimalValue !== null) {
            entryOptimal.textContent = `$${optimalValue.toFixed(2)}`;
            console.log(`✅ Entrada optimal ${symbol}: $${optimalValue.toFixed(2)}`);
        } else {
            entryOptimal.textContent = '$0.00';
            console.warn(`⚠️ entry_optimal indefinido para ${symbol}`);
        }
    } else {
        console.warn(`❌ Elemento entry-optimal-${symbol} no encontrado`);
    }

    if (entryRange && tradingLevels.entry_range) {
        const rangeLow = tradingLevels.entry_range.low;
        const rangeHigh = tradingLevels.entry_range.high;
        
        if (rangeLow !== undefined && rangeHigh !== undefined) {
            entryRange.textContent = `$${rangeLow.toFixed(2)} - $${rangeHigh.toFixed(2)}`;
            console.log(`✅ Rango entrada ${symbol}: $${rangeLow.toFixed(2)} - $${rangeHigh.toFixed(2)}`);
        } else {
            entryRange.textContent = '$0.00 - $0.00';
            console.warn(`⚠️ entry_range indefinido para ${symbol}`);
        }
    } else {
        console.warn(`❌ Elemento entry-range-${symbol} no encontrado o sin entry_range`);
    }

    // ✅ ACTUALIZAR TARGETS - Versión mejorada
    const targetsContainer = document.getElementById(`targets-${symbol}`);
    if (targetsContainer && tradingLevels.targets && Array.isArray(tradingLevels.targets)) {
        targetsContainer.innerHTML = '';
        
        tradingLevels.targets.forEach((target, index) => {
            if (target !== undefined && target !== null) {
                const targetDiv = document.createElement('div');
                targetDiv.className = 'level-item';
                targetDiv.innerHTML = `
                    <span class="level-label">Target ${index + 1}:</span>
                    <span class="level-value price-target">$${target.toFixed(2)}</span>
                `;
                targetsContainer.appendChild(targetDiv);
                console.log(`✅ Target ${index + 1} ${symbol}: $${target.toFixed(2)}`);
            }
        });
    } else {
        console.warn(`❌ Elemento targets-${symbol} no encontrado o targets inválidos`);
    }

    // ✅ ACTUALIZAR STOP LOSS
    const stopPrice = document.getElementById(`stop-price-${symbol}`);
    if (stopPrice && tradingLevels.stop_loss !== undefined) {
        stopPrice.textContent = `$${tradingLevels.stop_loss.toFixed(2)}`;
        console.log(`✅ Stop loss ${symbol}: $${tradingLevels.stop_loss.toFixed(2)}`);
    } else {
        console.warn(`❌ Elemento stop-price-${symbol} no encontrado o stop_loss indefinido`);
    }

    // ✅ ACTUALIZAR INFORMACIÓN ADICIONAL
    const positionSize = document.getElementById(`position-size-${symbol}`);
    if (positionSize && tradingLevels.position_size_pct !== undefined) {
        positionSize.textContent = `${tradingLevels.position_size_pct.toFixed(1)}%`;
    }

    const leverage = document.getElementById(`leverage-${symbol}`);
    if (leverage && tradingLevels.leverage && tradingLevels.leverage.recommended !== undefined) {
        leverage.textContent = `${tradingLevels.leverage.recommended.toFixed(1)}x`;
    }

    const riskReward = document.getElementById(`risk-reward-${symbol}`);
    if (riskReward && tradingLevels.risk_reward !== undefined) {
        riskReward.textContent = `1:${tradingLevels.risk_reward.toFixed(1)}`;
    }

    console.log(`✅ Sección de futuros actualizada para ${symbol}`);
}

function debugTradingData(symbol) {
    console.log("=== DEBUG TRADING DATA ===");
    console.log(`Símbolo: ${symbol}`);
    
    const data = analysisData[symbol];
    if (!data) {
        console.error(`❌ No hay datos para ${symbol}`);
        return;
    }

    console.log("Estructura completa:", data);
    console.log("Trading levels:", data.trading_levels);
    console.log("Signal:", data.signal);
    
    // Verificar elementos DOM
    const elements = [
        `entry-optimal-${symbol}`,
        `entry-range-${symbol}`,
        `targets-${symbol}`,
        `stop-price-${symbol}`,
        `futures-${symbol}`
    ];

    elements.forEach(elementId => {
        const element = document.getElementById(elementId);
        console.log(`Elemento ${elementId}:`, element ? "✅ Existe" : "❌ No existe");
    });
}

// Actualizar estadísticas globales
function updateGlobalStats() {
    const symbols = Object.keys(analysisData);
    const analyzed = symbols.filter(s => analysisData[s].signal?.signal !== 'LOADING').length;
    const highProb = symbols.filter(s => (analysisData[s].signal?.signal_strength || 0) >= 70).length;
    const activeSignals = symbols.filter(s => ['LONG', 'SHORT'].includes(analysisData[s].signal?.signal)).length;

    document.getElementById('symbols-analyzed').textContent = `${analyzed}/${symbols.length}`;
    document.getElementById('active-signals').textContent = activeSignals;
    document.getElementById('high-prob-signals').textContent = highProb;

    // Actualizar precio de BTC si está disponible
    if (analysisData.BTCUSDT && analysisData.BTCUSDT.current_price) {
        document.getElementById('btc-price').textContent = `$${analysisData.BTCUSDT.current_price.toLocaleString()}`;
        
        // Simular cambio porcentual (en producción, calcular real)
        const change = (Math.random() - 0.5) * 10; // Simulado
        const changeElement = document.getElementById('btc-change');
        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
        changeElement.className = `btc-change ${change >= 0 ? 'positive' : 'negative'}`;
    }
}

// Actualizar estado de conexión
function updateConnectionStatus(connected) {
    const statusElements = document.querySelectorAll('#connection-status');
    statusElements.forEach(element => {
        const dot = element.querySelector('.status-dot');
        const text = element.querySelector('span:last-child');
        
        if (connected) {
            dot.style.background = 'var(--success)';
            text.textContent = 'Conectado';
            element.style.background = 'rgba(16, 185, 129, 0.1)';
            element.style.borderColor = 'var(--success)';
        } else {
            dot.style.background = 'var(--danger)';
            text.textContent = 'Desconectado';
            element.style.background = 'rgba(239, 68, 68, 0.1)';
            element.style.borderColor = 'var(--danger)';
        }
    });
}

// Actualizar hora del servidor
function updateServerTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('es-ES', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const serverTimeElement = document.getElementById('server-time');
    if (serverTimeElement) {
        serverTimeElement.textContent = timeString;
    }
    
    const lastUpdateElement = document.getElementById('last-update');
    if (lastUpdateElement) {
        lastUpdateElement.textContent = timeString;
    }
}

// Rotar frases de filosofía
function rotatePhilosophy() {
    const philosophyElement = document.getElementById('philosophy-text');
    if (philosophyElement) {
        const randomQuote = philosophyQuotes[Math.floor(Math.random() * philosophyQuotes.length)];
        philosophyElement.style.opacity = '0';
        
        setTimeout(() => {
            philosophyElement.textContent = `"${randomQuote}"`;
            philosophyElement.style.opacity = '1';
        }, 300);
    }
}

// Agregar entrada al log
function addLogEntry(level, message, type = 'info') {
    const console = document.getElementById('console-log');
    const timestamp = new Date().toLocaleTimeString('es-ES', { hour12: false });
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        <span class="log-level-${type}">${level}</span>
        <span>${message}</span>
    `;
    
    console.appendChild(entry);
    console.scrollTop = console.scrollHeight;
    
    // Limitar a 50 entradas
    while (console.children.length > 50) {
        console.removeChild(console.firstChild);
    }
}

// Actualizar estadísticas del servidor
function updateServerStats(data) {
    // Implementar cuando se reciban estadísticas del servidor
    console.log('Server stats:', data);
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        max-width: 300px;
        z-index: 1000;
        box-shadow: var(--shadow);
        animation: slideIn 0.3s ease;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}" 
               style="color: var(--${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'accent-blue'});"></i>
            <span style="color: var(--text-primary); font-size: 0.9rem;">${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function toggleFutures(symbol) {
    const futuresSection = document.getElementById(`futures-${symbol}`);
    if (futuresSection) {
        if (futuresSection.style.display === 'none') {
            futuresSection.style.display = 'block';
            // *** FORZAR ACTUALIZACIÓN AL MOSTRAR ***
            if (analysisData[symbol]) {
                updateFuturesSection(symbol, analysisData[symbol]);
            }
        } else {
            futuresSection.style.display = 'none';
        }
    }
}

// *** BOTÓN DE REFRESH MANUAL AGREGADO ***
function addManualRefreshButton() {
    // Verificar si ya existe
    if (document.getElementById('manual-refresh-futures-btn')) return;
    
    const refreshBtn = document.createElement('button');
    refreshBtn.id = 'manual-refresh-futures-btn';
    refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Actualizar Entradas';
    refreshBtn.className = 'control-btn btn-warning';
    refreshBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background: linear-gradient(135deg, var(--warning), #D97706);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    `;
    
    refreshBtn.onclick = function() {
        console.log("🔧 Refresh manual solicitado");
        forceUpdateAllFutures();
        showNotification('Entradas actualizadas manualmente', 'success');
    };
    
    document.body.appendChild(refreshBtn);
    console.log("🔧 Botón de refresh manual agregado");
}

// Ejecutar después de que la página cargue
setTimeout(() => {
    addManualRefreshButton();
}, 4000);

// Estilos para animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .trading-card {
        transition: all 0.3s ease;
    }
    
    .philosophy-quote {
        transition: opacity 0.3s ease;
    }
    
    .price-entry {
        font-weight: 700;
        color: var(--accent-gold) !important;
    }
    
    .price-target {
        color: var(--success) !important;
    }
`;
document.head.appendChild(style);