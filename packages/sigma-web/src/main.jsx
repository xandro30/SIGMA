import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import Providers from "./app/Providers";
import App from "./app/App";
import "./index.css";
createRoot(document.getElementById("root")).render(
  <StrictMode><Providers><App /></Providers></StrictMode>
);
