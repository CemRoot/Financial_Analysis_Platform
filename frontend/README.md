# Financial Analysis Platform Frontend

This is the frontend application for the Financial Analysis Platform, a comprehensive tool for stock market analysis, prediction, and financial news tracking.

## Features

- **Dashboard**: Overview of market trends, portfolio performance, and key insights
- **Stock Analysis**: Detailed analysis of individual stocks with charts and historical data
- **News Aggregation**: Latest financial news from multiple sources
- **ML-based Predictions**: Machine learning predictions for stock performance
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Technology Stack

- React.js
- Material UI
- Chart.js
- React Router
- Axios for API calls

## Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd financial-analysis-platform/frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Start the development server:
   ```
   npm start
   ```
   
## Project Structure

```
src/
├── components/        # Reusable UI components
├── contexts/          # React Context providers
├── layouts/           # Page layout components
├── pages/             # Page components
├── services/          # API services
├── theme/             # UI theme configuration
├── App.js             # Main application component
└── index.js           # Application entry point
```

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm build`: Builds the app for production
- `npm test`: Runs the test suite
- `npm eject`: Ejects from Create React App

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```
REACT_APP_API_URL=http://localhost:5000/api
```

## Docker

The application can be run in a Docker container. Use the provided Dockerfile or docker-compose.yml from the root directory.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request