/* eslint-env node */
/* eslint-disable @typescript-eslint/no-require-imports */

// check-backend.js - Check if auth endpoints exist
const express = require('express');
const app = express();

// Attempt to load auth routes
try {
    const authRoutes = require('./routes/auth');
    console.log('✅ Auth routes loaded successfully');

    // Print detected endpoints
    console.log('📋 Available auth endpoints:');
    authRoutes.stack.forEach(layer => {
        if (layer.route) {
            const methods = Object.keys(layer.route.methods).map(method => method.toUpperCase());
            console.log(`   ${methods.join(',')} ${layer.route.path}`);
        }
    });
} catch (err) {
    console.log('❌ Auth routes not found or error:', err.message);
    console.log('💡 Creating basic auth routes...');

    // Fallback example code
    const basicAuthCode = `
    const express = require('express');
    const bcrypt = require('bcryptjs');
    const jwt = require('jsonwebtoken');
    const { Pool } = require('pg');
    
    const router = express.Router();
    const pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: { rejectUnauthorized: false }
    });
    
    router.post('/login', async (req, res) => {
        try {
            const { email, password } = req.body;
            // ... implement auth logic
        } catch (err) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });
    
    module.exports = router;
    `;
    console.log('📝 Basic auth code ready to implement');
}