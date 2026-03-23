import React, {
    useEffect,
    useState,
    ChangeEvent,
    FormEvent,
    FC,
} from "react";
import { Link } from "react-router-dom";
import { Settings } from "lucide-react";
import {
    fetchUserProfile,
    updateUserProfile,
    UserProfile,
    UserProfileUpdate,
} from "../services/userApi";

const ProfilePage: FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [form, setForm] = useState<UserProfileUpdate>({
        full_name: "",
        company: "",
        country: "",
        user_type: "",
        phone_number: "",
    });
    const [loading, setLoading] = useState<boolean>(true);
    const [saving, setSaving] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await fetchUserProfile();
                setProfile(data);

                setForm({
                    full_name: data.full_name ?? "",
                    company: data.company ?? "",
                    country: data.country ?? "",
                    user_type: data.user_type ?? "",
                    phone_number: data.phone_number ?? "",
                });
            } catch (e: unknown) {
                const err = e as Error;
                setError(err.message || "Failed to load profile");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setSaving(true);
        setError(null);
        setSuccess(null);

        try {
            const updated = await updateUserProfile(form);
            setProfile(updated);
            setSuccess("Profile updated successfully.");
        } catch (e: unknown) {
            const err = e as Error;
            setError(err.message || "Failed to update profile");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <div className="p-4">Loading profile...</div>;
    }

    if (error && !profile) {
        return <div className="p-4 text-red-600">Error: {error}</div>;
    }

    return (
        <div className="max-w-2xl mx-auto p-4 space-y-4">
            <div className="flex items-center justify-between gap-3">
                <h1 className="text-2xl font-semibold">My Profile</h1>
                <Link
                    to="/settings"
                    className="inline-flex items-center gap-2 rounded border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-800 shadow-sm hover:bg-slate-50"
                >
                    <Settings className="h-4 w-4" aria-hidden="true" />
                    Settings
                </Link>
            </div>

            {error && <div className="text-red-600 text-sm">{error}</div>}
            {success && (
                <div className="text-green-600 text-sm">{success}</div>
            )}

            <form
                onSubmit={handleSubmit}
                className="space-y-4 border rounded-lg p-4 bg-white/70 backdrop-blur"
            >
                {/* Email (read-only) */}
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="profile-email">
                        Email
                    </label>
                    <input
                        id="profile-email"
                        type="text"
                        value={profile?.email ?? ""}
                        disabled
                        className="w-full border rounded px-3 py-2 bg-gray-100 cursor-not-allowed text-gray-700"
                    />
                </div>

                {/* Full name */}
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="profile-full-name">
                        Full name
                    </label>
                    <input
                        id="profile-full-name"
                        type="text"
                        name="full_name"
                        value={form.full_name ?? ""}
                        onChange={handleChange}
                        className="w-full border rounded px-3 py-2"
                    />
                </div>

                {/* Company */}
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="profile-company">
                        Company
                    </label>
                    <input
                        id="profile-company"
                        type="text"
                        name="company"
                        value={form.company ?? ""}
                        onChange={handleChange}
                        className="w-full border rounded px-3 py-2"
                    />
                </div>

                {/* Country */}
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="profile-country">
                        Country
                    </label>
                    <input
                        id="profile-country"
                        type="text"
                        name="country"
                        value={form.country ?? ""}
                        onChange={handleChange}
                        className="w-full border rounded px-3 py-2"
                    />
                </div>

                {/* User type */}
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="profile-user-type">
                        User type
                    </label>
                    <input
                        id="profile-user-type"
                        type="text"
                        name="user_type"
                        value={form.user_type ?? ""}
                        onChange={handleChange}
                        className="w-full border rounded px-3 py-2"
                    />
                </div>

                {/* Phone number */}
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="profile-phone-number">
                        Phone number
                    </label>
                    <input
                        id="profile-phone-number"
                        type="text"
                        name="phone_number"
                        value={form.phone_number ?? ""}
                        onChange={handleChange}
                        className="w-full border rounded px-3 py-2"
                    />
                </div>

                <div className="flex items-center gap-3">
                    <button
                        type="submit"
                        disabled={saving}
                        className="px-4 py-2 rounded bg-blue-600 text-white text-sm font-medium disabled:opacity-60"
                    >
                        {saving ? "Saving..." : "Save changes"}
                    </button>

                    {profile?.role && (
                        <span className="text-xs text-gray-600">
                            Role: {profile.role}
                        </span>
                    )}
                </div>
            </form>
        </div>
    );
};

export default ProfilePage;
