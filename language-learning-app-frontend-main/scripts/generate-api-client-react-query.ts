// Script to generate React Query hooks-based client using openapi-react-query
import { execSync } from 'child_process'
import { fileURLToPath } from 'url'
import path from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const OPENAPI_PATH = path.resolve(__dirname, '../openapi.json')
const OUTPUT_PATH = path.resolve(__dirname, '../src/api')

const cmd = `npx openapi-react-query --client axios --output ${OUTPUT_PATH} --schema ${OPENAPI_PATH}`

console.log('Generating React Query hooks-based client...')
execSync(cmd, { stdio: 'inherit' })
console.log('Client generated in src/api/')
