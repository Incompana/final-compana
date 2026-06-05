import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App.jsx";
import { AssessmentProvider } from "./context/AssessmentContext";
import "./styles/global.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <GoogleOAuthProvider clientId="54398198808-h34m3qhjuh83sfhdt0u8jo4ikaktj59p.apps.googleusercontent.com">
      <AssessmentProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AssessmentProvider>
    </GoogleOAuthProvider>
  </StrictMode>
);