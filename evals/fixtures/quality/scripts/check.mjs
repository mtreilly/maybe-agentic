import { readdirSync, readFileSync } from 'node:fs';
for (const file of readdirSync('packages/api')) {
  if (file.endsWith('.json')) JSON.parse(readFileSync(`packages/api/${file}`, 'utf8'));
}
console.log('API JSON checked');
