const express = require('express');
const webhookController = require('./controllers/webhookController');

const app = express();
app.use(express.json({ strict: true }));

// Endpoint principal avec signature HMAC
app.post('/webhook', webhookController.handleWebhook);

// Endpoint de test (passphrase-only)
app.post('/webhook-test', webhookController.handleWebhookTest);

module.exports = app;
