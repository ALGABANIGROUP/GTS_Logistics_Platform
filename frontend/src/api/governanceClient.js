import axiosClient from "./axiosClient";

const base = "/api/v1/governance";

export const governanceClient = {
    async listBots() {
        const res = await axiosClient.get(`${base}/bots`);
        return res.data;
    },
    async getBot(botId) {
        const res = await axiosClient.get(`${base}/bots/${encodeURIComponent(botId)}`);
        return res.data;
    },
    async registerBot(manifest) {
        const res = await axiosClient.post(`${base}/bots/register`, manifest);
        return res.data;
    },
    async approveBot(botId, { approver, comments } = {}) {
        const res = await axiosClient.post(`${base}/bots/${encodeURIComponent(botId)}/approve`, {
            approver,
            comments,
        });
        return res.data;
    },
    async activateBot(botId, environment) {
        const res = await axiosClient.post(`${base}/bots/${encodeURIComponent(botId)}/activate`, {
            environment,
        });
        return res.data;
    },
};

export default governanceClient;
