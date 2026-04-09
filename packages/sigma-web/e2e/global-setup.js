import { ensureBackendReady, clearFirestore } from './helpers/seed.js';

export default async function globalSetup() {
  await ensureBackendReady();
  await clearFirestore();
}
