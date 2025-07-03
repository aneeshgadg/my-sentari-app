# Sentari Backend API Documentation

## Overview

This is a modular Flask backend API for the Sentari application. The API has been refactored from the original Next.js API routes into separate Python modules for better maintainability and scalability.

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── src/                   # Modular API endpoints
│   ├── __init__.py
│   ├── auth.py           # Authentication middleware
│   ├── analyze.py        # Tag analysis endpoint
│   ├── save_entry.py     # Save voice entries
│   ├── emotion_trend.py  # Emotion trend analysis
│   ├── pick_emoji.py     # Emoji generation
│   ├── pick_emoji_batch.py # Batch emoji generation
│   ├── run_pipeline.py   # Core pipeline execution
│   ├── empathy.py        # Empathy processing
│   ├── update_tags.py    # Update user tags
│   ├── update_transcript.py # Update user transcripts
│   ├── test_openai.py    # OpenAI connection test
│   └── test_tags.py      # Tag classification test
└── README_API.md         # This file
```

## API Endpoints

### Authentication Required Endpoints

All endpoints except `/api/run`, `/api/empathy`, `/api/test-openai`, `/api/test-tags`, and `/api/whisper` require authentication.

**Authentication Header:**
```
Authorization: Bearer <supabase_token>
```

### Endpoints

#### 1. POST `/api/analyze`
Analyze transcripts for tags and categories.

**Request Body:**
```json
{
  "transcript": "string",
  "entryId": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "purpose": "string",
    "tone": "string",
    "category": "string",
    "confidence": 0.85
  },
  "selectedTags": ["string"],
  "timestamp": "ISO string"
}
```

#### 2. POST `/api/save-entry`
Save voice entries to the database.

**Request Body:**
```json
{
  "transcript_raw": "string",
  "transcript_user": "string",
  "language_detected": "string",
  "language_rendered": "string",
  "tags_model": ["string"],
  "tags_user": ["string"],
  "category": "string",
  "audio_duration": 0,
  "client_timestamp": "ISO string (optional)"
}
```

#### 3. POST `/api/emotion-trend`
Get emotion trends for the last 7 days.

**Response:**
```json
{
  "trend": [
    {
      "timestamp": "ISO string",
      "score": 0.75
    }
  ]
}
```

#### 4. POST `/api/pick-emoji`
Generate emoji for an entry.

**Request Body:**
```json
{
  "transcript": "string (optional)",
  "entryId": "string"
}
```

#### 5. POST `/api/pick-emoji-batch`
Generate emojis for multiple entries.

**Request Body:**
```json
{
  "limit": 15
}
```

#### 6. POST `/api/run`
Run the core pipeline (no auth required).

**Request Body:**
```json
{
  "text": "string",
  "userId": "string"
}
```

#### 7. POST `/api/empathy`
Process transcript for empathy analysis (no auth required).

**Request Body:**
```json
{
  "transcript": "string",
  "userId": "string"
}
```

#### 8. POST `/api/update-tags`
Update user tags for an entry.

**Request Body:**
```json
{
  "entryId": "string",
  "tags_user": ["string"]
}
```

#### 9. POST `/api/update-transcript`
Update user transcript for an entry.

**Request Body:**
```json
{
  "entryId": "string",
  "transcript_user": "string"
}
```

#### 10. POST `/api/whisper`
Transcribe audio files (no auth required).

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` field with audio file

#### 11. GET `/api/test-openai`
Test OpenAI connection (no auth required).

#### 12. GET/POST `/api/test-tags`
Test tag classification (no auth required).

## Environment Variables

Required environment variables:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
```

## Running the Backend

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables in `.env` file

3. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Frontend Integration

The frontend has been updated to use the new Flask backend. Update your frontend configuration to point to the Flask backend URL:

```typescript
// In your frontend config
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": "Additional details (optional)",
  "status": 400
}
```

## Authentication

The backend uses Supabase authentication. Users must provide a valid Supabase token in the Authorization header for protected endpoints.

## Database Schema

The backend expects a Supabase database with a `voice_entries` table containing the following columns:
- id (UUID, primary key)
- user_id (UUID, foreign key to auth.users)
- transcript_raw (text)
- transcript_user (text)
- language_detected (text)
- language_rendered (text)
- tags_model (jsonb)
- tags_user (jsonb)
- category (text)
- audio_duration (integer)
- created_at (timestamp)
- updated_at (timestamp)
- emotion_score_score (float)
- emotion_score_log (text)
- entry_emoji (text)
- emoji_source (text)
- tags_log (jsonb) 