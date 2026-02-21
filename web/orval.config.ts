import { defineConfig } from 'orval'

export default defineConfig({
  api: {
    input: {
      target: './openapi.yaml',
    },
    output: {
      target: './src/api/endpoints',
      schemas: './src/api/model',
      client: 'axios',
      mode: 'split',
      prettier: true,
    },
  },
})
