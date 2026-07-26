# ChapterGuard

ChapterGuard is a simple reading companion app that helps users track a book, their current chapter, and ask questions while reading.

## Project structure

- frontend/: React + Vite frontend application
- root files: project documentation and shared Git ignore rules

## Frontend setup

The frontend is a Vite React app.

### Install dependencies

```bash
cd frontend
npm install
```

### Start the development server

```bash
cd frontend
npm run dev
```

### Build for production

```bash
cd frontend
npm run build
```

## Development notes

- The frontend includes a form for entering the book title, chapter, and reading question.
- The app displays reading status and an answer card after submission.
- ESLint is configured in the frontend project.
