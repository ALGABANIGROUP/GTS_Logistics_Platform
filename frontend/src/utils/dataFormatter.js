/**
 * Data Formatter Utility - API data processor
 * Converts raw objects and data into safe formats for React rendering
 */

/**
 * Format error message from API
 * Handles different error shapes (objects, strings, arrays)
 */
export const formatErrorMessage = (error) => {
    if (!error) return "An unexpected error occurred";

    // If it is a direct string
    if (typeof error === "string") {
        return error;
    }

    // If it is a Pydantic validation error message
    if (error.type && error.msg) {
        return `${error.type}: ${error.msg}`;
    }

    // If it is an array of errors
    if (Array.isArray(error)) {
        return error
            .map((err) => {
                if (typeof err === "string") return err;
                if (err.msg) return err.msg;
                if (err.message) return err.message;
                return JSON.stringify(err);
            })
            .filter(Boolean)
            .join("; ");
    }

    // If it is an object
    if (typeof error === "object") {
        // Try common properties
        if (error.detail) return error.detail;
        if (error.message) return error.message;
        if (error.msg) return error.msg;
        if (error.error) return error.error;

        // If there are remaining fields
        const keys = Object.keys(error).filter(
            (k) => k !== "type" && k !== "loc" && k !== "input"
        );
        if (keys.length > 0) {
            return `${keys[0]}: ${error[keys[0]]}`;
        }

        // Last attempt: convert to JSON
        try {
            return JSON.stringify(error);
        } catch {
            return "Error processing object";
        }
    }

    return String(error);
};

/**
 * Safe for rendering in React JSX
 * Validates that data is renderable
 */
export const safeRenderData = (data) => {
    if (data === null || data === undefined) {
        return null;
    }

    // String: Completely safe
    if (typeof data === "string" || typeof data === "number") {
        return data;
    }

    // boolean: safe
    if (typeof data === "boolean") {
        return data ? "true" : "false";
    }

    // Array: map items safely
    if (Array.isArray(data)) {
        return data.map((item, idx) => {
            const safe = safeRenderData(item);
            return safe === null ? null : <div key={idx}>{safe}</div>;
        });
    }

    // Object: cannot be rendered directly
    if (typeof data === "object") {
        // Try rendering inner text
        if (data.toString && data.toString() !== "[object Object]") {
            return data.toString();
        }

        // Convert to JSON (development only)
        if (process.env.NODE_ENV === "development") {
            try {
                return <pre>{JSON.stringify(data, null, 2)}</pre>;
            } catch {
                return "[Object cannot be serialized]";
            }
        }

        return "[Object]";
    }

    return String(data);
};

/**
 * API data handler - fully safe
 * Use with Promise.catch() or error handlers
 */
export const createSafeDataHandler = (onSuccess, onError) => {
    return {
        success: (data) => {
            try {
                // Ensure data is string, array, or known object
                if (typeof data === "string" || Array.isArray(data)) {
                    onSuccess?.(data);
                } else if (typeof data === "object" && data !== null) {
                    // Handle object
                    onSuccess?.(data);
                } else {
                    onSuccess?.(data);
                }
            } catch (err) {
                onError?.(err);
            }
        },

        error: (error) => {
            try {
                const formatted = formatErrorMessage(error);
                onError?.(formatted);
            } catch (err) {
                onError?.("Error processing error");
            }
        },
    };
};

/**
 * Axios data handler - converts Axios responses to safe data
 */
export const handleAxiosResponse = (response) => {
    // Extract actual data
    const data = response?.data || {};

    // If it is a direct text message
    if (typeof data === "string") {
        return data;
    }

    // If it is an object with a message
    if (data.message) return data.message;
    if (data.detail) return data.detail;
    if (data.msg) return data.msg;

    // If it is an array
    if (Array.isArray(data)) {
        return data.map((item) => formatErrorMessage(item)).join("; ");
    }

    // Object: collect all messages
    if (typeof data === "object") {
        const messages = [];
        for (const [key, value] of Object.entries(data)) {
            if (typeof value === "string") {
                messages.push(value);
            } else if (typeof value === "object" && value !== null) {
                messages.push(formatErrorMessage(value));
            }
        }
        return messages.filter(Boolean).join("; ") || "Request completed";
    }

    return "Request completed";
};

/**
 * Axios error handler
 */
export const handleAxiosError = (error) => {
    const status = error?.response?.status;
    const data = error?.response?.data;

    // Handle by status
    if (status === 400) {
        // Validation Error (Pydantic)
        if (Array.isArray(data?.detail)) {
            return data.detail
                .map((err) => formatErrorMessage(err))
                .filter(Boolean)
                .join("; ");
        }
        return formatErrorMessage(data?.detail || data || "Bad request");
    }

    if (status === 401) {
        return "Your session has expired. Please log in again.";
    }

    if (status === 403) {
        return "You do not have sufficient permissions to perform this action.";
    }

    if (status === 404) {
        return "The requested resource was not found.";
    }

    if (status === 422) {
        // Unprocessable Entity (Validation)
        if (Array.isArray(data?.detail)) {
            return data.detail
                .map((err) => {
                    const field = err.loc?.join(".");
                    const message = err.msg;
                    return field ? `${field}: ${message}` : message;
                })
                .filter(Boolean)
                .join("; ");
        }
        return formatErrorMessage(data);
    }

    if (status === 500) {
        return "Server error. Please try again later.";
    }

    if (status === 503) {
        return "The server is currently unavailable.";
    }

    // Generic error
    return (
        formatErrorMessage(data) ||
        error?.message ||
        "An unexpected connection error occurred"
    );
};

/**
 * Convert error from any source into safe message
 */
export const normalizeError = (error) => {
    // If it's an Axios error
    if (error?.response) {
        return handleAxiosError(error);
    }

    // If it's a normal error
    if (error instanceof Error) {
        return error.message;
    }

    // Regular object
    if (typeof error === "object") {
        return formatErrorMessage(error);
    }

    // Direct text
    return String(error || "An unexpected error occurred");
};

export default {
    formatErrorMessage,
    safeRenderData,
    createSafeDataHandler,
    handleAxiosResponse,
    handleAxiosError,
    normalizeError,
};
