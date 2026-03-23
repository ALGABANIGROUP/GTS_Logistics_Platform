import axiosClient from "../api/axiosClient";

const API_BASE = "/api/v1/legal-consultant";

const buildContractDraft = ({ carrier, contractType, serviceScope, paymentTerms, notes }) => `
Carrier Agreement Review Request

Carrier:
- Name: ${carrier?.name || "Unknown Carrier"}
- MC Number: ${carrier?.mc_number || "Not provided"}
- Contact Person: ${carrier?.contact_person || "Not provided"}
- Email: ${carrier?.email || "Not provided"}

Contract Details:
- Type: ${contractType}
- Service Scope: ${serviceScope}
- Payment Terms: ${paymentTerms}

Additional Notes:
${notes || "No additional notes provided."}
`.trim();

export const reviewCarrierContract = async ({
    carrier,
    contractType = "carrier_service_agreement",
    serviceScope,
    paymentTerms,
    notes,
}) => {
    const payload = {
        contract_id: carrier?.id ? `carrier-${carrier.id}` : undefined,
        contract_type: contractType,
        content: buildContractDraft({ carrier, contractType, serviceScope, paymentTerms, notes }),
    };

    const response = await axiosClient.post(`${API_BASE}/review-contract`, payload);
    return response?.data;
};

export const getLegalStats = async () => {
    const response = await axiosClient.get(`${API_BASE}/stats`);
    return response?.data || {};
};

const legalConsultantApi = {
    reviewCarrierContract,
    getLegalStats,
};

export default legalConsultantApi;
