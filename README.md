# Elmorshedy Cars - Dealership Management Platform

An integrated system for managing car dealership operations, combining an AI-driven Telegram sales agent with a management dashboard.

## Overview

This project is built to automate customer interactions and provide data-driven insights for car sales. It uses a FastAPI backend, a Streamlit dashboard for analytics, and a Telegram bot powered by Google's Gemini LLM.

## Key Features

- Sales Agent: A Telegram bot that handles customer inquiries about car specs, availability, and pricing.
- Management Dashboard: Real-time tracking of customer interests, booking statistics, and inventory status.
- Booking System: Automated management for test drives and viewing appointments.
- AI Reporting: Automated analysis of monthly data to generate performance reports.

## Core Logic: The Agent Graph

The intelligence of the sales agent is organized using a Graph/Node architecture. Unlike traditional complex decision trees, this system uses a Linear Pipeline approach to process messages.

### How it works:
1. State Initialization: Every message starts with a State object containing the user input, history, and metadata.
2. Node Execution: The message passes through a sequence of nodes (defined in `graph/builder.py`).
   - Normalization: Cleans up the input (e.g., handling Arabic slang).
   - Intent Recognition: Uses AI to determine what the user wants (buy, book, ask).
   - Data Lookup: Queries the database for car details or available slots.
   - Logic Checks: Verifies working hours, bot status, etc.
3. Early Stopping: Any node can decide to stop the pipeline (setting `should_stop`) if it has enough info to respond or if an error occurs.
4. Response Generation: The final node compiles the information gathered by previous nodes into a natural response.

## Technical Stack

- Backend: FastAPI
- Analytics: Streamlit, Pandas, Plotly
- AI: Google Gemini (generative-ai)
- Database: PostgreSQL (SQLAlchemy)
- Bot Engine: python-telegram-bot
- Infrastructure: Docker & Docker Compose

## Project Structure

- agents/: Telegram bot event handlers and interaction logic.
- app/: API endpoints, database models, and core application logic.
- dashboard/: Streamlit views for management and analytics.
- graph/: The heart of the bot logic, containing the pipeline builder and individual processing nodes.
- services/: Shared business logic for AI, caching, and analytics.

## Setup and Installation

1. Environment Configuration:
   Create a .env file with the following:
   - DATABASE_URL
   - TELEGRAM_BOT_TOKEN
   - GOOGLE_API_KEY

2. Deployment:
   The easiest way to run the full stack is via Docker:
   ```bash
   docker-compose up --build
   ```

3. Access:
   - API Documentation: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

## Testing

Run tests using:
```bash
pytest
```

---
Proprietary software for Elmorshedy Cars.
