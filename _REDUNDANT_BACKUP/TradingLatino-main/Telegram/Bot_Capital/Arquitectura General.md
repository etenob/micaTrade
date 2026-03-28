🖼️ Arquitectura General
flowchart TD
    subgraph Bots de Trading
        A[Bot_Scalping] --> B[Bot_Capital]
        C[Bot_Intradía] --> B
        D[Bot_Swing] --> B
    end

    subgraph Núcleo de Gestión
        B --> E[AlertManager\n(Filtra duplicados y cooldown)]
        E --> F[telegram_helper.py\n(Envía mensaje)]
    end

    subgraph Interfaz Usuario
        F --> G[Usuario recibe notificación en Telegram]
        H[Usuario escribe comando] --> I[poll_bot.py]
        I --> J{Comando}
        J -- /start --> K[Bienvenida]
        J -- /status --> L[Últimas señales / balance\n(vía Bot_Capital)]
        J -- /help --> M[Lista de comandos]
        J -- otros --> N[Eco / Respuesta genérica]
    end

🔑 Puntos Clave del Diseño

Un solo canal de salida: todos los bots envían sus señales hacia Bot_Capital.

AlertManager: evita duplicados, controla el intervalo de reenvío.

telegram_helper.py: único encargado de enviar mensajes al API de Telegram.

poll_bot.py: agrega bidireccionalidad → el usuario puede consultar el estado o pedir señales.

Extensible: se puede sumar Freqtrade para ejecución automática sin romper la arquitectura.
