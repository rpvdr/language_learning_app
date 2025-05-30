module.exports = {
  api: {
    input: './openapi.json',
    output: {
      mode: 'tags-split',
      target: './src/api/',
      schemas: './src/api/model',
      client: 'react-query',
      override: {
        baseUrl: 'import.meta.env.VITE_API_URL',
      },
    },
  },
}
