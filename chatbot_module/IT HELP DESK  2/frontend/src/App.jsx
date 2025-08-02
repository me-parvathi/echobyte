import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import LoginRegister from "./LoginRegister";
import Chatbot from "./Chatbot";

function ProtectedRoute({ children }) {
  const authToken = localStorage.getItem("token");
  return authToken ? children : <Navigate to="/" />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LoginRegister />} />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <Chatbot />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}
