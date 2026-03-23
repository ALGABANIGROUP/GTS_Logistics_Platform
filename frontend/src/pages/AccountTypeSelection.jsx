import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

const AccountTypeSelection = () => {
  const navigate = useNavigate();

  const handleSelect = (type) => {
    localStorage.setItem("account_type", type);

    const botInstructions = {
      broker: {
        role: "freight_broker_assistant",
        capabilities: ["shipment_matching", "carrier_negotiation", "rate_calculation"],
        auto_actions: ["monitor_shipments", "suggest_carriers", "update_status"],
      },
      carrier: {
        role: "carrier_operations_assistant",
        capabilities: ["load_acceptance", "route_optimization", "document_management"],
        auto_actions: ["scan_new_loads", "optimize_routes", "track_documents"],
      },
      partner: {
        role: "government_data_analyst",
        capabilities: ["compliance_monitoring", "report_generation", "api_integration"],
        auto_actions: ["audit_compliance", "generate_reports", "sync_data"],
      },
    };

    localStorage.setItem("bot_instructions", JSON.stringify(botInstructions[type]));
    navigate("/register");
  };

  const accountTypes = [
    {
      type: "broker",
      title: "Freight Broker",
      description: "Manage shipments and connect with carriers",
      features: ["AI-powered carrier matching", "Automated rate negotiation", "Real-time shipment tracking"],
      color: "from-blue-500 to-blue-700",
      badge: "BR",
    },
    {
      type: "carrier",
      title: "Carrier",
      description: "Receive and manage shipping offers",
      features: ["Smart load acceptance", "Route optimization", "Document automation"],
      color: "from-green-500 to-green-700",
      badge: "CA",
    },
    {
      type: "partner",
      title: "Government / Partner",
      description: "Access dashboards, data and system APIs",
      features: ["Compliance monitoring", "Data analytics", "API integration"],
      color: "from-purple-500 to-purple-700",
      badge: "PT",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Welcome to Gabani Transport Solutions (GTS) AI
          </h1>
          <p className="text-xl text-blue-100 max-w-2xl mx-auto">
            Choose your account type to get started with AI-powered logistics management
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {accountTypes.map((account, index) => (
            <motion.div
              key={account.type}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => handleSelect(account.type)}
              className="cursor-pointer group"
            >
              <div className="bg-white rounded-2xl shadow-2xl p-8 text-center transform transition-all duration-300 group-hover:scale-105 group-hover:shadow-3xl h-full flex flex-col">
                <div className={`w-20 h-20 rounded-full bg-gradient-to-r ${account.color} flex items-center justify-center mx-auto mb-6 text-sm font-semibold`}>
                  {account.badge}
                </div>

                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  {account.title}
                </h2>

                <p className="text-gray-600 mb-6 flex-grow">
                  {account.description}
                </p>

                <ul className="text-sm text-gray-500 space-y-2 mb-6">
                  {account.features.map((feature, i) => (
                    <li key={i} className="flex items-center">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                      {feature}
                    </li>
                  ))}
                </ul>

                <div className="mt-auto">
                  <button className={`w-full py-3 px-6 rounded-lg font-semibold bg-gradient-to-r ${account.color} text-white transition-all duration-300 group-hover:shadow-lg`}>
                    Select {account.type === "partner" ? "Partner" : account.type}
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-12 text-blue-200"
        >
          <p className="text-sm">
            Each account type comes with specialized AI assistants tailored to your needs
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default AccountTypeSelection;
