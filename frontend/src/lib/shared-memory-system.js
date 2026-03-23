// frontend/src/lib/shared-memory-system.js
class SharedMemorySystem {
    constructor() {
        this.memory = new Map();
        this.history = new Map();
        this.subscribers = new Map();
    }

    // Store shared data
    set(key, value, metadata = {}) {
        const memoryItem = {
            value,
            metadata: {
                source: metadata.source || 'unknown',
                timestamp: new Date(),
                version: this.getNextVersion(key),
                ...metadata
            }
        };

        // Save history
        if (!this.history.has(key)) {
            this.history.set(key, []);
        }
        this.history.get(key).push(memoryItem);

        // Update current memory
        this.memory.set(key, memoryItem);

        // Notify subscribers
        this.notifySubscribers(key, memoryItem);
    }

    // Retrieve data
    get(key, version = 'latest') {
        if (version === 'latest') {
            return this.memory.get(key);
        } else {
            const history = this.history.get(key);
            return history?.find(item => item.metadata.version === version);
        }
    }

    // Subscribe to updates
    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, new Set());
        }
        this.subscribers.get(key).add(callback);

        // Return unsubscribe function
        return () => {
            this.subscribers.get(key)?.delete(callback);
        };
    }

    // Smart search through memory
    smartSearch(query, filters = {}) {
        const results = [];

        this.memory.forEach((item, key) => {
            const score = this.calculateRelevanceScore(key, item, query, filters);
            if (score > 0) {
                results.push({
                    key,
                    item,
                    relevance: score
                });
            }
        });

        return results.sort((a, b) => b.relevance - a.relevance);
    }

    // Automatic memory cleanup
    startAutoCleanup() {
        setInterval(() => {
            this.cleanupOldData();
        }, 24 * 60 * 60 * 1000); // Daily
    }
}
