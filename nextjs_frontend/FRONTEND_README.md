# Documentation Maintainer Frontend

A React frontend built with Next.js 14+ for reviewing and managing documentation updates. This application provides a clean, modern interface for reviewing suggested changes to documentation.

## Features

- **Natural Language Query**: Type queries in plain English to find relevant documents
- **Side-by-Side Diff View**: Compare original and suggested content with visual diff highlighting and markdown rendering
- **Scrollable Content**: Both horizontal and vertical scrolling for long content
- **Change Type Indicators**: Color-coded badges showing modification type (modified, removed, unchanged)
- **Action Buttons**: Approve, reject, or edit suggestions (edit functionality placeholder)
- **Responsive Design**: Works well on desktop with clean, modern UI using Tailwind CSS

## Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd nextjs_frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

1. **Enter a Query**: Type your question or request in the input field at the top of the page
2. **Submit**: Click the "Search" button or press Enter
3. **Review Results**: The application will display relevant documents with suggested changes
4. **Take Action**: For each document, you can:
   - **Approve**: Accept the suggested changes
   - **Reject**: Decline the suggested changes  
   - **Edit**: Modify the suggestions (placeholder functionality)

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- **Endpoint**: `POST /retrieve_relevant_documents`
- **Request Body**: `{ "query": "user input" }`
- **Response**: Array of `DocumentUpdate` objects

## Project Structure

```
nextjs_frontend/
├── app/
│   ├── globals.css          # Global styles with Tailwind CSS
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page component
├── components/
│   └── DocumentCard.tsx     # Individual document display component
├── types/
│   └── index.ts             # TypeScript type definitions
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── FRONTEND_README.md               # This file
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Technologies Used

- **Next.js 14+** - React framework with app directory
- **TypeScript** - Type safety and better developer experience
- **Tailwind CSS** - Utility-first CSS framework for styling
- **React Diff Viewer** - Side-by-side diff visualization
- **React Markdown** - Markdown rendering for documentation content
- **Tailwind Typography** - Enhanced typography for markdown content
- **React 18** - Latest React features and hooks

## Development Notes

- The application uses the `app` directory structure (Next.js 14+)
- All components are client-side rendered for interactivity
- Error handling includes network issues and API errors
- Loading states provide user feedback during API calls
- The design is responsive and optimized for desktop use


## Troubleshooting

1. **Port conflicts**: If port 3000 is in use, Next.js will automatically use the next available port
2. **API connection errors**: Ensure your FastAPI backend is running on `http://localhost:8000`
3. **TypeScript errors**: Run `npm install` to ensure all type definitions are installed
4. **Build errors**: Clear `.next` directory and run `npm run build` again 