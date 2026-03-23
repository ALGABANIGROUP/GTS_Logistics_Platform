/**
 *  MDP - MapleLoad Canada Control Panel
 * Canadian Market Penetration Control Center for GTS Logistics
 */
import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "mapleload_canada";

// Tab definitions
const CONTROL_TABS = [
    { id: "lead_generation", name: "Lead Generation", icon: "" },
    { id: "outreach_automation", name: "Outreach Automation", icon: "" },
    { id: "geographic_analysis", name: "Geographic Analysis", icon: "" },
    { id: "campaign_management", name: "Campaign Management", icon: "" },
];

// Canadian provinces
const PROVINCES = [
    { code: "ON", name: "Ontario", icon: "" },
    { code: "QC", name: "Quebec", icon: "" },
    { code: "BC", name: "British Columbia", icon: "" },
    { code: "AB", name: "Alberta", icon: "" },
    { code: "MB", name: "Manitoba", icon: "" },
    { code: "SK", name: "Saskatchewan", icon: "" },
    { code: "NS", name: "Nova Scotia", icon: "" },
    { code: "NB", name: "New Brunswick", icon: "" },
];

// Outreach controls
const OUTREACH_CONTROLS = [
    { action: "start_campaign", label: " New Campaign", color: "emerald" },
    { action: "pause_outreach", label: " Pause All", color: "amber" },
    { action: "analyze_response", label: " Analyze", color: "blue" },
    { action: "export_leads", label: " Export", color: "purple" },
];

// Industry targets
const TARGET_INDUSTRIES = [
    { name: "Manufacturing", companies: 4250, contacted: 1890, conversion: "12%" },
    { name: "Logistics & Transport", companies: 2180, contacted: 1245, conversion: "18%" },
    { name: "Retail & Distribution", companies: 3420, contacted: 890, conversion: "9%" },
    { name: "Food & Beverage", companies: 1890, contacted: 678, conversion: "15%" },
    { name: "Construction", companies: 2780, contacted: 456, conversion: "7%" },
];

