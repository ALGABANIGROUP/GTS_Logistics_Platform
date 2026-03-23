// frontend/src/lib/ai-bot-communication.js
class AIBotOrchestrator {
    constructor() {
        this.bots = new Map();
        this.sharedMemory = new SharedMemorySystem();
        this.eventBus = new BotEventBus();
    }

    // Register bots in the system
    registerBot(botName, botInstance) {
        this.bots.set(botName, {
            instance: botInstance,
            capabilities: botInstance.getCapabilities(),
            status: 'active'
        });
    }

    // Request collaboration between bots
    async requestCollaboration(requesterBot, targetBots, action, data) {
        const results = [];

        for (const botName of targetBots) {
            const bot = this.bots.get(botName);
            if (bot && bot.capabilities.includes(action)) {
                const result = await bot.instance.executeAction(action, data);
                results.push({ bot: botName, result });
            }
        }

        return results;
    }

    // Automatic capabilities discovery
    discoverCapabilities() {
        const capabilitiesMap = {};
        this.bots.forEach((bot, name) => {
            capabilitiesMap[name] = bot.capabilities;
        });
        return capabilitiesMap;
    }
}
