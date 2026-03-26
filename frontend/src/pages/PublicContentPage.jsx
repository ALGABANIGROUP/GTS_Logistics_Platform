import { Link, useLocation, useParams } from "react-router-dom";

const PAGE_COPY = {
  "/blog": {
    title: "Logistics Blog",
    description: "Articles, lane intelligence, and operational updates are being prepared for publication.",
  },
  "/podcasts": {
    title: "Podcasts",
    description: "Audio episodes and interviews will be published here.",
  },
  "/community": {
    title: "Community",
    description: "The public community hub is being assembled with discussions, events, and operator resources.",
  },
  "/stories": {
    title: "Customer Stories",
    description: "Case studies and field stories will be published here.",
  },
  "/press": {
    title: "Press",
    description: "Press releases and media updates will be listed here.",
  },
  "/alerts": {
    title: "Alerts",
    description: "Public security and freight alerts will appear here.",
  },
  "/emergency": {
    title: "Emergency Freight",
    description: "Emergency freight guidance and response resources will be published here.",
  },
  "/partners": {
    title: "Partners",
    description: "Public partner program details and onboarding material will be available here.",
  },
  "/fraud-prevention": {
    title: "Fraud Prevention",
    description: "Fraud prevention checklists and educational content will be published here.",
  },
  "/find-loads": {
    title: "Find Loads",
    description: "The public load discovery experience is not available on this route yet.",
  },
};

function toTitleFromSlug(slug = "") {
  return String(slug)
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function PublicContentPage() {
  const location = useLocation();
  const params = useParams();
  const slug = params.slug || params.toolSlug || "";
  const pathname = location.pathname;
  const exact = PAGE_COPY[pathname];

  const title =
    exact?.title ||
    (pathname.startsWith("/resources/")
      ? toTitleFromSlug(slug || pathname.split("/").pop())
      : pathname.startsWith("/tools/")
        ? `${toTitleFromSlug(slug)} Tool`
        : toTitleFromSlug(slug || pathname.split("/").filter(Boolean).pop()));

  const description =
    exact?.description ||
    `This public page exists now so the route no longer breaks, but the final content for "${title}" has not been published yet.`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="mx-auto max-w-4xl px-6 py-20">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/40 backdrop-blur-xl">
          <div className="text-xs uppercase tracking-[0.3em] text-red-300">GTS Public Content</div>
          <h1 className="mt-4 text-4xl font-bold">{title || "Public Content"}</h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">{description}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/resources"
              className="rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-500"
            >
              Back to Resources
            </Link>
            <Link
              to="/contact"
              className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
            >
              Contact GTS
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