export default function MapleLoadControlPanel({ mode = "active" }) {
    const isPreview = mode === "preview";
    const [activeTab, setActiveTab] = useState("lead_generation");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);

    // Control panel data state
    const [panelData, setPanelData] = useState({
        // Provincial metrics
        provincialMetrics: [],
        // Database stats
        databaseStats: {
            totalCompanies: 0,
            verifiedContacts: 0,
            engagementRate: "0%",
        },
        // Active searches
        activeSearches: {
            count: 0,
            companiesFoundToday: 0,
            criteria: { regions: [], industries: [], companySize: "" },
        },
        // Email campaigns
        emailCampaigns: [],
        // Campaign scheduler
        campaignScheduler: {
            nextCampaign: "",
            scheduledFor: "",
            targetSize: 0,
        },
        // Geographic hot zones
        geographicAnalysis: {
            hotZones: [],
            opportunityZones: [],
        },
    });

    // Load data from API
    const loadPanelData = useCallback(async () => {
        if (isPreview) return;
        setLoading(true);
        try {
            const [statusRes, leadsRes] = await Promise.all([
                axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`).catch(() => null),
                axiosClient.get("/api/v1/leads/stats").catch(() => null),
            ]);

            if (statusRes?.data || leadsRes?.data) {
                setConnected(true);
                // Update with real data when available
            }
            setLastUpdate(new Date());
        } catch (err) {
            console.warn("Panel data load error:", err);
        } finally {
            setLoading(false);
        }
    }, [isPreview]);

    useEffect(() => {
        loadPanelData();
    }, [loadPanelData]);

    // Connect to APIs (simulation)
    const handleConnectAPIs = () => {
        setConnected(true);
        setPanelData({
            provincialMetrics: [],
            databaseStats: {
                totalCompanies: 0,
                verifiedContacts: 0,
                engagementRate: "0%",
            },
            activeSearches: {
                count: 0,
                companiesFoundToday: 147,
                criteria: {
                    regions: ["Ontario", "Quebec", "BC"],
                    industries: ["Manufacturing", "Logistics", "Retail"],
                    companySize: "50+ employees",
                },
            },
            emailCampaigns: [
                {
                    name: "Manufacturing Outreach Q4",
                    sent: 2450,
                    opened: 1234,
                    replied: 245,
                    conversion: "10%",
                    status: "Active",
                },
                {
                    name: "Logistics Partners BC",
                    sent: 890,
                    opened: 534,
                    replied: 89,
                    conversion: "10%",
                    status: "Active",
                },
                {
                    name: "Retail Distribution ON",
                    sent: 1200,
                    opened: 456,
                    replied: 34,
                    conversion: "2.8%",
                    status: "Paused",
                },
            ],
            campaignScheduler: {
                nextCampaign: "Western Canada Expansion",
                scheduledFor: "Tomorrow 9:00 AM EST",
                targetSize: 500,
            },
            geographicAnalysis: {
                hotZones: ["Greater Toronto Area", "Metro Vancouver", "Calgary Region", "Montreal Metro"],
                opportunityZones: ["Saskatchewan", "Manitoba", "Maritimes", "Northern Ontario"],
            },
        });
        setLastUpdate(new Date());
    };

    // Execute action
    const executeAction = async (action) => {
        if (isPreview) return;
        try {
            await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
                message: action,
                context: {},
                meta: { source: "mapleload_control_panel" },
            });
            await loadPanelData();
        } catch (err) {
            console.error("Action failed:", err);
        }
    };

    return (
        <div className="min-h-screen space-y-4">
            {/* Control Panel Header */}
            <header className="rounded-2xl border border-white/10 bg-gradient-to-br from-red-900/30 via-slate-900/90 to-white/5 p-5 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    {/* Title Section */}
                    <div className="flex items-center gap-4">
                        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-red-500 to-red-700 text-4xl shadow-lg shadow-red-500/30">

                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">
                                MAPLELOAD CANADA COMMAND
                            </h1>
                            <p className="text-sm text-slate-400">
                                MDP Canadian Market Penetration Control
                            </p>
                        </div>
                    </div>

                    {/* Status & Controls */}
                    <div className="flex items-center gap-3">
                        <ConnectionStatus connected={connected} />
                        {!connected && (
                            <button
                                onClick={handleConnectAPIs}
                                disabled={isPreview}
                                className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-red-500/30 transition hover:bg-red-500 disabled:opacity-50"
                            >
                                Connect Database
                            </button>
                        )}
                        <button
                            onClick={loadPanelData}
                            disabled={loading || isPreview}
                            className="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20 disabled:opacity-50"
                        >
                            <span className={loading ? "animate-spin" : ""}></span>
                        </button>
                    </div>
                </div>

                {/* Provincial Metrics */}
                <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                    {panelData.provincialMetrics.length > 0 ? (
                        panelData.provincialMetrics.map((prov) => (
                            <ProvinceCard key={prov.province} data={prov} />
                        ))
                    ) : (
                        PROVINCES.slice(0, 6).map((prov) => (
                            <div key={prov.code} className="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
                                <span className="text-xl">{prov.icon}</span>
                                <div className="mt-1 text-xs text-slate-400">{prov.name}</div>
                                <div className="text-lg font-bold text-slate-500">--</div>
                            </div>
                        ))
                    )}
                </div>

                {/* Outreach Controls */}
                <div className="mt-4 flex flex-wrap gap-2">
                    {OUTREACH_CONTROLS.map((ctrl) => (
                        <OutreachButton
                            key={ctrl.action}
                            control={ctrl}
                            onClick={() => executeAction(ctrl.action)}
                            disabled={isPreview}
                        />
                    ))}
                </div>
            </header>

            {/* Preview Banner */}
            {isPreview && (
                <div className="rounded-xl border border-amber-400/30 bg-amber-500/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                        <span className="text-amber-400"></span>
                        <span className="text-sm font-semibold text-amber-100">
                            Preview Mode - Canadian database not connected
                        </span>
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            <div className="flex gap-4">
                {/* Tab Navigation */}
                <nav className="hidden w-56 flex-shrink-0 space-y-1 lg:block">
                    {CONTROL_TABS.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition ${activeTab === tab.id
                                ? "bg-red-600/30 text-white"
                                : "text-slate-400 hover:bg-white/5 hover:text-slate-300"
                                }`}
                        >
                            <span className="text-lg">{tab.icon}</span>
                            {tab.name}
                        </button>
                    ))}
                </nav>

                {/* Mobile Tab Bar */}
                <div className="mb-4 flex gap-2 overflow-x-auto pb-2 lg:hidden">
                    {CONTROL_TABS.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${activeTab === tab.id
                                ? "bg-red-600/30 text-white"
                                : "bg-white/5 text-slate-400"
                                }`}
                        >
                            <span>{tab.icon}</span>
                            {tab.name}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <main className="flex-1 space-y-4">
                    {activeTab === "lead_generation" && (
                        <LeadGenerationTab panelData={panelData} industries={TARGET_INDUSTRIES} />
                    )}
                    {activeTab === "outreach_automation" && (
                        <OutreachAutomationTab panelData={panelData} onAction={executeAction} disabled={isPreview} />
                    )}
                    {activeTab === "geographic_analysis" && (
                        <GeographicAnalysisTab panelData={panelData} provinces={PROVINCES} />
                    )}
                    {activeTab === "campaign_management" && (
                        <CampaignManagementTab panelData={panelData} onAction={executeAction} disabled={isPreview} />
                    )}
                </main>

                {/* Canadian Market Sidebar */}
                <aside className="hidden w-64 flex-shrink-0 space-y-4 xl:block">
                    {/* Connection Status */}
                    <SidebarSection title=" CONNECTION STATUS">
                        <SidebarStatus
                            icon=""
                            label="Database Connection"
                            status={connected ? "Connected" : "Not Connected"}
                            color={connected ? "green" : "red"}
                        />
                        <SidebarStatus
                            icon=""
                            label="Email Service"
                            status={connected ? "Configured" : "Not Configured"}
                            color={connected ? "green" : "red"}
                        />
                        <SidebarStatus
                            icon=""
                            label="API Keys"
                            status={connected ? "Active" : "Missing"}
                            color={connected ? "green" : "red"}
                        />
                    </SidebarSection>

                    {/* Database Stats */}
                    <SidebarSection title=" DATABASE STATS">
                        <SidebarMetric label="Total Companies" value={panelData.databaseStats.totalCompanies.toLocaleString()} color="blue" />
                        <SidebarMetric label="Verified Contacts" value={panelData.databaseStats.verifiedContacts.toLocaleString()} color="green" />
                        <SidebarMetric label="Engagement Rate" value={panelData.databaseStats.engagementRate} color="amber" />
                    </SidebarSection>

                    {/* Active Searches */}
                    <SidebarSection title=" ACTIVE SEARCHES">
                        <div className="rounded-lg bg-emerald-500/10 p-3 text-center">
                            <div className="text-2xl font-bold text-emerald-400">{panelData.activeSearches.count}</div>
                            <div className="text-xs text-slate-400">Running Searches</div>
                        </div>
                        <div className="rounded-lg bg-blue-500/10 p-3 text-center">
                            <div className="text-2xl font-bold text-blue-400">{panelData.activeSearches.companiesFoundToday}</div>
                            <div className="text-xs text-slate-400">Found Today</div>
                        </div>
                    </SidebarSection>

                    {/* Quick Actions */}
                    <SidebarSection title=" QUICK ACTIONS">
                        <SidebarButton icon="" label="Search Companies" onClick={() => executeAction("search_companies")} />
                        <SidebarButton icon="" label="Send Campaign" onClick={() => executeAction("send_campaign")} />
                        <SidebarButton icon="" label="Generate Report" onClick={() => executeAction("generate_report")} />
                    </SidebarSection>
                </aside>
            </div>

            {/* Status Bar Footer */}
            <footer className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                <div className="flex flex-wrap items-center justify-between gap-4 text-xs">
                    <div className="flex flex-wrap gap-6">
                        <FooterStat label="Last Update" value={lastUpdate?.toLocaleTimeString() || "Never"} />
                        <FooterStat label="Database" value={connected ? " Connected" : " Offline"} />
                        <FooterStat label="Active Campaigns" value={panelData.emailCampaigns.filter(c => c.status === "Active").length.toString()} />
                        <FooterStat label="Engagement" value={panelData.databaseStats.engagementRate} />
                    </div>
                    <Link
                        to="/ai-bots/control?bot=mapleload_canada"
                        className="text-red-400 hover:text-red-300"
                    >
                        Advanced Settings
                    </Link>
                </div>
            </footer>
        </div>
    );
}

// 
// SUB-COMPONENTS
// 

function ConnectionStatus({ connected }) {
    return (
        <div
            className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold ${connected
                ? "bg-emerald-500/20 text-emerald-300"
                : "bg-slate-500/20 text-slate-400"
                }`}
        >
            <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500 animate-pulse" : "bg-slate-500"}`} />
            {connected ? " CONNECTED" : " OFFLINE"}
        </div>
    );
}

