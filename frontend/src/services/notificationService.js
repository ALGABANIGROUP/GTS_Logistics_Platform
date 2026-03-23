// frontend/src/services/notificationService.js

import axiosClient from '../api/axiosClient';

class NotificationService {
    // Email notifications
    async sendEmail(to, subject, body, options = {}) {
        try {
            const response = await axiosClient.post('/api/v1/notifications/email', {
                to,
                subject,
                body,
                ...options
            });
            return response.data;
        } catch (error) {
            console.error('Failed to send email:', error);
            throw error;
        }
    }

    // SMS notifications
    async sendSMS(to, message, options = {}) {
        try {
            const response = await axiosClient.post('/api/v1/notifications/sms', {
                to,
                message,
                ...options
            });
            return response.data;
        } catch (error) {
            console.error('Failed to send SMS:', error);
            throw error;
        }
    }

    // Push notifications
    async sendPushNotification(userId, title, body, options = {}) {
        try {
            const response = await axiosClient.post('/api/v1/notifications/push', {
                userId,
                title,
                body,
                ...options
            });
            return response.data;
        } catch (error) {
            console.error('Failed to send push notification:', error);
            throw error;
        }
    }

    // Register for push notifications
    async registerPushNotifications(subscription) {
        try {
            const response = await axiosClient.post('/api/v1/notifications/push/register', {
                subscription
            });
            return response.data;
        } catch (error) {
            console.error('Failed to register push notifications:', error);
            throw error;
        }
    }

    // Test notification settings
    async testNotification(type, contact) {
        try {
            const response = await axiosClient.post('/api/v1/notifications/test', {
                type,
                contact
            });
            return response.data;
        } catch (error) {
            console.error('Failed to test notification:', error);
            throw error;
        }
    }

    // Browser push notification setup
    async setupPushNotifications() {
        if (!('serviceWorker' in navigator) || !('PushManager' in navigator)) {
            console.warn('Push notifications not supported');
            return null;
        }

        try {
            // Register service worker
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('Service Worker registered:', registration);

            // Wait for the service worker to be ready
            await navigator.serviceWorker.ready;

            // Check permission
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                throw new Error('Notification permission denied');
            }

            // Subscribe to push notifications
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(globalThis.process?.env?.REACT_APP_VAPID_PUBLIC_KEY || 'BDefaultVAPIDKeyForDevelopment1234567890123456789012345678901234567890')
            });

            console.log('Push subscription:', subscription);

            // Register with backend
            await this.registerPushNotifications(subscription);

            return subscription;
        } catch (error) {
            console.error('Failed to setup push notifications:', error);
            throw error;
        }
    }

    // Helper function to convert VAPID key
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
}

export default new NotificationService();