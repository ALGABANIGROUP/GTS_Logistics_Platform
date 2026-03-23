import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import {
    TrendingUp,
    Users,
    Zap,
    AlertCircle,
    Download,
    RefreshCw,
} from 'lucide-react';
import './MLDashboard.css';

const MLDashboard = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [refreshing, setRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [customersData, setCustomersData] = useState({});
    const [driversData, setDriversData] = useState({});
    const [revenueData, setRevenueData] = useState({});

    // Fetch data
    const fetchData = async () => {
        setLoading(true);
        try {
            const [customersRes, driversRes] = await Promise.all([
                axiosClient.get('/api/v1/ml/customers/top?limit=10').catch(() => ({ data: {} })),
                axiosClient.get('/api/v1/ml/drivers/top-performers?limit=10').catch(() => ({ data: {} })),
            ]);
            setCustomersData(customersRes.data);
            setDriversData(driversRes.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        setRefreshing(true);
        await fetchData();
        setRefreshing(false);
    };

    useEffect(() => {
        fetchData();
    }, []);

    const SummaryCard = ({ icon: Icon, title, value, trend, color }) => (
        <div className={`summary-card summary-card-${color}`}>
            <div className="summary-card-header">
                <Icon className="summary-card-icon" />
                <span className="summary-card-title">{title}</span>
            </div>
            <div className="summary-card-content">
                <div className="summary-card-value">{value}</div>
                {trend && (
                    <div className={`summary-card-trend ${trend.positive ? 'positive' : 'negative'}`}>
                        <TrendingUp size={16} />
                        <span>{trend.value}% {trend.label}</span>
                    </div>
                )}
            </div>
        </div>
    );

    const revenueTrendData = [
        { day: 'Mon', revenue: 4000 },
        { day: 'Tue', revenue: 4500 },
        { day: 'Wed', revenue: 3800 },
        { day: 'Thu', revenue: 5200 },
        { day: 'Fri', revenue: 5800 },
        { day: 'Sat', revenue: 6200 },
        { day: 'Sun', revenue: 4500 },
    ];

    const customerScoresData = [
        { name: 'Customer A', score: 95 },
        { name: 'Customer B', score: 88 },
        { name: 'Customer C', score: 82 },
        { name: 'Customer D', score: 78 },
        { name: 'Customer E', score: 75 },
    ];

    const driverPerformanceData = [
        { name: 'Driver 1', onTimeRate: 98, rating: 95 },
        { name: 'Driver 2', onTimeRate: 96, rating: 92 },
        { name: 'Driver 3', onTimeRate: 94, rating: 89 },
        { name: 'Driver 4', onTimeRate: 91, rating: 85 },
        { name: 'Driver 5', onTimeRate: 88, rating: 82 },
    ];

    return (
        <div className="ml-dashboard">
            <div className="ml-dashboard-header">
                <div className="ml-dashboard-title">
                    <Zap className="title-icon" />
                    <h1>Machine Learning Insights</h1>
                </div>
                <button
                    className={`refresh-button ${refreshing ? 'refreshing' : ''}`}
                    onClick={handleRefresh}
                    disabled={refreshing}
                >
                    <RefreshCw size={18} />
                    {refreshing ? 'Refreshing...' : 'Refresh Data'}
                </button>
            </div>

            {loading && (
                <div className="loading-container">
                    <div className="spinner" />
                    <p>Loading AI insights...</p>
                </div>
            )}

            {!loading && (
                <>
                    {/* Summary Cards */}
                    <div className="summary-cards-grid">
                        <SummaryCard
                            icon={Users}
                            title="Top Customers"
                            value={customersData?.count || 0}
                            trend={{ value: 12, label: 'increase', positive: true }}
                            color="blue"
                        />
                        <SummaryCard
                            icon={TrendingUp}
                            title="Revenue This Month"
                            value="$45,000"
                            trend={{ value: 8, label: 'growth', positive: true }}
                            color="green"
                        />
                        <SummaryCard
                            icon={Zap}
                            title="System Health"
                            value="95%"
                            trend={{ value: 2, label: 'optimal', positive: true }}
                            color="purple"
                        />
                        <SummaryCard
                            icon={AlertCircle}
                            title="Active Alerts"
                            value="3"
                            trend={{ value: 1, label: 'monitoring', positive: false }}
                            color="orange"
                        />
                    </div>

                    {/* Tabs */}
                    <div className="ml-dashboard-tabs">
                        <button
                            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                            onClick={() => setActiveTab('overview')}
                        >
                            Overview
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'customers' ? 'active' : ''}`}
                            onClick={() => setActiveTab('customers')}
                        >
                            Customer Analytics
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'drivers' ? 'active' : ''}`}
                            onClick={() => setActiveTab('drivers')}
                        >
                            Driver Performance
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'forecast' ? 'active' : ''}`}
                            onClick={() => setActiveTab('forecast')}
                        >
                            Demand Forecast
                        </button>
                    </div>

                    {/* Overview Tab */}
                    {activeTab === 'overview' && (
                        <div className="ml-dashboard-content">
                            <div className="insights-section">
                                <h3>Key Insights</h3>
                                <div className="insights-list">
                                    <div className="insight-item">
                                        <div className="insight-number">1</div>
                                        <div className="insight-content">
                                            <h4>Top Customer: Premium Account Holder</h4>
                                            <p>Has placed 45+ orders with 98% on-time delivery rate</p>
                                        </div>
                                    </div>
                                    <div className="insight-item">
                                        <div className="insight-number">2</div>
                                        <div className="insight-content">
                                            <h4>Revenue Growth: +15% YoY</h4>
                                            <p>Peak demand expected on weekends during winter months</p>
                                        </div>
                                    </div>
                                    <div className="insight-item">
                                        <div className="insight-number">3</div>
                                        <div className="insight-content">
                                            <h4>Driver Efficiency Alert</h4>
                                            <p>3 drivers performing below baseline - recommend training</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="revenue-chart">
                                <h3>Revenue Trend (Last 7 Days)</h3>
                                <table className="simple-chart">
                                    <thead>
                                        <tr>
                                            <th>Day</th>
                                            <th>Revenue</th>
                                            <th>Chart</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {revenueTrendData.map((item) => (
                                            <tr key={item.day}>
                                                <td>{item.day}</td>
                                                <td>${item.revenue.toLocaleString()}</td>
                                                <td>
                                                    <div className="bar-chart">
                                                        <div
                                                            className="bar"
                                                            style={{ width: `${(item.revenue / 7000) * 100}%` }}
                                                        ></div>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Customer Analytics Tab */}
                    {activeTab === 'customers' && (
                        <div className="ml-dashboard-content">
                            <div className="chart-card">
                                <h3>Top 10 Customers by ML Score</h3>
                                <div className="customers-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Rank</th>
                                                <th>Customer Name</th>
                                                <th>ML Score</th>
                                                <th>Total Orders</th>
                                                <th>Revenue</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {customersData?.customers?.map((customer, idx) => (
                                                <tr key={customer.id}>
                                                    <td>#{idx + 1}</td>
                                                    <td>{customer.name || `Customer ${customer.id}`}</td>
                                                    <td>
                                                        <span className="score-badge">{customer.score?.toFixed(0) || 0}</span>
                                                    </td>
                                                    <td>{customer.orders || 0}</td>
                                                    <td>${(customer.revenue || 0).toLocaleString()}</td>
                                                    <td>
                                                        <span className="status-badge status-active">Active</span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <div className="actions-section">
                                <h3>Recommended Actions</h3>
                                <div className="actions-grid">
                                    <div className="action-card">
                                        <h4>VIP Program</h4>
                                        <p>Offer exclusive benefits to top 10 customers</p>
                                        <button className="action-button">Implement</button>
                                    </div>
                                    <div className="action-card">
                                        <h4>Loyalty Rewards</h4>
                                        <p>5% discount on next 10 shipments for high-value customers</p>
                                        <button className="action-button">Send Campaign</button>
                                    </div>
                                    <div className="action-card">
                                        <h4>Churn Prevention</h4>
                                        <p>Personalized offers for at-risk customers</p>
                                        <button className="action-button">Activate</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Driver Performance Tab */}
                    {activeTab === 'drivers' && (
                        <div className="ml-dashboard-content">
                            <div className="drivers-performance">
                                <h3>Top Performing Drivers</h3>
                                <table className="drivers-table">
                                    <thead>
                                        <tr>
                                            <th>Driver</th>
                                            <th>On-Time Rate</th>
                                            <th>Rating</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {driverPerformanceData.map((driver) => (
                                            <tr key={driver.name}>
                                                <td>{driver.name}</td>
                                                <td>{driver.onTimeRate}%</td>
                                                <td>{driver.rating}%</td>
                                                <td>
                                                    <span className="status-badge status-active">Active</span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            <div className="drivers-stats">
                                <h3>Driver Statistics</h3>
                                <div className="stats-grid">
                                    {driversData?.top_performers?.length > 0 ? (
                                        driversData.top_performers.map(driver => (
                                            <div key={driver.driver_id} className="stat-card">
                                                <div className="stat-header">
                                                    <h4>{driver.name || 'Driver'}</h4>
                                                    <span className="rank">#{driver.rank || '?'}</span>
                                                </div>
                                                <div className="stat-content">
                                                    <div className="stat-item">
                                                        <span>On-Time Rate</span>
                                                        <div className="progress-bar">
                                                            <div
                                                                className="progress-fill"
                                                                style={{ width: `${(driver.on_time_rate || 0) * 100}%` }}
                                                            />
                                                        </div>
                                                        <span className="percentage">{((driver.on_time_rate || 0) * 100).toFixed(1)}%</span>
                                                    </div>
                                                    <div className="stat-item">
                                                        <span>Rating</span>
                                                        <span className="rating">{(driver.rating || 0).toFixed(1)}/5.0</span>
                                                    </div>
                                                    <div className="stat-item">
                                                        <span>Monthly Revenue</span>
                                                        <span className="revenue">${(driver.revenue || 0).toLocaleString()}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '2rem' }}>
                                            No driver data available
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Forecast Tab */}
                    {activeTab === 'forecast' && (
                        <div className="ml-dashboard-content">
                            <div className="chart-card">
                                <h3>30-Day Demand Forecast</h3>
                                <p className="forecast-description">
                                    AI-powered prediction of shipment volume for the next 30 days
                                </p>
                                <div className="forecast-info">
                                    <div className="forecast-stat">
                                        <span className="label">Expected Peak</span>
                                        <span className="value">Week 3</span>
                                    </div>
                                    <div className="forecast-stat">
                                        <span className="label">Avg Daily Volume</span>
                                        <span className="value">2,450 shipments</span>
                                    </div>
                                    <div className="forecast-stat">
                                        <span className="label">Confidence Level</span>
                                        <span className="value">94%</span>
                                    </div>
                                </div>
                            </div>

                            <div className="recommendations-section">
                                <h3>Staffing Recommendations</h3>
                                <div className="recommendations-list">
                                    <div className="recommendation-item high">
                                        <div className="recommendation-level">HIGH</div>
                                        <div className="recommendation-content">
                                            <h4>Increase fleet capacity by 25%</h4>
                                            <p>Expected high demand in week 3. Recommend hiring 8-10 temporary drivers.</p>
                                        </div>
                                    </div>
                                    <div className="recommendation-item medium">
                                        <div className="recommendation-level">MEDIUM</div>
                                        <div className="recommendation-content">
                                            <h4>Expand warehouse hours</h4>
                                            <p>Consider 24-hour operations during peak weeks to improve throughput.</p>
                                        </div>
                                    </div>
                                    <div className="recommendation-item low">
                                        <div className="recommendation-level">LOW</div>
                                        <div className="recommendation-content">
                                            <h4>Stock additional equipment</h4>
                                            <p>Prepare extra packaging materials and scanning devices (10-15% buffer).</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Export Button */}
                    <div className="export-section">
                        <button className="export-button">
                            <Download size={18} />
                            Export Report
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};

export default MLDashboard;
