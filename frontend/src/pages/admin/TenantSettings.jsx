import React, { useState } from 'react';
import { Building, Settings, Palette, Link as LinkIcon, Users, Shield } from 'lucide-react';

const TenantSettings = () => {
    const [activeTenant, setActiveTenant] = useState(null);
    const [tenants] = useState([
        { id: 1, name: 'ABC Logistics', domain: 'abc.gts.com', plan: 'Enterprise' }
    ]);
    return (
        <div className="glass-page space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-100">Tenant Management</h1>
                    <p className="text-slate-400">Manage tenant companies and their settings</p>
                </div>
                <button className="glass-btn-primary">+ Add New Tenant</button>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-1">
                    <div className="glass-panel rounded-xl p-4">
                        <h3 className="font-bold text-lg mb-4 text-slate-100">Tenants</h3>
                        <div className="space-y-2">
                            {tenants.map(tenant => (
                                <button
                                    key={tenant.id}
                                    onClick={() => setActiveTenant(tenant)}
                                    className={`w-full text-left p-3 rounded-lg flex items-center justify-between border transition ${activeTenant?.id === tenant.id
                                        ? 'glass-panel border-white/20 shadow-lg'
                                        : 'border-white/5 hover:border-white/15 hover:bg-white/5'
                                        }`}
                                >
                                    <div className="flex items-center">
                                        <Building className="w-5 h-5 text-slate-300" />
                                        <div className="ml-3">
                                            <div className="font-medium text-slate-100">{tenant.name}</div>
                                            <div className="text-sm text-slate-400">{tenant.plan}</div>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
                {activeTenant && (
                    <div className="lg:col-span-3">
                        <div className="glass-panel rounded-xl p-6">
                            <h2 className="text-2xl font-bold mb-4 text-slate-100">{activeTenant.name}</h2>
                            <div className="text-slate-300">Tenant settings content (English only)</div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TenantSettings;
