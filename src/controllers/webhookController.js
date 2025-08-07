const { verifyHmac } = require('../utils/hmac');

const SECRET  = process.env.WEBHOOK_SECRET;
const PASSPH  = process.env.WEBHOOK_PASSPHRASE;
const NO_AUTH = process.env.TEST_NO_AUTH === 'true';

async function handleWebhook(req, res) {
  const payload    = JSON.stringify(req.body);
  const signature  = req.headers['x-signature'] || '';

  // Vérif signature si NON en mode test
  if (!NO_AUTH) {
    if (!verifyHmac(payload, signature, SECRET)) {
      return res.status(401).json({ success: false, message: 'Signature invalide' });
    }
  }

  // Vérif passphrase
  if (req.body.passphrase !== PASSPH) {
    return res.status(401).json({ success: false, message: 'Passphrase invalide' });
  }

  // Ici, insérez votre logique grid / entry / exit
  // Par ex. : await gridManager.execute(req.body);

  console.log('✅ Payload validé :', req.body);
  return res.json({ success: true, message: 'Webhook exécuté' });
}

function handleWebhookTest(req, res) {
  if (req.body.passphrase !== PASSPH) {
    return res.status(401).json({ success: false, message: 'Passphrase invalide' });
  }
  console.log('🧪 Test webhook reçu :', req.body.action || 'ping');
  return res.json({ success: true, message: `Test ${req.body.action || 'pong'} OK` });
}

module.exports = { handleWebhook, handleWebhookTest };
