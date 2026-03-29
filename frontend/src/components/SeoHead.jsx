import { useEffect } from "react";

const upsertMeta = (selector, attributes) => {
    let node = document.head.querySelector(selector);
    if (!node) {
        node = document.createElement("meta");
        document.head.appendChild(node);
    }
    Object.entries(attributes).forEach(([key, value]) => {
        if (value == null || value === "") {
            node.removeAttribute(key);
            return;
        }
        node.setAttribute(key, value);
    });
    return node;
};

const upsertLink = (selector, attributes) => {
    let node = document.head.querySelector(selector);
    if (!node) {
        node = document.createElement("link");
        document.head.appendChild(node);
    }
    Object.entries(attributes).forEach(([key, value]) => {
        if (value == null || value === "") {
            node.removeAttribute(key);
            return;
        }
        node.setAttribute(key, value);
    });
    return node;
};

const upsertJsonLd = (id, schema) => {
    let node = document.head.querySelector(`script[data-seo-schema="${id}"]`);
    if (!node) {
        node = document.createElement("script");
        node.type = "application/ld+json";
        node.dataset.seoSchema = id;
        document.head.appendChild(node);
    }
    node.textContent = JSON.stringify(schema);
    return node;
};

export default function SeoHead({
    title,
    description,
    canonical,
    keywords,
    ogTitle,
    ogDescription,
    ogUrl,
    twitterTitle,
    twitterDescription,
    schema,
}) {
    useEffect(() => {
        if (title) {
            document.title = title;
        }

        upsertMeta('meta[name="description"]', { name: "description", content: description });
        upsertMeta('meta[name="keywords"]', { name: "keywords", content: keywords });
        upsertMeta('meta[name="robots"]', { name: "robots", content: "index,follow" });
        upsertMeta('meta[property="og:title"]', { property: "og:title", content: ogTitle || title });
        upsertMeta('meta[property="og:description"]', { property: "og:description", content: ogDescription || description });
        upsertMeta('meta[property="og:url"]', { property: "og:url", content: ogUrl || canonical });
        upsertMeta('meta[property="og:type"]', { property: "og:type", content: "website" });
        upsertMeta('meta[name="twitter:card"]', { name: "twitter:card", content: "summary_large_image" });
        upsertMeta('meta[name="twitter:title"]', { name: "twitter:title", content: twitterTitle || ogTitle || title });
        upsertMeta('meta[name="twitter:description"]', { name: "twitter:description", content: twitterDescription || ogDescription || description });

        const verification = import.meta.env.VITE_GOOGLE_SITE_VERIFICATION;
        if (verification) {
            upsertMeta('meta[name="google-site-verification"]', {
                name: "google-site-verification",
                content: verification,
            });
        }

        upsertLink('link[rel="canonical"]', { rel: "canonical", href: canonical });

        let schemaNode;
        if (schema) {
            schemaNode = upsertJsonLd("page", schema);
        }

        return () => {
            if (schemaNode) {
                schemaNode.remove();
            }
        };
    }, [
        canonical,
        description,
        keywords,
        ogDescription,
        ogTitle,
        ogUrl,
        schema,
        title,
        twitterDescription,
        twitterTitle,
    ]);

    return null;
}
