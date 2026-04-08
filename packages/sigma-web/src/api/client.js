const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
async function req(path, opts={}) {
  const res = await fetch(`${BASE}/v1${path}`, {
    headers: { "Content-Type":"application/json", ...opts.headers }, ...opts,
  });
  if (!res.ok) { const e = await res.json().catch(()=>({message:"Error"})); throw new Error(e.message??`HTTP ${res.status}`); }
  if (res.status===204) return null;
  return res.json();
}
export const api = {
  get:    (p)    => req(p),
  post:   (p,b)  => req(p, { method:"POST",   body:JSON.stringify(b) }),
  patch:  (p,b)  => req(p, { method:"PATCH",  body:JSON.stringify(b) }),
  delete: (p)    => req(p, { method:"DELETE" }),
};
