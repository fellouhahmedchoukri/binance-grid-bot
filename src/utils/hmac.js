const crypto = require('crypto');

function verifyHmac(payload, signature, secret) {
  if (!secret) return false;
  const hash = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  return hash === signature;
}

module.exports = { verifyHmac };
