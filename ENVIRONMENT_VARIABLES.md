# Environment Variables Configuration

This document describes all the environment variables that can be configured for the backend.

## OpenAI Model Configuration

### OPENAI_CHAT_MODEL
- **Default**: `gpt-4o-mini`
- **Description**: The OpenAI model to use for chat completions (text generation, analysis, etc.)
- **Examples**: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`

### OPENAI_EMBED_MODEL
- **Default**: `text-embedding-3-small`
- **Description**: The OpenAI model to use for text embeddings
- **Examples**: `text-embedding-3-small`, `text-embedding-3-large`

### OPENAI_WHISPER_MODEL
- **Default**: `whisper-1`
- **Description**: The OpenAI model to use for audio transcription
- **Examples**: `whisper-1`

## API Keys

### OPENAI_API_KEY
- **Required**: Yes
- **Description**: Your OpenAI API key for accessing OpenAI services
- **Format**: `sk-...`

### SUPABASE_URL
- **Required**: Yes
- **Description**: Your Supabase project URL
- **Format**: `https://gfzmmnyhywerfjpnuvdj.supabase.co`

### SUPABASE_KEY
- **Required**: Yes
- **Description**: Your Supabase service role key
- **Format**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdmem1tbnloeXdlcmZqcG51dmRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NDg2OTksImV4cCI6MjA2NzEyNDY5OX0.70brbyoXBQMyth-7wKrnBW41waN7sC4GQg5D9XRT_6U`

## Backend-Core Microservice Configuration

### BACKEND_CORE_URL
- **Default**: `http://localhost:5001`
- **Description**: URL of the backend-core microservice
- **Examples**: `http://localhost:5001`, `http://backend-core:5001`

## Flask Configuration

### FLASK_ENV
- **Default**: `development`
- **Description**: Flask environment mode
- **Values**: `development`, `production`

### FLASK_DEBUG
- **Default**: `True`
- **Description**: Enable Flask debug mode
- **Values**: `True`, `False`

## Example .env File

Create a `.env` file in the backend directory with the following content:

```env
# OpenAI Model Configuration
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_WHISPER_MODEL=whisper-1

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Backend-Core Microservice Configuration
BACKEND_CORE_URL=http://localhost:5001

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

## Usage

The environment variables are automatically loaded by the `config.py` file using `python-dotenv`. You can access them in your code by importing from the config module:

```python
from .config import OPENAI_CHAT_MODEL, OPENAI_EMBED_MODEL, OPENAI_WHISPER_MODEL
```

## Benefits

- **Flexibility**: Easily switch between different OpenAI models without code changes
- **Environment-specific**: Use different models for development, staging, and production
- **Cost optimization**: Use cheaper models for development and testing
- **Future-proof**: Easy to upgrade to newer models when they become available 