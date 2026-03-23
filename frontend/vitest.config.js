import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: ['./src/test/setup.js'],
        include: ['src/**/*.{test,spec}.{js,jsx}'],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'lcov'],
            include: [
                'src/api/paymentApi.js',
                'src/routes/RequireAuth.jsx',
                'src/hooks/useTruckWS.js',
                'src/services/metaDataApi.js',
                'src/services/metaDataService.js',
                'src/utils/tierUtils.js',
            ],
            thresholds: {
                lines: 90,
                functions: 90,
                branches: 90,
                statements: 90,
            },
        },
    },
});
