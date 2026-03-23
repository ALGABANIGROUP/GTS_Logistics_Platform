import React from 'react';
import { useNavigate } from 'react-router-dom';
import './TermsAndConditions.css';

const TermsAndConditions = () => {
    const navigate = useNavigate();

    return (
        <div className="terms-container">
            <div className="terms-content">
                <button
                    onClick={() => navigate(-1)}
                    style={{
                        position: 'absolute',
                        top: '2rem',
                        left: '2rem',
                        background: 'rgba(59, 130, 246, 0.2)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        color: '#60a5fa',
                        padding: '0.5rem 1rem',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        fontWeight: '500',
                        transition: 'all 0.3s ease',
                        backdropFilter: 'blur(10px)',
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(59, 130, 246, 0.3)';
                        e.currentTarget.style.transform = 'translateX(-4px)';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                        e.currentTarget.style.transform = 'translateX(0)';
                    }}
                >
                    ← Back
                </button>

                <header className="terms-header">
                    <h1>Conditions of Service</h1>
                    <div className="company-info">
                        <h2>Gabani Transport Solutions (GTS)</h2>
                        <p>Logistics • Technology • AI-Powered Freight</p>
                    </div>
                </header>

                <section className="terms-section">
                    <h3>1. DEFINITIONS</h3>
                    <ul>
                        <li><strong>Company</strong> refers to Gabani Transport Solutions (GTS), a licensed freight broker.</li>
                        <li><strong>Customer</strong> refers to any individual or entity utilizing the Company's services.</li>
                        <li><strong>Carrier</strong> refers to the third-party trucking company or transporter contracted to transport shipments.</li>
                        <li><strong>Shipment</strong> refers to the goods being transported as per the Customer's request.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>2. ROLE OF THE BROKER</h3>
                    <ul>
                        <li>Gabani Transport Solutions (GTS) operates solely as a freight broker and does not own or operate any trucks or transport equipment.</li>
                        <li>The Company arranges transportation services on behalf of Customers with authorized Carriers.</li>
                        <li>The Company assumes no liability for the actual transportation, loss, or damage to shipments.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>3. LIMITATION OF LIABILITY</h3>
                    <ul>
                        <li>The Company is not liable for any cargo loss, delay, damage, or theft.</li>
                        <li>The Carrier is solely responsible for the shipment's condition, timely delivery, and any claims related to loss or damage.</li>
                        <li>The Customer agrees to pursue any claims directly with the Carrier and not the Broker.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>4. PAYMENT TERMS</h3>
                    <ul>
                        <li>All invoices must be paid within 15 days from the invoice date unless otherwise agreed in writing.</li>
                        <li>Late payments are subject to a 5% penalty per month.</li>
                        <li>The Company reserves the right to withhold services for overdue accounts.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>5. CANCELLATION & CHANGES</h3>
                    <ul>
                        <li>Cancellations made before dispatching a Carrier are subject to a $50 processing fee.</li>
                        <li>Once a Carrier has been dispatched, cancellations are non-refundable.</li>
                        <li>Any changes to the shipment details after dispatch may result in additional charges.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>6. CUSTOMER OBLIGATIONS</h3>
                    <ul>
                        <li>The Customer is responsible for ensuring that the shipment is properly packaged, labeled, and complies with all regulations.</li>
                        <li>Any incorrect or incomplete information provided by the Customer may result in delays or additional fees.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>7. CARRIER RESPONSIBILITIES</h3>
                    <ul>
                        <li>Carriers must comply with all FMCSA regulations and maintain proper licensing and insurance.</li>
                        <li>Carriers must provide accurate tracking and delivery updates.</li>
                        <li>Any delays or damages caused by the Carrier must be reported immediately.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>8. INSURANCE & CLAIMS</h3>
                    <ul>
                        <li>The Company does not provide cargo insurance.</li>
                        <li>The Customer must ensure that the Carrier's insurance is adequate for their shipment.</li>
                        <li>Any claims for loss or damage must be filed with the Carrier within 30 days of delivery.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>9. GOVERNING LAW</h3>
                    <ul>
                        <li>These Terms & Conditions shall be governed by the laws of the State of Texas, USA.</li>
                        <li>Any disputes shall be resolved through arbitration in Austin, Texas.</li>
                    </ul>
                </section>

                <section className="terms-section">
                    <h3>10. AMENDMENTS</h3>
                    <ul>
                        <li>The Company reserves the right to modify these Terms & Conditions at any time.</li>
                        <li>Continued use of services constitutes acceptance of any amendments.</li>
                    </ul>
                </section>

                <section className="terms-contact">
                    <h3>Contact Information</h3>

                    <div className="contact-section">
                        <h4>Main Emails</h4>
                        <div className="contact-item">
                            <span className="label">Support & Help:</span>
                            <a href="mailto:support@gabanistore.com">support@gabanistore.com</a>
                        </div>
                        <div className="contact-item">
                            <span className="label">Operations:</span>
                            <a href="mailto:operations@gabanilogistics.com">operations@gabanilogistics.com</a>
                        </div>
                        <div className="contact-item">
                            <span className="label">Investments:</span>
                            <a href="mailto:investments@gabanilogistics.com">investments@gabanilogistics.com</a>
                        </div>
                        <div className="contact-item">
                            <span className="label">Customer Service:</span>
                            <a href="mailto:customers@gabanilogistics.com">customers@gabanilogistics.com</a>
                        </div>
                    </div>

                    <div className="contact-section">
                        <h4>Phone</h4>
                        <div className="contact-item">
                            <a href="tel:+17786518297">+1 (778) 651-8297</a>
                        </div>
                    </div>
                </section>

                <div className="terms-footer">
                    <p>Last Updated: February 2026</p>
                    <p>© 2026 Gabani Transport Solutions (GTS). All rights reserved.</p>
                </div>
            </div>
        </div>
    );
};

export default TermsAndConditions;
