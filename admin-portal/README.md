# Aura Audit AI - Admin Portal

Admin portal for managing customer support tickets, issues, and integration with JIRA.

## Features

- **Ticket Management**: View and manage support tickets from JIRA
- **AI-Powered Analysis**: Analyze bugs with Claude Code
- **Auto-Fix**: Automatically fix bugs and create pull requests
- **Customer Support**: Track and respond to customer issues

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

The admin portal requires the following environment variables:

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_JIRA_URL`: JIRA instance URL

See `.env.example` for more details.
