import { WS_BASE_URL } from "./env";

export function buildWsUrl(path: string) {
    const cleanBase = String(WS_BASE_URL).replace(/\/+$/, "");
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    return `${cleanBase}${cleanPath}`;
}
