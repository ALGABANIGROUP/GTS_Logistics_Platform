// frontend/src/pages/partner/PartnerSettingsPage.jsx

import React, { useEffect, useState } from "react";
import { getPartnerProfile } from "../../services/partnerApi";

const PartnerSettingsPage = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // for now, read-only (view profile)
    useEffect(() => {
        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                const res = await getPartnerProfile();
                setProfile(res);
            } catch (err) {
                const msg =
                    err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to load partner profile.";
                setError(msg);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    return (
        <div className="space-y-4">
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">
                    Settings
                </h1>
                <p className="text-sm text-gray-500">
                    Partner profile and bank information (read-only for now).
                </p>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-100 rounded-md px-3 py-2 text-sm text-red-700">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="text-sm text-gray-600">
                    Loading partner profile...
                </div>
            ) : !profile ? (
                <div className="text-sm text-gray-600">
                    Partner profile not available.
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                        <h2 className="font-semibold text-gray-900 mb-2">
                            Profile
                        </h2>
                        <p className="text-gray-700">{profile.name}</p>
                        <p className="text-gray-700 text-xs mt-1">
                            Code: {profile.code}
                        </p>
                        <p className="text-gray-700 text-xs mt-1">
                            Type: {profile.partnerType}
                        </p>
                        <p className="text-gray-700 text-xs mt-1">
                            Email: {profile.email}
                        </p>
                        {profile.phone && (
                            <p className="text-gray-700 text-xs mt-1">
                                Phone: {profile.phone}
                            </p>
                        )}
                        {profile.addressText && (
                            <p className="text-gray-500 text-xs mt-2 whitespace-pre-line">
                                {profile.addressText}
                            </p>
                        )}
                    </div>

                    <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                        <h2 className="font-semibold text-gray-900 mb-2">
                            Bank & commission
                        </h2>
                        <p className="text-gray-700 text-xs">
                            Default B2B share: {profile.defaultB2BShare}%
                        </p>
                        <p className="text-gray-700 text-xs">
                            Default B2C share: {profile.defaultB2CShare}%
                        </p>
                        <p className="text-gray-700 text-xs">
                            Default marketplace share: {profile.defaultMarketplaceShare}%
                        </p>

                        {profile.bankAccountName && (
                            <p className="text-gray-700 text-xs mt-2">
                                Account name: {profile.bankAccountName}
                            </p>
                        )}
                        {profile.bankAccountIban && (
                            <p className="text-gray-700 text-xs">
                                IBAN: {profile.bankAccountIban}
                            </p>
                        )}
                        {profile.bankAccountSwift && (
                            <p className="text-gray-700 text-xs">
                                SWIFT: {profile.bankAccountSwift}
                            </p>
                        )}

                        <p className="text-[11px] text-gray-400 mt-3">
                            For security reasons, profile and bank details may only be
                            updated by the GTS admin team.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PartnerSettingsPage;
