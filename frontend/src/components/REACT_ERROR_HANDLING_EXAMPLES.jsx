/**
 * Example of correct error handling usage in React
 * Example Usage: React Error Handling
 */

import React, { useState } from "react";
import axiosClient from "../api/axiosClient";
import {
    SafeErrorDisplay,
    SafeSuccessDisplay,
    SafeDataDisplay,
} from "../components/SafeDisplay";
import { normalizeError } from "../utils/dataFormatter";

/**
 * Example 1: Using SafeErrorDisplay in a component
 */
export const LoginFormExample = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        try {
            const response = await axiosClient.post("/api/v1/auth/token", {
                email,
                password,
            });

            // Data is now safe
            const token = response.data?.access_token;
            setSuccess("Login successful!");
            localStorage.setItem("access_token", token);
        } catch (err) {
            // Handle error safely
            const normalizedMessage = normalizeError(err);
            setError(normalizedMessage);

            // Don't try to display err.response.data directly!
            // Use normalizeError() instead
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-md mx-auto p-6 space-y-4">
            <h1>Login</h1>

            {/* ✅ Display error safely */}
            {error && (
                <SafeErrorDisplay
                    error={error}
                    onDismiss={() => setError(null)}
                />
            )}

            {/* ✅ Display success message safely */}
            {success && (
                <SafeSuccessDisplay
                    message={success}
                    onDismiss={() => setSuccess(null)}
                />
            )}

            <form onSubmit={handleLogin} className="space-y-4">
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    className="w-full px-4 py-2 border rounded"
                    disabled={loading}
                />

                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    className="w-full px-4 py-2 border rounded"
                    disabled={loading}
                />

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-500 text-white py-2 rounded disabled:opacity-50"
                >
                    {loading ? "Loading..." : "Sign in"}
                </button>
            </form>
        </div>
    );
};

/**
 * Example 2: Using Promise.catch with normalizeError
 */
export const UserProfileExample = () => {
    const [user, setUser] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    React.useEffect(() => {
        loadUser();
    }, []);

    const loadUser = () => {
        setLoading(true);
        setError(null);

        axiosClient
            .get("/api/v1/users/me")
            .then((response) => {
                // Data is safe
                setUser(response.data);
            })
            .catch((err) => {
                // Handle error safely
                const message = normalizeError(err);
                setError(message);

                // Don't do this:
                // setError(err.response.data); // ❌ May be an object!

                // Do this instead:
                // setError(normalizeError(err)); // ✅ Always text
            })
            .finally(() => {
                setLoading(false);
            });
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="p-6 space-y-4">
            {/* ✅ Display error safely */}
            {error && (
                <SafeErrorDisplay
                    error={error}
                    onDismiss={() => setError(null)}
                />
            )}

            {/* ✅ Display data safely */}
            {user && (
                <div>
                    <h2>User Profile</h2>
                    <SafeDataDisplay data={user} />
                </div>
            )}

            <button
                onClick={loadUser}
                className="px-4 py-2 bg-blue-500 text-white rounded"
            >
                Reload
            </button>
        </div>
    );
};

/**
 * Example 3: Error handling in async/await
 */
export const DataFetchExample = async () => {
    try {
        const response = await axiosClient.get("/api/v1/data");

        // Data is now safe
        console.log("Data:", response.data);
        return response.data;
    } catch (error) {
        // Convert error to safe text message
        const message = normalizeError(error);
        console.error("Error:", message); // Always text
        throw new Error(message); // Throw safe error
    }
};

/**
 * Example 4: Handling Validation errors (422)
 */
export const ValidationErrorExample = () => {
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const submitForm = async (formData) => {
        setLoading(true);
        setErrors({});

        try {
            await axiosClient.post("/api/v1/users", formData);
            // Success
        } catch (error) {
            if (error.response?.status === 422) {
                // Validation error from Pydantic
                const details = error.response.data?.detail;

                if (Array.isArray(details)) {
                    // Handle error array
                    const fieldErrors = {};
                    details.forEach((err) => {
                        const field = err.loc?.[1] || "general";
                        const message = err.msg || "Error";
                        fieldErrors[field] = message;
                    });
                    setErrors(fieldErrors);
                } else {
                    // Generic error
                    const message = normalizeError(error);
                    setErrors({ general: message });
                }
            } else {
                // Another error
                const message = normalizeError(error);
                setErrors({ general: message });
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <form>
            {/* Display errors safely */}
            {errors.general && (
                <SafeErrorDisplay error={errors.general} />
            )}

            {/* Display field errors */}
            {Object.entries(errors).map(([field, error]) => (
                field !== "general" && (
                    <div key={field}>
                        <SafeErrorDisplay error={error} />
                    </div>
                )
            ))}

            <button
                onClick={(e) => {
                    e.preventDefault();
                    submitForm({ /* form data */ });
                }}
                disabled={loading}
            >
                Submit
            </button>
        </form>
    );
};

/**
 * Best practices:
 *
 * ✅ DO:
 * - Use normalizeError() for any server error
 * - Use SafeErrorDisplay to display errors
 * - Validate data types before rendering
 * - Only use error.response.data after safe handling
 *
 * ❌ DON'T:
 * - Render error.response.data directly in JSX
 * - Assume data is always text
 * - Render a raw object in React (causes error)
 * - Forget to handle API errors
 *
 * 🔐 Security:
 * - All errors are converted to safe text
 * - No raw objects in JSX
 * - Comprehensive handling of Pydantic validation errors
 * - Multi-language error support
 */

export default {
    LoginFormExample,
    UserProfileExample,
    DataFetchExample,
    ValidationErrorExample,
};
