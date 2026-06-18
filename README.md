# MedSafe

MedSafe is a FastAPI-based medicine safety app that checks drug interactions and side effects, and includes Firebase-backed authentication and history/profile features.

Live website: https://med-safe-tau.vercel.app/

## What's Included

- Drug interaction and side-effect checking
- Firebase authentication
- User history and profile pages
- FastAPI backend with static frontend pages

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd project
```

### 2. Create a Python environment

You can use either Conda or a virtual environment.

#### Conda

```bash
conda env create -f environment.yml
conda activate medsafe
```

#### Virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file from `.env.example` and fill in the required values.

### 4. Run the app locally

```bash
uvicorn main:app --reload
```

Open the app in your browser at:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/login
- http://127.0.0.1:8000/profile

## Environment Variables

The backend expects the following values:

- `APP_NAME`
- `APP_DESCRIPTION`
- `APP_VERSION`
- `ANTHROPIC_API_KEY`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`

## Notes

- The Firebase private key should be stored with escaped newlines in the `.env` file.
- The production deployment is handled on Vercel.
