const fastify = require('fastify')();

fastify.get('/', async () => ({
  message: 'hello',
  framework: 'fastify',
}));

fastify.listen({ host: '0.0.0.0', port: 8000 });
