import React from 'react';
import { CustomerServicePanel } from './panels/customer-service';

const AICustomerService = () => {
    return (
        <div className="bot-page" style={{ background: '#0f172a', minHeight: '100vh' }}>
            <CustomerServicePanel />
        </div>
    );
};

export default AICustomerService;
