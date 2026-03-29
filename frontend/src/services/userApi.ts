// src/services/userApi.ts

import { API_BASE_URL } from "../config/env";

function getAuthToken(): string | null {
    return localStorage.getItem("access_token");
}

function getAuthHeaders() {
    const token = getAuthToken();
    const headers: Record<string, string> = {
        "Accept": "application/json",
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
}

export interface UserProfile {
    id: number;
    email: string;
    full_name?: string | null;
    username?: string | null;
    company?: string | null;
    country?: string | null;
    user_type?: string | null;
    phone_number?: string | null;
    role?: string | null;
    is_active?: boolean | null;
    created_at?: string | null;
    updated_at?: string | null;
}

export interface UserProfileUpdate {
    full_name?: string;
    company?: string;
    country?: string;
    user_type?: string;
    phone_number?: string;
}

export async function fetchAuthMe() {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        method: "GET",
        headers: getAuthHeaders(),
    });

    if (!res.ok) {
        throw new Error(`auth/me failed: ${res.status}`);
    }

    return res.json() as Promise<{
        id: number;
        email: string;
        role: string;
        is_active: boolean;
    }>;
}

export async function fetchUserProfile(): Promise<UserProfile> {
    const res = await fetch(`${API_BASE_URL}/users/me`, {
        method: "GET",
        headers: getAuthHeaders(),
    });

    if (!res.ok) {
        throw new Error(`users/me failed: ${res.status}`);
    }

    return res.json() as Promise<UserProfile>;
}

export async function updateUserProfile(payload: UserProfileUpdate): Promise<UserProfile> {
    const res = await fetch(`${API_BASE_URL}/users/me`, {
        method: "PUT",
        headers: {
            ...getAuthHeaders(),
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        throw new Error(`update users/me failed: ${res.status}`);
    }

    return res.json() as Promise<UserProfile>;
}