function ProvinceCard({ data }) {
    const statusColors = {
        Hot: "from-red-500/20 to-red-600/10 border-red-500/30",
        Warm: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
        Cold: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
    };

    return (
        <div className={`rounded-lg border bg-gradient-to-br p-3 text-center ${statusColors[data.status]}`}>
            <div className="text-xs font-medium text-slate-400">{data.province}</div>
            <div className="mt-1 text-lg font-bold text-white">{data.leads.toLocaleString()}</div>
            <div className={`text-xs font-semibold ${data.growth.startsWith("+") ? "text-emerald-400" : "text-rose-400"}`}>
                {data.growth}
            </div>
        </div>
    );
}

function OutreachButton({ control, onClick, disabled }) {
    const colorClasses = {
        emerald: "bg-emerald-600/80 hover:bg-emerald-500/80 shadow-emerald-500/30",
        amber: "bg-amber-600/80 hover:bg-amber-500/80 shadow-amber-500/30",
        blue: "bg-blue-600/80 hover:bg-blue-500/80 shadow-blue-500/30",
        purple: "bg-purple-600/80 hover:bg-purple-500/80 shadow-purple-500/30",
    };

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-semibold text-white shadow-lg transition disabled:opacity-50 ${colorClasses[control.color]}`}
        >
            {control.label}
        </button>
    );
}

function SidebarSection({ title, children }) {
    return (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                {title}
            </h4>
            <div className="space-y-2">{children}</div>
        </div>
    );
}

function SidebarButton({ icon, label, onClick }) {
    return (
        <button
            onClick={onClick}
            className="flex w-full items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-sm text-slate-300 transition hover:bg-white/10"
        >
            <span>{icon}</span>
            {label}
        </button>
    );
}

function SidebarMetric({ label, value, color }) {
    const colorClasses = {
        green: "text-emerald-400",
        blue: "text-blue-400",
        amber: "text-amber-400",
        red: "text-red-400",
    };

    return (
        <div className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
            <span className="text-sm text-slate-400">{label}</span>
            <span className={`font-semibold ${colorClasses[color]}`}>{value}</span>
        </div>
    );
}

function SidebarStatus({ icon, label, status, color }) {
    const colorClasses = {
        green: "text-emerald-400",
        blue: "text-blue-400",
        amber: "text-amber-400",
        red: "text-rose-400",
    };

    const statusIcon = color === "green" ? "" : "";

    return (
        <div className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
            <span className="flex items-center gap-2 text-sm text-slate-400">
                <span>{icon}</span>
                {label}
            </span>
            <span className={`flex items-center gap-1 text-xs font-semibold ${colorClasses[color]}`}>
                {statusIcon} {status}
            </span>
        </div>
    );
}

function FooterStat({ label, value }) {
    return (
        <div>
            <span className="text-slate-500">{label}: </span>
            <span className="font-medium text-slate-300">{value}</span>
        </div>
    );
}

// 
// TAB CONTENT COMPONENTS
// 

function LeadGenerationTab({ panelData, industries }) {
    return (
        <div className="space-y-4">
            {/* Search Criteria */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Company Search Engine
                </h3>
                <div className="grid gap-4 md:grid-cols-3">
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Target Regions</label>
                        <div className="flex flex-wrap gap-1">
                            {panelData.activeSearches.criteria.regions.length > 0 ? (
                                panelData.activeSearches.criteria.regions.map((region) => (
                                    <span key={region} className="rounded bg-red-500/20 px-2 py-1 text-xs text-red-300">
                                        {region}
                                    </span>
                                ))
                            ) : (
                                <span className="text-xs text-slate-500 italic">Not configured</span>
                            )}
                        </div>
                    </div>
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Target Industries</label>
                        <div className="flex flex-wrap gap-1">
                            {panelData.activeSearches.criteria.industries.length > 0 ? (
                                panelData.activeSearches.criteria.industries.map((industry) => (
                                    <span key={industry} className="rounded bg-blue-500/20 px-2 py-1 text-xs text-blue-300">
                                        {industry}
                                    </span>
                                ))
                            ) : (
                                <span className="text-xs text-slate-500 italic">Not configured</span>
                            )}
                        </div>
                    </div>
                    <div>
                        <label className="mb-2 block text-xs text-slate-400">Company Size</label>
                        <span className="rounded bg-purple-500/20 px-2 py-1 text-xs text-purple-300">
                            {panelData.activeSearches.criteria.companySize || "Not set"}
                        </span>
                    </div>
                </div>
            </div>

            {/* Industry Targets */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Industry Target Performance
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-white/10 text-left text-xs uppercase text-slate-500">
                                <th className="pb-3 pr-4">Industry</th>
                                <th className="pb-3 pr-4 text-center">Total Companies</th>
                                <th className="pb-3 pr-4 text-center">Contacted</th>
                                <th className="pb-3 pr-4 text-center">Conversion</th>
                                <th className="pb-3 text-center">Progress</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {industries.map((industry) => (
                                <tr key={industry.name} className="text-slate-300">
                                    <td className="py-3 pr-4 font-medium">{industry.name}</td>
                                    <td className="py-3 pr-4 text-center">{industry.companies.toLocaleString()}</td>
                                    <td className="py-3 pr-4 text-center text-blue-400">{industry.contacted.toLocaleString()}</td>
                                    <td className="py-3 pr-4 text-center">
                                        <span className={`font-semibold ${parseFloat(industry.conversion) >= 15 ? "text-emerald-400" :
                                            parseFloat(industry.conversion) >= 10 ? "text-amber-400" :
                                                "text-rose-400"
                                            }`}>
                                            {industry.conversion}
                                        </span>
                                    </td>
                                    <td className="py-3 text-center">
                                        <div className="mx-auto h-2 w-24 overflow-hidden rounded-full bg-white/10">
                                            <div
                                                className="h-full bg-gradient-to-r from-red-500 to-red-400"
                                                style={{ width: `${(industry.contacted / industry.companies) * 100}%` }}
                                            />
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function OutreachAutomationTab({ panelData, onAction, disabled }) {
    return (
        <div className="space-y-4">
            {/* Email Campaigns */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Active Email Campaigns
                </h3>
                <div className="space-y-3">
                    {panelData.emailCampaigns.length > 0 ? (
                        panelData.emailCampaigns.map((campaign, i) => (
                            <div key={i} className="rounded-lg border border-white/10 bg-white/5 p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <span className="font-semibold text-white">{campaign.name}</span>
                                            <span className={`rounded-full px-2 py-0.5 text-xs ${campaign.status === "Active"
                                                ? "bg-emerald-500/20 text-emerald-300"
                                                : "bg-slate-500/20 text-slate-400"
                                                }`}>
                                                {campaign.status}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-lg font-bold text-emerald-400">{campaign.conversion}</div>
                                        <div className="text-xs text-slate-400">Conversion</div>
                                    </div>
                                </div>
                                <div className="mt-3 grid grid-cols-4 gap-3 text-center">
                                    <div>
                                        <div className="text-lg font-semibold text-white">{campaign.sent.toLocaleString()}</div>
                                        <div className="text-xs text-slate-500">Sent</div>
                                    </div>
                                    <div>
                                        <div className="text-lg font-semibold text-blue-400">{campaign.opened.toLocaleString()}</div>
                                        <div className="text-xs text-slate-500">Opened</div>
                                    </div>
                                    <div>
                                        <div className="text-lg font-semibold text-purple-400">{campaign.replied}</div>
                                        <div className="text-xs text-slate-500">Replied</div>
                                    </div>
                                    <div>
                                        <div className="text-lg font-semibold text-slate-400">
                                            {((campaign.opened / campaign.sent) * 100).toFixed(0)}%
                                        </div>
                                        <div className="text-xs text-slate-500">Open Rate</div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="py-8 text-center text-slate-500">
                            Connect to view active campaigns
                        </div>
                    )}
                </div>
            </div>

            {/* Next Scheduled Campaign */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Next Scheduled Campaign
                </h3>
                {panelData.campaignScheduler.nextCampaign ? (
                    <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-lg font-semibold text-white">{panelData.campaignScheduler.nextCampaign}</div>
                                <div className="text-sm text-slate-400">
                                    Scheduled: {panelData.campaignScheduler.scheduledFor}
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-2xl font-bold text-emerald-400">
                                    {panelData.campaignScheduler.targetSize}
                                </div>
                                <div className="text-xs text-slate-400">Target Companies</div>
                            </div>
                        </div>
                        <div className="mt-4 flex gap-2">
                            <button
                                onClick={() => onAction("launch_campaign_now")}
                                disabled={disabled}
                                className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-50"
                            >
                                Launch Now
                            </button>
                            <button
                                onClick={() => onAction("edit_campaign")}
                                disabled={disabled}
                                className="rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/20 disabled:opacity-50"
                            >
                                Edit
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="py-8 text-center text-slate-500">
                        No campaigns scheduled
                    </div>
                )}
            </div>
        </div>
    );
}

function GeographicAnalysisTab({ panelData, provinces }) {
    return (
        <div className="space-y-4">
            {/* Canadian Map Placeholder */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Canadian Market Heat Map
                </h3>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                    {provinces.map((prov) => (
                        <div key={prov.code} className="rounded-lg bg-white/5 p-4 text-center transition hover:bg-white/10">
                            <span className="text-3xl">{prov.icon}</span>
                            <div className="mt-2 font-semibold text-white">{prov.name}</div>
                            <div className="text-xs text-slate-400">{prov.code}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Hot Zones */}
            <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> HOT ZONES
                    </h3>
                    <div className="space-y-2">
                        {panelData.geographicAnalysis.hotZones.length > 0 ? (
                            panelData.geographicAnalysis.hotZones.map((zone, i) => (
                                <div key={i} className="flex items-center gap-2 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-300">
                                    <span></span>
                                    {zone}
                                </div>
                            ))
                        ) : (
                            <div className="text-sm text-slate-500 italic">No hot zones identified</div>
                        )}
                    </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                        <span></span> OPPORTUNITY ZONES
                    </h3>
                    <div className="space-y-2">
                        {panelData.geographicAnalysis.opportunityZones.length > 0 ? (
                            panelData.geographicAnalysis.opportunityZones.map((zone, i) => (
                                <div key={i} className="flex items-center gap-2 rounded-lg bg-blue-500/10 px-3 py-2 text-sm text-blue-300">
                                    <span></span>
                                    {zone}
                                </div>
                            ))
                        ) : (
                            <div className="text-sm text-slate-500 italic">No opportunity zones identified</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function CampaignManagementTab({ panelData, onAction, disabled }) {
    return (
        <div className="space-y-4">
            {/* Campaign Templates */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Campaign Templates
                </h3>
                <div className="grid gap-3 md:grid-cols-2">
                    {[
                        { name: "Cold Outreach - Manufacturing", type: "Email", success: "12%" },
                        { name: "Warm Lead Follow-up", type: "Email + Call", success: "28%" },
                        { name: "Re-engagement Campaign", type: "Email", success: "8%" },
                        { name: "Premium Partner Intro", type: "Custom", success: "35%" },
                    ].map((template, i) => (
                        <div key={i} className="rounded-lg border border-white/10 bg-white/5 p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="font-semibold text-white">{template.name}</div>
                                    <div className="text-xs text-slate-400">{template.type}</div>
                                </div>
                                <div className="text-right">
                                    <div className="font-bold text-emerald-400">{template.success}</div>
                                    <div className="text-xs text-slate-500">Success Rate</div>
                                </div>
                            </div>
                            <button
                                onClick={() => onAction(`use_template_${i}`)}
                                disabled={disabled}
                                className="mt-3 w-full rounded-lg bg-red-600/80 py-2 text-sm font-semibold text-white hover:bg-red-500 disabled:opacity-50"
                            >
                                Use Template
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Campaign Analytics */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
                    <span></span> Campaign Analytics Summary
                </h3>
                <div className="grid gap-4 md:grid-cols-4">
                    <div className="rounded-lg bg-blue-500/10 p-4 text-center">
                        <div className="text-2xl font-bold text-blue-400">
                            {panelData.emailCampaigns.reduce((acc, c) => acc + c.sent, 0).toLocaleString()}
                        </div>
                        <div className="text-sm text-slate-400">Total Sent</div>
                    </div>
                    <div className="rounded-lg bg-emerald-500/10 p-4 text-center">
                        <div className="text-2xl font-bold text-emerald-400">
                            {panelData.emailCampaigns.reduce((acc, c) => acc + c.opened, 0).toLocaleString()}
                        </div>
                        <div className="text-sm text-slate-400">Total Opened</div>
                    </div>
                    <div className="rounded-lg bg-purple-500/10 p-4 text-center">
                        <div className="text-2xl font-bold text-purple-400">
                            {panelData.emailCampaigns.reduce((acc, c) => acc + c.replied, 0).toLocaleString()}
                        </div>
                        <div className="text-sm text-slate-400">Total Replies</div>
                    </div>
                    <div className="rounded-lg bg-amber-500/10 p-4 text-center">
                        <div className="text-2xl font-bold text-amber-400">
                            {panelData.emailCampaigns.length > 0
                                ? (panelData.emailCampaigns.reduce((acc, c) => acc + parseFloat(c.conversion), 0) / panelData.emailCampaigns.length).toFixed(1)
                                : "0"}%
                        </div>
                        <div className="text-sm text-slate-400">Avg Conversion</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
