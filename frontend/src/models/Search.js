const DEFAULT_STOP_WORDS = {
    ar: [
        "the",
        "a",
        "an",
        "and",
        "or",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "am",
        "are",
        "was",
        "were",
        "from",
    ],
    en: [
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "am",
        "are",
        "was",
        "were",
    ],
};

export class SearchIndex {
    constructor(name, options = {}) {
        this.name = name;
        this.documents = [];
        this.index = {};
        this.lastUpdated = null;
        this.options = {
            fields: options.fields || [],
            weights: options.weights || {},
            language: options.language || "ar",
            ...options,
        };
    }

    update(documents = []) {
        this.documents = Array.isArray(documents) ? documents : [];
        this.buildIndex();
        this.lastUpdated = new Date().toISOString();
    }

    buildIndex() {
        this.index = {};

        this.documents.forEach((doc, docIndex) => {
            Object.keys(doc || {}).forEach((field) => {
                if (!this.shouldIndexField(field)) return;
                const value = doc[field];
                if (value == null) return;
                const textValue = Array.isArray(value) ? value.join(" ") : String(value);
                if (textValue.trim().length === 0) return;
                this.indexText(field, textValue, docIndex);
            });
        });
    }

    indexText(field, text, docIndex) {
        const tokens = this.tokenize(text);
        tokens.forEach((token) => {
            if (!this.index[token]) this.index[token] = {};
            if (!this.index[token][field]) this.index[token][field] = new Set();
            this.index[token][field].add(docIndex);
        });
    }

