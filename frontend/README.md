# Frontend

React + TypeScript + Vite frontend for LegalLens.

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Opens on `http://localhost:5173` with proxy to backend API at `http://localhost:8000`.

### Build

```bash
npm run build
```

## Pages

- **Upload**: Drag-drop PDF upload
- **Dashboard**: View extracted clauses, risk flags, ask questions, compare documents

## API Integration

All API calls are in `src/services/api.ts`. Update `baseURL` if backend runs on different port.
