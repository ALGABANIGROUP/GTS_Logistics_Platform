import documentLogoSrc from "../assets/gts_logo.png";

let cachedDocumentLogoDataUrl = null;

export const DOCUMENT_LOGO_SRC = documentLogoSrc;

export const getDocumentLogoDataUrl = async () => {
    if (cachedDocumentLogoDataUrl) {
        return cachedDocumentLogoDataUrl;
    }

    try {
        const response = await fetch(documentLogoSrc);
        const blob = await response.blob();
        cachedDocumentLogoDataUrl = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
        return cachedDocumentLogoDataUrl;
    } catch {
        return null;
    }
};
