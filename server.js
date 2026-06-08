require('dotenv').config();
const app = require('./index.js');

const HOST = process.env.HOST || '0.0.0.0';
const PORT = Number(process.env.PORT) || 3000;

app.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}`);
});
