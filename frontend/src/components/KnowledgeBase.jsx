/**
 * Knowledge Base Frontend Components
 * Frontend knowledge base components
 */

import React, { useState, useEffect } from 'react';
import axiosClient from '../api/axiosClient';

// ============================================
// KNOWLEDGE BASE LIST - Articles list
// ============================================

export function KnowledgeBaseList() {
    const [articles, setArticles] = useState([]);
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('all');
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchArticles();
    }, [search, category]);

    const fetchArticles = async () => {
        try {
            setLoading(true);
            const params = {};
            if (search) params.search = search;
            if (category !== 'all') params.category = category;

            const response = await axiosClient.get('/api/v1/support/knowledge-base', { params });
            setArticles(response.data);
        } catch (error) {
            console.error('Error fetching articles:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">Knowledge Base</h1>
                    <p className="text-gray-600">Find answers to common questions</p>
                </div>

                {/* Search Bar */}
                <div className="mb-8">
                    <div className="relative">
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Search articles..."
                            className="w-full px-6 py-4 rounded-lg shadow-md border-2 border-transparent focus:outline-none focus:border-blue-500"
                        />
                        <span className="absolute right-4 top-4 text-2xl">🔍</span>
                    </div>
                </div>

                {/* Category Filter */}
                <div className="flex gap-2 mb-8 flex-wrap justify-center">
                    {['all', 'technical', 'billing', 'account', 'general'].map(cat => (
                        <button
                            key={cat}
                            onClick={() => setCategory(cat)}
                            className={`px-4 py-2 rounded-full font-medium transition ${category === cat
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-100'
                                }`}
                        >
                            {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Articles Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {articles.map(article => (
                        <div
                            key={article.id}
                            onClick={() => navigate(`/support/knowledge-base/${article.id}`)}
                            className="bg-white rounded-lg shadow-md hover:shadow-lg transition cursor-pointer p-6"
                        >
                            <div className="mb-3">
                                <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                                    {article.category}
                                </span>
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2">
                                {article.title}
                            </h3>
                            <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                                {article.content.substring(0, 150)}...
                            </p>
                            <div className="flex justify-between items-center text-sm text-gray-500">
                                <span>👁️ {article.view_count} views</span>
                                <span>👍 {article.helpful_votes}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {articles.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-gray-600 text-lg">No articles found</p>
                    </div>
                )}
            </div>
        </div>
    );
}

// ============================================
// ARTICLE DETAIL - Article details
// ============================================

export function KnowledgeBaseArticle() {
    const { articleId } = useParams();
    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [helpful, setHelpful] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchArticle();
    }, [articleId]);

    const fetchArticle = async () => {
        try {
            setLoading(true);
            const response = await axiosClient.get(`/api/v1/support/knowledge-base/${articleId}`);
            setArticle(response.data);
        } catch (error) {
            console.error('Error fetching article:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleHelpful = async (isHelpful) => {
        try {
            await axiosClient.post(`/api/v1/support/knowledge-base/${articleId}/vote`, {
                is_helpful: isHelpful
            });
            setHelpful(isHelpful);
            fetchArticle();
        } catch (error) {
            console.error('Error voting:', error);
        }
    };

    if (loading) return <div className="text-center py-8">Loading...</div>;
    if (!article) return <div className="text-center py-8 text-red-600">Article not found</div>;

    return (
        <div className="max-w-4xl mx-auto py-8">
            <button
                onClick={() => navigate('/support/knowledge-base')}
                className="text-blue-600 hover:text-blue-800 mb-6 flex items-center gap-2"
            >
                ← Back to Knowledge Base
            </button>

            <div className="bg-white rounded-lg shadow-md p-8">
                {/* Header */}
                <div className="mb-6">
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium mb-4">
                        {article.category}
                    </span>
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">{article.title}</h1>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>👁️ {article.view_count} views</span>
                        <span>👍 {article.helpful_votes} helpful</span>
                        <span>📅 {new Date(article.created_at).toLocaleDateString()}</span>
                    </div>
                </div>

                {/* Content */}
                <div className="prose prose-sm max-w-none mb-8">
                    <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {article.content}
                    </p>
                </div>

                {/* Helpful Section */}
                <div className="border-t pt-6">
                    <p className="text-gray-700 mb-4 font-medium">Was this article helpful?</p>
                    <div className="flex gap-4">
                        <button
                            onClick={() => handleHelpful(true)}
                            className={`px-6 py-2 rounded-lg font-medium transition ${helpful === true
                                ? 'bg-green-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                        >
                            👍 Yes
                        </button>
                        <button
                            onClick={() => handleHelpful(false)}
                            className={`px-6 py-2 rounded-lg font-medium transition ${helpful === false
                                ? 'bg-red-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                        >
                            👎 No
                        </button>
                    </div>
                </div>

                {/* Related Articles */}
                <div className="border-t mt-8 pt-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Related Articles</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Related articles would be loaded here */}
                        <div className="p-4 border rounded-lg hover:shadow-md transition cursor-pointer">
                            <p className="font-medium text-gray-900 mb-2">Related Article 1</p>
                            <p className="text-sm text-gray-600">Related content description...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ============================================
// ADMIN - CREATE ARTICLE
// ============================================

export function CreateKnowledgeBaseArticle() {
    const [formData, setFormData] = useState({
        title: '',
        content: '',
        category: 'general',
    });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            await axiosClient.post('/api/v1/support/knowledge-base', formData);
            navigate('/support/knowledge-base');
        } catch (error) {
            console.error('Error creating article:', error);
            alert('Failed to create article');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
            <h2 className="text-3xl font-bold mb-6">Create Knowledge Base Article</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Title */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Title *
                    </label>
                    <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Article title"
                    />
                </div>

                {/* Category */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category *
                    </label>
                    <select
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="technical">Technical</option>
                        <option value="billing">Billing</option>
                        <option value="account">Account</option>
                        <option value="general">General</option>
                    </select>
                </div>

                {/* Content */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Content *
                    </label>
                    <textarea
                        name="content"
                        value={formData.content}
                        onChange={handleChange}
                        required
                        rows="12"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Write your article content here..."
                    />
                </div>

                {/* Buttons */}
                <div className="flex gap-3">
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                        {loading ? 'Publishing...' : 'Publish Article'}
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate('/support/knowledge-base')}
                        className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}

import { useNavigate, useParams } from 'react-router-dom';
