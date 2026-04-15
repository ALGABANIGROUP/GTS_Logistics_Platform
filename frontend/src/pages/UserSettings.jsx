import React, { useState, useEffect } from 'react';
import { User, Lock, Bell, Globe, Moon, LogOut, Mail, Phone, MapPin, Calendar, Crown, Shield, Star, Edit3, Check, X, RefreshCw } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext.jsx';
import axiosClient from '../api/axiosClient';
import PreferencesPanel from '../components/PreferencesPanel.jsx';
import SessionsPanel from '../components/SessionsPanel.jsx';
import TruckOrbitSpinner from '../components/loaders/TruckOrbitSpinner.jsx';

const UserSettings = () => {
    const [activeTab, setActiveTab] = useState('profile');
    const { user, changePassword } = useAuth();
    const [userDetails, setUserDetails] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [location, setLocation] = useState(null);
    const [locationLoading, setLocationLoading] = useState(false);
    const [editingLocation, setEditingLocation] = useState(false);
    const [newLocation, setNewLocation] = useState('');
    const [editingProfile, setEditingProfile] = useState(false);
    const [profileForm, setProfileForm] = useState({
        name: '',
        company: '',
        country: '',
        phone_number: ''
    });
    const [savingProfile, setSavingProfile] = useState(false);

    // Password change state
    const [changingPassword, setChangingPassword] = useState(false);
    const [passwordForm, setPasswordForm] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [passwordError, setPasswordError] = useState('');
    const [passwordSuccess, setPasswordSuccess] = useState('');
    const [twoFactorLoading, setTwoFactorLoading] = useState(false);
    const [twoFactorSetup, setTwoFactorSetup] = useState(null);
    const [twoFactorCode, setTwoFactorCode] = useState('');
    const [twoFactorMessage, setTwoFactorMessage] = useState('');
    const [twoFactorError, setTwoFactorError] = useState('');

    useEffect(() => {
        fetchUserDetails();
        getCurrentLocation();
    }, []);

    useEffect(() => {
        if (userDetails?.user) {
            const userData = userDetails.user;
            setProfileForm({
                name: userData.name || '',
                company: userData.company || '',
                country: userData.country || '',
                phone_number: userData.phone_number || ''
            });
        }
    }, [userDetails]);

    const fetchUserDetails = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await axiosClient.get('/api/v1/auth/me');
            if (response.data.ok) {
                setUserDetails(response.data);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (err) {
            console.error('Failed to fetch user details:', err);
            setError(`Failed to load user information: ${err.response?.data?.detail || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const getCurrentLocation = () => {
        if (navigator.geolocation) {
            setLocationLoading(true);
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const { latitude, longitude } = position.coords;
                    try {
                        // Use reverse geocoding to get the place name
                        const response = await fetch(
                            `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
                        );
                        const data = await response.json();
                        const locationName = `${data.city || 'Unknown City'}, ${data.countryName || 'Unknown Country'}`;
                        setLocation({
                            name: locationName,
                            coords: { latitude, longitude }
                        });
                    } catch (error) {
                        console.error('Failed to get location name:', error);
                        setLocation({
                            name: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
                            coords: { latitude, longitude }
                        });
                    }
                    setLocationLoading(false);
                },
                (error) => {
                    console.error('Geolocation error:', error);
                    setLocation({ name: 'Location access denied', coords: null });
                    setLocationLoading(false);
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        } else {
            setLocation({ name: 'Geolocation not supported', coords: null });
        }
    };

    const cancelLocationEdit = () => {
        setEditingLocation(false);
        setNewLocation('');
    };

    const updateLocation = async () => {
        if (!newLocation.trim()) return;

        try {
            // An API call could be added here to update location in the database
            // For now, save to localStorage as an example
            localStorage.setItem('user_custom_location', newLocation);
            setLocation({ name: newLocation, coords: null });
            setEditingLocation(false);
            setNewLocation('');
        } catch (error) {
            console.error('Failed to update location:', error);
        }
    };

    const handleProfileChange = (field, value) => {
        setProfileForm(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const saveProfileChanges = async () => {
        try {
            setSavingProfile(true);
            const response = await axiosClient.put('/api/v1/users/me', profileForm);
            if (response.data.ok) {
                // Update the userDetails with new data
                setUserDetails(prev => ({
                    ...prev,
                    user: {
                        ...prev.user,
                        ...profileForm
                    }
                }));
                setEditingProfile(false);
            }
        } catch (error) {
            console.error('Failed to save profile:', error);
            setError('Failed to save profile changes');
        } finally {
            setSavingProfile(false);
        }
    };

    const cancelProfileEdit = () => {
        // Reset form to current values
        const userData = userDetails?.user || {};
        setProfileForm({
            name: userData.name || '',
            company: userData.company || '',
            country: userData.country || '',
            phone_number: userData.phone_number || ''
        });
        setEditingProfile(false);
    };

    const handlePasswordChange = (field, value) => {
        setPasswordForm(prev => ({
            ...prev,
            [field]: value
        }));
        // Clear errors when user starts typing
        if (passwordError) setPasswordError('');
        if (passwordSuccess) setPasswordSuccess('');
    };

    const validatePasswordForm = () => {
        if (!passwordForm.currentPassword.trim()) {
            setPasswordError('Current password is required');
            return false;
        }
        if (!passwordForm.newPassword.trim()) {
            setPasswordError('New password is required');
            return false;
        }
        if (passwordForm.newPassword.length < 8) {
            setPasswordError('New password must be at least 8 characters long');
            return false;
        }
        if (passwordForm.newPassword !== passwordForm.confirmPassword) {
            setPasswordError('New passwords do not match');
            return false;
        }
        if (passwordForm.currentPassword === passwordForm.newPassword) {
            setPasswordError('New password must be different from current password');
            return false;
        }
        return true;
    };

    const handleChangePassword = async () => {
        if (!validatePasswordForm()) return;

        setChangingPassword(true);
        setPasswordError('');
        setPasswordSuccess('');

        try {
            await changePassword(passwordForm.currentPassword, passwordForm.newPassword);
            setPasswordSuccess('Password changed successfully!');
            setPasswordForm({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            });
        } catch (error) {
            setPasswordError(error?.response?.data?.detail || 'Failed to change password');
        } finally {
            setChangingPassword(false);
        }
    };

    const startTwoFactorSetup = async () => {
        try {
            setTwoFactorLoading(true);
            setTwoFactorError('');
            setTwoFactorMessage('');
            const response = await axiosClient.post('/api/v1/auth/2fa/setup');
            setTwoFactorSetup(response.data || null);
            setTwoFactorMessage('2FA setup created. Scan the QR code or use the manual key, then verify.');
        } catch (err) {
            console.error('Failed to start 2FA setup:', err);
            setTwoFactorError(err?.response?.data?.detail || 'Unable to start 2FA setup.');
        } finally {
            setTwoFactorLoading(false);
        }
    };

    const verifyTwoFactorSetup = async () => {
        if (!twoFactorCode.trim()) {
            setTwoFactorError('Enter the verification code from your authenticator app.');
            return;
        }

        try {
            setTwoFactorLoading(true);
            setTwoFactorError('');
            setTwoFactorMessage('');
            await axiosClient.post('/api/v1/auth/2fa/verify', { token: twoFactorCode.trim() });
            setTwoFactorMessage('Two-factor authentication has been verified successfully.');
            setTwoFactorCode('');
            fetchUserDetails();
        } catch (err) {
            console.error('Failed to verify 2FA:', err);
            setTwoFactorError(err?.response?.data?.detail || 'Invalid 2FA code. Please try again.');
        } finally {
            setTwoFactorLoading(false);
        }
    };

    const getRoleDisplayName = (role) => {
        // Match backend/security/rbac.py INTERNAL_ROLE_ORDER + PARTNER_ROLE
        const roleNames = {
            'super_admin': 'Super Admin',
            'admin': 'Administrator',
            'manager': 'Manager',
            'user': 'User',
            'partner': 'Partner'
        };
        return roleNames[role] || role;
    };

    const getRoleIcon = (role) => {
        switch (role) {
            case 'super_admin':
                return <Crown className="w-5 h-5 text-red-400" />;
            case 'admin':
                return <Shield className="w-5 h-5 text-blue-400" />;
            case 'manager':
                return <Star className="w-5 h-5 text-amber-400" />;
            case 'partner':
                return <User className="w-5 h-5 text-purple-400" />;
            default:
                return <User className="w-5 h-5 text-slate-400" />;
        }
    };

    const renderProfileTab = () => {
        if (loading) {
            return (
                <div className="flex items-center justify-center py-12">
                    <TruckOrbitSpinner text="Loading user information..." size={72} speed={1.2} />
                </div>
            );
        }

        if (error) {
            return (
                <div className="glass-card p-6 text-center">
                    <div className="text-red-400 text-lg mb-2">⚠️ Error</div>
                    <p className="text-slate-300">{error}</p>
                    <button
                        onClick={fetchUserDetails}
                        className="glass-button mt-4"
                    >
                        Try Again
                    </button>
                </div>
            );
        }

        const userData = userDetails?.user || {};
        const tenantData = userDetails?.tenant || {};
        const planData = userDetails?.plan || {};

        return (
            <div className="space-y-6">
                <div className="flex items-center gap-4 mb-6">
                    <div className="w-20 h-20 rounded-full glass-card flex items-center justify-center">
                        <User className="w-10 h-10 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white">{userData.name || 'User Name'}</h2>
                        <p className="text-slate-300">{userData.email || 'user@example.com'}</p>
                        <div className="flex items-center gap-2 mt-1">
                            {getRoleIcon(userData.role)}
                            <p className="text-slate-400 text-sm">Role: {getRoleDisplayName(userData.role)}</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-card p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                <User className="w-5 h-5" />
                                Personal Information
                            </h3>
                            <div className="flex gap-2">
                                {!editingProfile ? (
                                    <button
                                        onClick={() => setEditingProfile(true)}
                                        className="glass-button flex items-center gap-1"
                                    >
                                        <Edit3 className="w-4 h-4" />
                                        Edit
                                    </button>
                                ) : (
                                    <>
                                        <button
                                            onClick={saveProfileChanges}
                                            disabled={savingProfile}
                                            className="px-3 py-1 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors flex items-center gap-1 disabled:opacity-50"
                                        >
                                            {savingProfile ? (
                                                <div className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
                                            ) : (
                                                <Check className="w-4 h-4" />
                                            )}
                                            Save
                                        </button>
                                        <button
                                            onClick={cancelProfileEdit}
                                            className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors flex items-center gap-1"
                                        >
                                            <X className="w-4 h-4" />
                                            Cancel
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <Mail className="w-5 h-5 text-slate-400" />
                                <div>
                                    <p className="text-sm text-slate-400">Email</p>
                                    <p className="text-white">{userData.email || 'user@example.com'}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <User className="w-5 h-5 text-slate-400" />
                                <div className="flex-1">
                                    <p className="text-sm text-slate-400">Full Name</p>
                                    {editingProfile ? (
                                        <input
                                            type="text"
                                            value={profileForm.name || ''}
                                            onChange={(e) => handleProfileChange('name', e.target.value)}
                                            className="w-full px-3 py-1 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                                            title="Enter your full name"
                                        />
                                    ) : (
                                        <p className="text-white">{userData.name || 'Not provided'}</p>
                                    )}
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <Shield className="w-5 h-5 text-slate-400" />
                                <div>
                                    <p className="text-sm text-slate-400">User ID</p>
                                    <p className="text-white font-mono text-sm">{userData.id || 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Crown className="w-5 h-5" />
                            Account & Subscription
                        </h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                                <span className="text-slate-300 font-medium">Account Type</span>
                                <span className="glass-button text-xs px-3 py-1">
                                    {getRoleDisplayName(userData.role)}
                                </span>
                            </div>
                            <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                                <span className="text-slate-300 font-medium">Status</span>
                                <span className={`text-xs px-3 py-1 rounded-full ${userData.is_active
                                    ? 'bg-green-500/20 text-green-300'
                                    : 'bg-red-500/20 text-red-300'
                                    }`}>
                                    {userData.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                            <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                                <span className="text-slate-300 font-medium">Plan</span>
                                <span className="text-white font-medium">{planData.name || 'Default'}</span>
                            </div>
                            <div className="flex justify-between items-center py-2">
                                <span className="text-slate-300 font-medium">Tenant</span>
                                <span className="text-white font-medium">{tenantData.name || 'Default'}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Location Section */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <MapPin className="w-5 h-5" />
                        Location Information
                    </h3>

                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <MapPin className="w-5 h-5 text-slate-400" />
                            <div>
                                <p className="text-sm text-slate-400">Current Location</p>
                                <p className="text-white">
                                    {locationLoading ? 'Detecting location...' : location?.name || 'Location not available'}
                                </p>
                            </div>
                        </div>

                        {(userData.role === 'admin' || userData.role === 'super_admin') && (
                            <div className="flex gap-2">
                                {!editingLocation ? (
                                    <button
                                        onClick={() => setEditingLocation(true)}
                                        className="glass-button flex items-center gap-1"
                                    >
                                        <Edit3 className="w-4 h-4" />
                                        Edit
                                    </button>
                                ) : (
                                    <>
                                        <button
                                            onClick={updateLocation}
                                            className="px-3 py-1 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors flex items-center gap-1"
                                        >
                                            <Check className="w-4 h-4" />
                                            Save
                                        </button>
                                        <button
                                            onClick={cancelLocationEdit}
                                            className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors flex items-center gap-1"
                                        >
                                            <X className="w-4 h-4" />
                                            Cancel
                                        </button>
                                    </>
                                )}
                            </div>
                        )}
                    </div>

                    {editingLocation && (
                        <div className="mt-4">
                            <input
                                type="text"
                                value={newLocation}
                                onChange={(e) => setNewLocation(e.target.value)}
                                title="Enter new location (e.g., Riyadh, Saudi Arabia)"
                                className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            />
                            <p className="text-xs text-slate-400 mt-1">
                                ⚠️ Location changes require admin approval for security reasons
                            </p>
                        </div>
                    )}
                </div>

                {/* Admin Features Section */}
                {(userData.role === 'admin' || userData.role === 'super_admin') && userDetails?.features && (
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Shield className="w-5 h-5 text-red-400" />
                            Admin Features & Permissions
                        </h3>

                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-4">
                            {userDetails.features.slice(0, 16).map((feature, index) => (
                                <div key={index} className="flex items-center gap-2 text-sm bg-slate-800/30 rounded-lg p-2">
                                    <Check className="w-4 h-4 text-green-400" />
                                    <span className="text-slate-300">{feature}</span>
                                </div>
                            ))}
                            {userDetails.features.length > 16 && (
                                <div className="text-sm text-slate-400 bg-slate-800/30 rounded-lg p-2">
                                    +{userDetails.features.length - 16} more features
                                </div>
                            )}
                        </div>

                        <div className="mt-4 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                            <p className="text-yellow-400 text-sm">
                                <strong>Security Notice:</strong> As an admin, you have access to sensitive operations.
                                All location changes require additional verification for financial data protection.
                            </p>
                        </div>
                    </div>
                )}

                {/* Features & Permissions */}
                {userDetails?.features && !(userData.role === 'admin' || userData.role === 'super_admin') && (
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Star className="w-5 h-5" />
                            Features & Permissions
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {userDetails.features.slice(0, 12).map((feature, index) => (
                                <div key={index} className="flex items-center gap-2 text-sm">
                                    <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                                    <span className="text-slate-300">{feature}</span>
                                </div>
                            ))}
                            {userDetails.features.length > 12 && (
                                <div className="text-sm text-slate-400">
                                    +{userDetails.features.length - 12} more features
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        );
    };

    const renderSecurityTab = () => (
        <div className="space-y-6">
            {/* Password Change Section */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Lock className="w-5 h-5" />
                    Change Password
                </h3>

                {passwordError && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-red-400 text-sm">{passwordError}</p>
                    </div>
                )}

                {passwordSuccess && (
                    <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                        <p className="text-green-400 text-sm">{passwordSuccess}</p>
                    </div>
                )}

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Current Password
                        </label>
                        <input
                            type="password"
                            value={passwordForm.currentPassword}
                            onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            title="Enter your current password"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            New Password
                        </label>
                        <input
                            type="password"
                            value={passwordForm.newPassword}
                            onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            title="Enter your new password"
                        />
                        <p className="text-xs text-slate-400 mt-1">
                            Password must be at least 8 characters long
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Confirm New Password
                        </label>
                        <input
                            type="password"
                            value={passwordForm.confirmPassword}
                            onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            title="Confirm your new password"
                        />
                    </div>

                    <button
                        onClick={handleChangePassword}
                        disabled={changingPassword}
                        className="w-full px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-400/30 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {changingPassword ? (
                            <>
                                <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                                Changing Password...
                            </>
                        ) : (
                            <>
                                <Lock className="w-4 h-4" />
                                Change Password
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Two-Factor Authentication Section */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Two-Factor Authentication</h3>
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-white font-medium">Two-Factor Authentication</p>
                            <p className="text-slate-400 text-sm">Add an extra layer of security to your account</p>
                        </div>
                        <button
                            onClick={startTwoFactorSetup}
                            disabled={twoFactorLoading}
                            className="glass-button disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {twoFactorLoading ? 'Processing...' : 'Enable 2FA'}
                        </button>
                    </div>

                    {twoFactorMessage ? (
                        <p className="text-sm text-emerald-300">{twoFactorMessage}</p>
                    ) : null}

                    {twoFactorError ? (
                        <p className="text-sm text-red-300">{twoFactorError}</p>
                    ) : null}

                    {twoFactorSetup ? (
                        <div className="space-y-3 border border-slate-700/50 rounded-lg p-4 bg-slate-900/30">
                            {twoFactorSetup.qr_code ? (
                                <div>
                                    <p className="text-slate-300 text-sm mb-2">Scan this QR code in your authenticator app:</p>
                                    <img
                                        src={twoFactorSetup.qr_code}
                                        alt="2FA QR code"
                                        className="w-40 h-40 bg-white rounded p-2"
                                    />
                                </div>
                            ) : null}

                            <div>
                                <p className="text-slate-300 text-sm mb-1">Manual setup key:</p>
                                <p className="text-white font-mono break-all text-sm">
                                    {twoFactorSetup.manual_entry_key || twoFactorSetup.secret || 'N/A'}
                                </p>
                            </div>

                            <div className="flex flex-col md:flex-row gap-2">
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    placeholder="Enter 6-digit code"
                                    value={twoFactorCode}
                                    onChange={(e) => setTwoFactorCode(e.target.value)}
                                    className="flex-1 px-3 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                                />
                                <button
                                    onClick={verifyTwoFactorSetup}
                                    disabled={twoFactorLoading}
                                    className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-400/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Verify Code
                                </button>
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>

            {/* Security Log Section */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Security Activity</h3>
                <div className="space-y-3">
                    <div className="flex items-center justify-between py-2 border-b border-slate-700/50">
                        <div>
                            <p className="text-white text-sm">Last password change</p>
                            <p className="text-slate-400 text-xs">30 days ago</p>
                        </div>
                        <RefreshCw className="w-4 h-4 text-slate-400" />
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-slate-700/50">
                        <div>
                            <p className="text-white text-sm">Last login</p>
                            <p className="text-slate-400 text-xs">2 hours ago</p>
                        </div>
                        <LogOut className="w-4 h-4 text-slate-400" />
                    </div>
                </div>
            </div>
        </div>
    );

    const renderNotificationsTab = () => (
        <div className="space-y-6">
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Notification Preferences</h3>
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-white font-medium">Email Notifications</p>
                            <p className="text-slate-400 text-sm">Receive updates via email</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" className="sr-only peer" defaultChecked />
                            <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-white font-medium">Push Notifications</p>
                            <p className="text-slate-400 text-sm">Receive browser notifications</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" className="sr-only peer" />
                            <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderContent = () => {
        switch (activeTab) {
            case 'profile':
                return renderProfileTab();
            case 'security':
                return renderSecurityTab();
            case 'notifications':
                return renderNotificationsTab();
            case 'preferences':
                return <PreferencesPanel />;
            case 'sessions':
                return <SessionsPanel />;
            default:
                return <div className="text-white">{activeTab} settings content</div>;
        }
    };

    return (
        <div className="max-w-6xl mx-auto p-6">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Account Settings</h1>
                <p className="text-slate-300">Manage your personal settings and preferences</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <div className="lg:col-span-1">
                    <div className="glass-card p-4 space-y-2">
                        {[
                            { id: 'profile', label: 'Profile', icon: <User className="w-5 h-5" /> },
                            { id: 'security', label: 'Security', icon: <Lock className="w-5 h-5" /> },
                            { id: 'notifications', label: 'Notifications', icon: <Bell className="w-5 h-5" /> },
                            { id: 'preferences', label: 'Preferences', icon: <Globe className="w-5 h-5" /> },
                            { id: 'sessions', label: 'Active Sessions', icon: <LogOut className="w-5 h-5" /> }
                        ].map(item => (
                            <button
                                key={item.id}
                                onClick={() => setActiveTab(item.id)}
                                className={`w-full text-left p-3 rounded-lg flex items-center justify-between transition-colors ${activeTab === item.id
                                    ? 'bg-blue-500/20 text-blue-300 border border-blue-400/30'
                                    : 'hover:bg-white/10 text-slate-300 hover:text-white'
                                    }`}
                            >
                                <span>{item.label}</span>
                                {item.icon}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="lg:col-span-3">
                    <div className="glass-card p-6">
                        {renderContent()}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserSettings;
