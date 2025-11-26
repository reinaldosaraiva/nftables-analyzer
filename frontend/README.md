# NFTables Analyzer Frontend

Next.js 15 frontend for visualizing and querying nftables firewall rules.

## Features

- Dark theme UI with Tailwind CSS
- Interactive graph visualization with React Flow
- Upload rules via textarea or file
- Query firewall rules with source/destination IP, port, and protocol
- Real-time highlighting of matched nodes and edges
- Custom node types for networks, rules, and ports

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Requirement

The backend API must be running on `http://localhost:8000`. See the main project README for backend setup.

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page
│   └── globals.css         # Global styles
├── components/
│   ├── RuleUploader.tsx    # Upload rules interface
│   ├── RuleGraph.tsx       # React Flow visualization
│   ├── QueryForm.tsx       # Query form
│   ├── ResultPanel.tsx     # Result display
│   └── nodes/              # Custom React Flow nodes
│       ├── NetworkNode.tsx
│       ├── RuleNode.tsx
│       └── PortNode.tsx
└── lib/
    ├── api.ts              # API client
    └── types.ts            # TypeScript types
```

## Build for Production

```bash
npm run build
npm start
```
