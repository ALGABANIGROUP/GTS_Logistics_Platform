export function buildWsUrl(path: string) {
  const base =
    import.meta.env.VITE_WS_BASE_URL ||
    `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/api/v1/ws`;

  const cleanBase = base.replace(/\/+$/, "");
  const cleanPath = path.startsWith("/") ? path : `/${path}`;

  return `${cleanBase}${cleanPath}`;
}
