
import axios from "axios";

// Render FastAPI backend URL.
// Example:
// VITE_API_URL=https://aivoa-1.onrender.com
const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
  console.warn(
    "VITE_API_URL is not configured. Please add it to your Vercel environment variables."
  );
}

// Remove trailing slash to avoid URLs like:
// https://backend.com//api/copilot/parse
const BASE_URL = API_URL
  ? API_URL.replace(/\/+$/, "")
  : "";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    Accept: "application/json",
  },
  timeout: 120000,
});


// =====================================================
// Health Check
// =====================================================

export const checkHealth = async () => {
  const response = await api.get("/api/health");
  return response.data;
};


// =====================================================
// AIVOA Copilot - Parse Complaint
// =====================================================

export const parseComplaint = async (text = "", file = null) => {
  const formData = new FormData();

  if (text && text.trim()) {
    formData.append("text", text.trim());
  }

  if (file) {
    formData.append("file", file);
  }

  if (!text?.trim() && !file) {
    throw new Error("Please enter complaint text or upload a file.");
  }

  const response = await api.post(
    "/api/copilot/parse",
    formData
  );

  return response.data;
};


// =====================================================
// AIVOA Copilot - Chat Correction
// =====================================================

export const correctComplaint = async (
  message,
  currentFields
) => {
  if (!message || !message.trim()) {
    throw new Error("Correction message cannot be empty.");
  }

  const response = await api.post(
    "/api/copilot/chat",
    {
      message: message.trim(),
      current_fields: currentFields || {},
    }
  );

  return response.data;
};


// =====================================================
// Complaints - Commit Complaint
// =====================================================

export const commitComplaint = async (complaintData) => {
  const response = await api.post(
    "/api/complaints",
    complaintData
  );

  return response.data;
};


// =====================================================
// Complaints - Get All Complaints
// =====================================================

export const getComplaints = async () => {
  const response = await api.get(
    "/api/complaints"
  );

  return response.data;
};


// =====================================================
// Complaints - Get Single Complaint
// =====================================================

export const getComplaint = async (complaintId) => {
  if (!complaintId) {
    throw new Error("Complaint ID is required.");
  }

  const response = await api.get(
    `/api/complaints/${complaintId}`
  );

  return response.data;
};


// =====================================================
// Axios Error Helper
// =====================================================

export const getApiErrorMessage = (error) => {
  if (error.response) {
    return (
      error.response.data?.detail ||
      error.response.data?.message ||
      `Request failed with status code ${error.response.status}`
    );
  }

  if (error.request) {
    return "Unable to connect to the AIVOA backend. Please check the backend URL and CORS configuration.";
  }

  return error.message || "An unexpected error occurred.";
};


export default api;
