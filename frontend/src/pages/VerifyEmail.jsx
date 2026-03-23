import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';

export default function VerifyEmail() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('verifying');
    const [message, setMessage] = useState('Verifying your email...');
    const [error, setError] = useState(null);

    useEffect(() => {
        const verifyToken = async () => {
            const token = searchParams.get('token');

            if (!token) {
                setStatus('error');
                setMessage('No verification token provided.');
                setError('Missing token');
                return;
            }

            try {
                const response = await axiosClient.get(`/portal/verify-email?token=${token}`);

                setStatus('success');
                setMessage(response.data.message || 'Your email has been verified successfully!');

                // Redirect to login after 3 seconds
                setTimeout(() => {
                    navigate('/login');
                }, 3000);
            } catch (err) {
                setStatus('error');
                setMessage(err.response?.data?.detail || 'Email verification failed. Please try again.');
                setError(err.message);
            }
        };

        verifyToken();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-4">
            <div className="w-full max-w-md">
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <div className="text-center">
                        {status === 'verifying' && (
                            <>
                                <div className="mb-4 flex justify-center">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900 mb-2">Verifying Email</h1>
                            </>
                        )}

                        {status === 'success' && (
                            <>
                                <div className="mb-4 flex justify-center">
                                    <div className="flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                                        <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900 mb-2">Email Verified</h1>
                            </>
                        )}

                        {status === 'error' && (
                            <>
                                <div className="mb-4 flex justify-center">
                                    <div className="flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                                        <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </div>
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h1>
                            </>
                        )}

                        <p className={`text-lg mb-6 ${status === 'success' ? 'text-green-600' :
                                status === 'error' ? 'text-red-600' :
                                    'text-gray-600'
                            }`}>
                            {message}
                        </p>

                        {error && (
                            <p className="text-sm text-gray-500 mb-4">Error: {error}</p>
                        )}

                        <div className="space-y-3">
                            {status === 'success' && (
                                <p className="text-sm text-gray-600">
                                    Redirecting to login in a few seconds...
                                </p>
                            )}

                            <button
                                onClick={() => navigate('/login')}
                                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                            >
                                Go to Login
                            </button>

                            <button
                                onClick={() => navigate('/')}
                                className="w-full px-4 py-2 bg-gray-100 text-gray-900 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                            >
                                Back to Home
                            </button>
                        </div>
                    </div>
                </div>

                <p className="text-center text-sm text-gray-600 mt-6">
                    Problems verifying your email?{' '}
                    <a href="/support" className="text-blue-600 hover:underline">
                        Contact support
                    </a>
                </p>
            </div>
        </div>
    );
}
