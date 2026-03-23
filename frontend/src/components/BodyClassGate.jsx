import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const NO_BG_PATHS = new Set([
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/request-received",
  "/verify-email",
  "/account-inactive",
  "/portal",
  "/portal/landing",
  "/portal/select",
]);

const isNoBgPath = (pathname) => {
  if (NO_BG_PATHS.has(pathname)) return true;
  if (pathname.startsWith("/activate/")) return true;
  if (pathname.startsWith("/logout")) return true;
  return false;
};

export default function BodyClassGate() {
  const location = useLocation();

  useEffect(() => {
    if (typeof document === "undefined") return;
    const body = document.body;
    if (!body) return;

    const shouldDisable = isNoBgPath(location.pathname);
    body.classList.toggle("gts-no-bg", shouldDisable);
  }, [location.pathname]);

  return null;
}
