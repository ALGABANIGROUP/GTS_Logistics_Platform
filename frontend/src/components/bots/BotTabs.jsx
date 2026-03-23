/**
 * Bot Tabs Component
 * Tab navigation for the bot control interface
 */
export default function BotTabs({ tabs, activeTab, onTabChange }) {
    return (
        <div className="border-b border-slate-700/50 px-2">
            <div className="flex gap-1 overflow-x-auto scrollbar-thin scrollbar-thumb-slate-600">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => onTabChange(tab.id)}
                        className={`flex items-center gap-2 whitespace-nowrap rounded-t-lg px-4 py-3 text-sm font-medium transition ${activeTab === tab.id
                            ? "border-b-2 border-blue-500 bg-slate-800/60 text-white backdrop-blur"
                            : "text-slate-400 hover:bg-slate-800/40 hover:text-white hover:backdrop-blur"
                            }`}
                    >
                        <span className="text-base">{tab.icon}</span>
                        <span>{tab.name}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
