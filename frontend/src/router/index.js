import { createRouter, createWebHistory } from 'vue-router';

// Import views
import MaintenanceView from '../views/bots/MaintenanceView.vue';
// ...import other views as needed

const routes = [
    {
        path: '/ai-bots/maintenance-dashboard',
        name: 'MaintenanceDashboard',
        component: MaintenanceView,
    },
    // ...other routes
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
