// Live data fallback helpers. Any usage should be replaced with backend calls.
export const liveDataApi = {
    getGeneralAnalysis: async () => {
        throw new Error('Fallback API disabled: use live backend data only.');
    },
    getWeeklyReports: async () => {
        throw new Error('Fallback API disabled: use live backend data only.');
    }
};
