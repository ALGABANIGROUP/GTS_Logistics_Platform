// File: frontend/src/pages/Account.jsx
import React, { useMemo, useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext.jsx";
import axiosClient from "../api/axiosClient";
import { toast } from "react-toastify";
import { getUserRole } from "../utils/userRole";

const Account = () => {
    const auth = useAuth ? useAuth() : null;
    const user = auth?.user || null;

    const roleValue = useMemo(() => getUserRole(user), [user]);
    const roleLabel = roleValue
        ? roleValue.replaceAll("_", " ").toUpperCase()
        : "USER";
    const isAdmin = useMemo(() => {
        return roleValue.includes("admin") || roleValue.includes("super");
    }, [roleValue]);

    const [isEditing, setIsEditing] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [serverMessage, setServerMessage] = useState(null);
    const [errorMessage, setErrorMessage] = useState(null);

    const [formData, setFormData] = useState({
        full_name: user?.full_name || user?.name || "",
        company: user?.company || "",
        country: user?.country || "",
        user_type: user?.user_type || "",
        phone_number: user?.phone_number || user?.phone || "",
    });

    const [changeReason, setChangeReason] = useState("");

    // Keep form data in sync with the latest user object
    useEffect(() => {
        setFormData({
            full_name: user?.full_name || user?.name || "",
            company: user?.company || "",
            country: user?.country || "",
            user_type: user?.user_type || "",
            phone_number: user?.phone_number || user?.phone || "",
        });
    }, [user]);

    if (!user) {
        return (
            <div className="glass-page min-h-[60vh] flex items-center justify-center">
                <div className="glass-panel rounded-xl px-6 py-4">
                    <p className="text-sm">
                        No user session found. Please log in again.
                    </p>
                </div>
            </div>
        );
    }

    const initials = (user.full_name || user.name || user.email || "?")
        .split(" ")
        .map((p) => p[0]?.toUpperCase())
        .slice(0, 2)
        .join("");

    const handleEditToggle = () => {
        setIsEditing((prev) => !prev);
        setServerMessage(null);
        setErrorMessage(null);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setServerMessage(null);
        setErrorMessage(null);

        try {
            if (isAdmin) {
                // Admin: direct profile update against /users/me
                const payload = {
                    email: user.email,
                    full_name: formData.full_name || "",
                    company: formData.company || "",
                    country: formData.country || "",
                    user_type: formData.user_type || "",
                    phone_number: formData.phone_number || "",
                };

                const response = await axiosClient.put("/users/me", payload);
                const updatedUser = response?.data || null;

                if (updatedUser && auth?.setUser) {
                    // Merge backend profile fields into the auth user object
                    auth.setUser((prev) => ({
                        ...(prev || {}),
                        ...updatedUser,
                    }));
                }

                // Keep the local form state aligned with the backend response
                if (updatedUser) {
                    setFormData({
                        full_name: updatedUser.full_name || "",
                        company: updatedUser.company || "",
                        country: updatedUser.country || "",
                        user_type: updatedUser.user_type || "",
                        phone_number: updatedUser.phone_number || "",
                    });
                }

                toast.success("Profile updated successfully");
                setServerMessage("Profile updated successfully.");
                setIsEditing(false);
            } else {
                // Non-admin: send change request for admin approval
                if (!changeReason.trim()) {
                    setErrorMessage("Please provide a reason for the requested changes.");
                    setSubmitting(false);
                    return;
                }

                const payload = {
                    requested_changes: {
                        full_name: formData.full_name,
                        company: formData.company,
                        country: formData.country,
                        user_type: formData.user_type,
                        phone_number: formData.phone_number,
                    },
                    reason: changeReason.trim(),
                };

                await axiosClient.post("/account/change-request", payload);

                toast.info("Change request submitted for admin approval");
                setServerMessage(
                    "Your change request has been submitted and is pending admin approval."
                );
                setIsEditing(false);
            }
        } catch (err) {
            console.error("[Account] submit error:", err);
            const detail =
                err?.response?.data?.detail ||
                err?.response?.data?.message ||
                "Failed to process request";
            setErrorMessage(detail);
            toast.error(detail);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="glass-page space-y-6 p-4 md:p-6">
            <div className="flex items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Account & Profile</h1>
                    <p className="text-gray-600 text-sm mt-1">
                        View your profile information and manage change requests.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                        Role: {roleLabel}
                    </span>
                    <button
                        type="button"
                        onClick={handleEditToggle}
                        className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium border border-blue-600 text-blue-600 hover:bg-blue-50 transition-colors"
                    >
                        {isEditing
                            ? "Cancel"
                            : isAdmin
                                ? "Edit Profile"
                                : "Request Profile Change"}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: main profile card */}
                <div className="lg:col-span-2 glass-card rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="h-14 w-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-xl font-semibold">
                            {initials}
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-gray-900">
                                {user.full_name || user.name || "User"}
                            </h2>
                            <p className="text-sm text-gray-600">
                                {user.user_type || "Account"}{" "}
                                {user.country ? `• ${user.country}` : null}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                                Role: {roleLabel}
                            </p>
                        </div>
                    </div>

                    {!isEditing && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <p className="text-xs uppercase text-gray-500">Email</p>
                                <p className="text-sm font-medium text-gray-900">{user.email}</p>
                            </div>

                            <div className="space-y-1">
                                <p className="text-xs uppercase text-gray-500">Company</p>
                                <p className="text-sm font-medium text-gray-900">
                                    {user.company || "—"}
                                </p>
                            </div>

                            <div className="space-y-1">
                                <p className="text-xs uppercase text-gray-500">Country</p>
                                <p className="text-sm font-medium text-gray-900">
                                    {user.country || "—"}
                                </p>
                            </div>

                            <div className="space-y-1">
                                <p className="text-xs uppercase text-gray-500">User Type</p>
                                <p className="text-sm font-medium text-gray-900">
                                    {user.user_type || "—"}
                                </p>
                            </div>

                            <div className="space-y-1">
                                <p className="text-xs uppercase text-gray-500">Phone</p>
                                <p className="text-sm font-medium text-gray-900">
                                    {user.phone_number || user.phone || "—"}
                                </p>
                            </div>

                            <div className="space-y-1">
                                <p className="text-xs uppercase text-gray-500">Login Source</p>
                                <p className="text-sm font-medium text-gray-900">
                                    {user.source || "Web-UI"}
                                </p>
                            </div>
                        </div>
                    )}

                    {isEditing && (
                        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                        Full Name
                                    </label>
                                    <input
                                        type="text"
                                        name="full_name"
                                        value={formData.full_name}
                                        onChange={handleInputChange}
                                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                        Company
                                    </label>
                                    <input
                                        type="text"
                                        name="company"
                                        value={formData.company}
                                        onChange={handleInputChange}
                                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                        Country
                                    </label>
                                    <input
                                        type="text"
                                        name="country"
                                        value={formData.country}
                                        onChange={handleInputChange}
                                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                        User Type
                                    </label>
                                    <input
                                        type="text"
                                        name="user_type"
                                        value={formData.user_type}
                                        onChange={handleInputChange}
                                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                        Phone
                                    </label>
                                    <input
                                        type="text"
                                        name="phone_number"
                                        value={formData.phone_number}
                                        onChange={handleInputChange}
                                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                            </div>

                            {!isAdmin && (
                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">
                                        Reason for change (required)
                                    </label>
                                    <textarea
                                        value={changeReason}
                                        onChange={(e) => setChangeReason(e.target.value)}
                                        rows={3}
                                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Explain why you need these changes. This will be sent to an admin for approval."
                                    />
                                </div>
                            )}

                            {errorMessage && (
                                <p className="text-xs text-red-600">{errorMessage}</p>
                            )}
                            {serverMessage && (
                                <p className="text-xs text-green-600">{serverMessage}</p>
                            )}

                            <div className="flex items-center justify-end gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={handleEditToggle}
                                    disabled={submitting}
                                    className="px-4 py-2 rounded-lg text-sm border border-gray-300 text-gray-700 hover:bg-gray-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="px-4 py-2 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
                                >
                                    {submitting
                                        ? isAdmin
                                            ? "Saving..."
                                            : "Sending request..."
                                        : isAdmin
                                            ? "Save changes"
                                            : "Submit change request"}
                                </button>
                            </div>
                        </form>
                    )}
                </div>

                {/* Right: session meta */}
                <div className="glass-card rounded-xl p-6 space-y-4">
                    <h3 className="text-sm font-semibold text-gray-900">Session Overview</h3>
                    <div className="space-y-3 text-sm">
                        <div className="flex items-center justify-between">
                            <span className="text-gray-600">Status</span>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                Active
                            </span>
                        </div>
                        {user.loginAt && (
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Last Login</span>
                                <span className="text-gray-900 text-xs">
                                    {new Date(user.loginAt).toLocaleString()}
                                </span>
                            </div>
                        )}
                        {roleValue && (
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Role</span>
                                <span className="text-gray-900 text-xs">{roleLabel}</span>
                            </div>
                        )}
                    </div>
                    <p className="text-xs text-gray-400 mt-4">
                        Admin users can update profile data directly. Non-admin users submit
                        a change request that must be approved by an administrator.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Account;
