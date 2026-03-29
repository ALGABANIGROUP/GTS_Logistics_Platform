// frontend/src/api/authTest.js
/**
 * Authentication Diagnostic Test
 * Run in browser console to test auth endpoints
 */

import { API_BASE_URL } from "../config/env";

const BASE_URL = String(API_BASE_URL || "").replace(/\/+$/, "");

// Test credentials
const TEST_USER = {
    username: "enjoy983@hotmail.com",
    password: "password123",
};

export const authTests = {

    /**
     * Test 1: Login and get token
     */
    async test1_login() {
        console.log("\n=== TEST 1: Login ===");
        try {
            const data = new URLSearchParams();
            data.append("username", TEST_USER.username);
            data.append("password", TEST_USER.password);

            const res = await fetch(`${BASE_URL}/api/v1/auth/token`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: data,
            });

            const result = await res.json();
            console.log("Status:", res.status);
            console.log("Response:", result);

            if (res.ok && result.access_token) {
                sessionStorage.setItem("test_token", result.access_token);
                console.log("✅ Token saved to sessionStorage");
                return result.access_token;
            } else {
                console.error("❌ Login failed");
                return null;
            }
        } catch (err) {
            console.error("❌ Error:", err.message);
            return null;
        }
    },

    /**
     * Test 2: Get current user with token
     */
    async test2_getCurrentUser() {
        console.log("\n=== TEST 2: Get Current User ===");
        try {
            let token = sessionStorage.getItem("test_token");

            if (!token) {
                console.warn("⚠️  No token found. Run test1_login() first");
                return null;
            }

            console.log("Using token:", token.substring(0, 50) + "...");

            const res = await fetch(`${BASE_URL}/api/v1/auth/me`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json",
                },
            });

            console.log("Status:", res.status);
            const result = await res.json();
            console.log("Response:", result);

            if (res.ok) {
                console.log("✅ Successfully fetched user");
            } else {
                console.error("❌ Failed to fetch user");
            }

            return result;
        } catch (err) {
            console.error("❌ Error:", err.message);
            return null;
        }
    },

    /**
     * Test 3: Get quick user info (no DB query)
     */
    async test3_quickUserInfo() {
        console.log("\n=== TEST 3: Quick User Info ===");
        try {
            let token = sessionStorage.getItem("test_token");

            if (!token) {
                console.warn("⚠️  No token found. Run test1_login() first");
                return null;
            }

            const res = await fetch(`${BASE_URL}/api/v1/auth/me/quick`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json",
                },
            });

            console.log("Status:", res.status);
            const result = await res.json();
            console.log("Response:", result);

            if (res.ok) {
                console.log("✅ Quick auth check successful");
            } else {
                console.error("❌ Quick auth check failed");
            }

            return result;
        } catch (err) {
            console.error("❌ Error:", err.message);
            return null;
        }
    },

    /**
     * Test 4: Check token validity
     */
    async test4_tokenValidity() {
        console.log("\n=== TEST 4: Token Validity ===");
        try {
            let token = sessionStorage.getItem("test_token");

            if (!token) {
                console.warn("⚠️  No token found. Run test1_login() first");
                return null;
            }

            // Decode JWT (without verification)
            const parts = token.split(".");
            if (parts.length !== 3) {
                console.error("❌ Invalid token format");
                return null;
            }

            const payload = JSON.parse(atob(parts[1]));
            console.log("Token Payload:", payload);

            // Check expiration
            const now = Math.floor(Date.now() / 1000);
            const exp = payload.exp;
            const remaining = exp - now;

            console.log(`Token expires in: ${remaining} seconds (${(remaining / 60).toFixed(1)} minutes)`);

            if (remaining > 0) {
                console.log("✅ Token is still valid");
            } else {
                console.error("❌ Token has expired");
            }

            return payload;
        } catch (err) {
            console.error("❌ Error:", err.message);
            return null;
        }
    },

    /**
     * Run all tests
     */
    async runAll() {
        console.log("🧪 Starting Auth Diagnostic Tests");
        console.log("=".repeat(50));

        const token = await this.test1_login();
        if (token) {
            await this.test2_getCurrentUser();
            await this.test3_quickUserInfo();
            await this.test4_tokenValidity();
        }

        console.log("=".repeat(50));
        console.log("✅ Tests complete");
    },
};

// Make available in console
if (typeof window !== "undefined") {
    window.authTests = authTests;
    console.log("🧪 Auth tests available as: window.authTests");
    console.log("Run: authTests.runAll() to test all endpoints");
}

export default authTests;
