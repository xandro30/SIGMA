import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
const qc = new QueryClient({ defaultOptions:{ queries:{ staleTime:1000*60*5, retry:1, refetchOnWindowFocus:false }, mutations:{ retry:0 } } });
if (import.meta.env.DEV) window.__QC__ = qc;
export default function Providers({ children }) {
  return <BrowserRouter><QueryClientProvider client={qc}>{children}</QueryClientProvider></BrowserRouter>;
}