    tokenize(text) {
        const cleanText = String(text)
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^\w\u0600-\u06FF\s]/g, " ");

        const tokens = cleanText.split(/\s+/).filter((token) => token.length > 2);
        return tokens.filter((token) => !this.isStopWord(token));
    }

    search(query, options = {}) {
        const tokens = this.tokenize(query);
        const results = new Map();

        tokens.forEach((token) => {
            const tokenResults = this.searchToken(token, options);
            tokenResults.forEach((score, docIndex) => {
                const current = results.get(docIndex) || 0;
                results.set(docIndex, current + score);
            });
        });

        const maxResults = options.maxResults || 50;
        const highlight = options.highlightMatches !== false;

        const sortedResults = Array.from(results.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, maxResults)
            .map(([docIndex, score]) => ({
                document: this.documents[docIndex],
                score,
                highlights: highlight ? this.generateHighlights(this.documents[docIndex], tokens) : {},
                source: this.name,
            }));

        return {
            query,
            total: sortedResults.length,
            results: sortedResults,
            time: Date.now(),
            index: this.name,
        };
    }

    searchToken(token, options = {}) {
        const results = new Map();

        if (this.index[token]) {
            Object.entries(this.index[token]).forEach(([field, docIndices]) => {
                const weight = this.getFieldWeight(field);
                docIndices.forEach((docIndex) => {
                    const current = results.get(docIndex) || 0;
                    results.set(docIndex, current + weight);
                });
            });
        }

        if (options.enableFuzzySearch) {
            const similarTokens = this.findSimilarTokens(token);
            similarTokens.forEach((similarToken) => {
                if (!this.index[similarToken]) return;
                Object.entries(this.index[similarToken]).forEach(([field, docIndices]) => {
                    const weight = this.getFieldWeight(field) * 0.7;
                    docIndices.forEach((docIndex) => {
                        const current = results.get(docIndex) || 0;
                        results.set(docIndex, current + weight);
                    });
                });
            });
        }

        return results;
    }

    findSimilarTokens(token) {
        const similar = [];
        const maxDistance = 2;

        Object.keys(this.index).forEach((indexToken) => {
            if (this.levenshteinDistance(token, indexToken) <= maxDistance) {
                similar.push(indexToken);
            }
        });

        return similar;
    }

    levenshteinDistance(a, b) {
        if (a.length === 0) return b.length;
        if (b.length === 0) return a.length;

        const matrix = Array.from({ length: b.length + 1 }, () => []);

        for (let i = 0; i <= b.length; i += 1) {
            matrix[i][0] = i;
        }

        for (let j = 0; j <= a.length; j += 1) {
            matrix[0][j] = j;
        }

        for (let i = 1; i <= b.length; i += 1) {
            for (let j = 1; j <= a.length; j += 1) {
                if (b.charAt(i - 1) === a.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }

        return matrix[b.length][a.length];
    }

    generateHighlights(document, tokens) {
        const highlights = {};
        if (!document) return highlights;

        Object.keys(document).forEach((field) => {
            if (!this.shouldIndexField(field)) return;
            const value = document[field];
            if (value == null) return;
            const textValue = Array.isArray(value) ? value.join(" ") : String(value);
            if (!textValue) return;
            const fieldHighlights = this.highlightText(textValue, tokens);
            if (fieldHighlights.length > 0) {
                highlights[field] = fieldHighlights;
            }
        });

        return highlights;
    }

    highlightText(text, tokens) {
        const highlights = [];
        const lowerText = text.toLowerCase();

        tokens.forEach((token) => {
            const regex = new RegExp(`(${this.escapeRegex(token)})`, "gi");
            let match;
            while ((match = regex.exec(lowerText)) !== null) {
                highlights.push({
                    token: match[1],
                    start: match.index,
                    end: match.index + match[1].length,
                    context: this.getContext(text, match.index, 40),
                });
            }
        });

        return highlights;
    }

    getContext(text, position, contextLength) {
        const start = Math.max(0, position - contextLength);
        const end = Math.min(text.length, position + contextLength);
        let context = text.substring(start, end);
        if (start > 0) context = `...${context}`;
        if (end < text.length) context = `${context}...`;
        return context;
    }

    escapeRegex(value) {
        return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    getFieldWeight(field) {
        return this.options.weights[field] || 1.0;
    }

    shouldIndexField(field) {
        return this.options.fields.length === 0 || this.options.fields.includes(field);
    }

    isStopWord(word) {
        const lang = this.options.language || "ar";
        return (
            DEFAULT_STOP_WORDS[lang]?.includes(word.toLowerCase()) ||
            DEFAULT_STOP_WORDS.en.includes(word.toLowerCase())
        );
    }

    getStats() {
        return {
            name: this.name,
            documentCount: this.documents.length,
            tokenCount: Object.keys(this.index).length,
            lastUpdated: this.lastUpdated,
            fields: this.options.fields,
        };
    }
}

export class SearchEngine {
    constructor(indices, options = {}) {
        this.indices = indices;
        this.options = {
            enableFuzzySearch: true,
            enableSynonyms: true,
            enableAutocomplete: true,
            searchDepth: "deep",
            maxResults: 50,
            highlightMatches: true,
            language: "ar",
            ...options,
        };
    }

    async search(query, searchOptions = {}) {
        const options = { ...this.options, ...searchOptions };
        const startTime = Date.now();
        const indicesToSearch = this.getIndicesToSearch(options);

        const results = await Promise.all(
            indicesToSearch.map((indexName) => {
                const index = this.indices[indexName];
                if (!index) return { results: [], total: 0, index: indexName };
                return index.search(query, options);
            })
        );

        const mergedResults = this.mergeResults(results);
        const filteredResults = this.applyFilters(mergedResults, options.filters);
        const sortedResults = this.sortResults(filteredResults, options.sortBy);
        const finalResults = sortedResults.slice(0, options.maxResults || 50);

        return {
            query,
            total: finalResults.length,
            results: finalResults,
            time: Date.now() - startTime,
            indices: indicesToSearch,
            meta: {
                searchDepth: options.searchDepth,
                fuzzySearch: options.enableFuzzySearch,
                synonyms: options.enableSynonyms,
            },
        };
    }

    getIndicesToSearch(options) {
        if (options.indices && options.indices.length > 0) {
            return options.indices.filter((indexName) => this.indices[indexName]);
        }

        switch (options.searchDepth) {
            case "quick":
                return ["users", "roles"];
            case "deep":
            case "exhaustive":
            default:
                return Object.keys(this.indices);
        }
    }

    mergeResults(allResults) {
        const mergedMap = new Map();

        allResults.forEach((indexResults) => {
            const indexName = indexResults.index || "unknown";

            indexResults.results.forEach((result) => {
                const docId = result.document?.id || JSON.stringify(result.document);
                if (!mergedMap.has(docId)) {
                    mergedMap.set(docId, {
                        document: result.document,
                        totalScore: result.score,
                        sources: [indexName],
                        scores: { [indexName]: result.score },
                        highlights: result.highlights || {},
                    });
                } else {
                    const existing = mergedMap.get(docId);
                    existing.totalScore += result.score;
                    existing.sources.push(indexName);
                    existing.scores[indexName] = result.score;
                    if (result.highlights) {
                        existing.highlights = { ...existing.highlights, ...result.highlights };
                    }
                }
            });
        });

        return Array.from(mergedMap.values());
    }

    applyFilters(results, filters = {}) {
        if (!filters || Object.keys(filters).length === 0) return results;

        return results.filter((result) => {
            const document = result.document || {};
            return Object.entries(filters).every(([key, value]) =>
                this.matchesFilter(document, key, value)
            );
        });
    }

    matchesFilter(document, key, value) {
        const docValue = document[key];
        if (docValue == null) return false;

        if (key === "dateRange" && value?.start) {
            const docDate = new Date(document.createdAt || document.updatedAt || 0).getTime();
            const startDate = new Date(value.start).getTime();
            const endDate = new Date(value.end || value.start).getTime();
            return docDate >= startDate && docDate <= endDate;
        }

        if (Array.isArray(value)) {
            return value.includes(docValue);
        }

        if (typeof docValue === "string" && typeof value === "string") {
            return docValue.toLowerCase().includes(value.toLowerCase());
        }

        return docValue === value;
    }

    sortResults(results, sortBy = "relevance") {
        return results.sort((a, b) => {
            switch (sortBy) {
                case "date":
                    return new Date(b.document?.createdAt || 0) - new Date(a.document?.createdAt || 0);
                case "name":
                    return String(a.document?.name || a.document?.title || "").localeCompare(
                        String(b.document?.name || b.document?.title || ""),
                        "ar"
                    );
                case "category":
                    return String(a.document?.category || "").localeCompare(String(b.document?.category || ""), "ar");
                case "relevance":
                default:
                    return b.totalScore - a.totalScore;
            }
        });
    }
}
