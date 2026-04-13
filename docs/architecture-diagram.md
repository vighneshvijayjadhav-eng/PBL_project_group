# Architecture Diagram

```text
React (Vite)
  |
  | Axios + JWT Access Token
  v
FastAPI Application
  |
  |-- Auth Router
  |     |-- Login
  |     |-- Refresh
  |     |-- Logout
  |
  |-- Claims Router
  |     |-- User Claims
  |     |-- Claim Summary
  |     |-- Admin Claims
  |
  |-- System Router
        |-- Health Check
  |
  v
Service Layer
  |
  |-- Claim Service
  |-- System Service
  |-- Risk Client
  |-- Audit Logger
  |-- Refresh Token Store
  |-- Token Blacklist
  |
  v
SQLAlchemy ORM
  |
  v
Database
  |
  v
Risk Engine
  |
  |-- Rule Engine
  |-- ML Model
  |-- Scorer
  |-- Artifacts (model, scaler, encoders, feature order)
```
