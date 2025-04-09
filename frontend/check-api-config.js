// Simple script to output the API configuration and URL paths used in the frontend
console.log('Frontend API Configuration Check');
console.log('===============================');

// Import the configuration from this file (by printing its content)
const chartServicePath = require('path').resolve(__dirname, 'src/services/chart.js');
const fs = require('fs');

console.log(`Checking chart service at: ${chartServicePath}`);
console.log('\nChart Service Content:');
console.log('---------------------');

try {
  const chartServiceContent = fs.readFileSync(chartServicePath, 'utf8');
  // Extract URL paths with regex
  const apiCallMatches = chartServiceContent.match(/api\.get\(`\/[^`]+`/g) || [];
  const apiEndpoints = apiCallMatches.map(match => match.replace('api.get(`', '').replace('`', ''));
  
  console.log('\nAPI Endpoints used in chart.js:');
  apiEndpoints.forEach(endpoint => {
    console.log(`- ${endpoint}`);
  });
  
  // Check the baseURL configuration
  const apiServicePath = require('path').resolve(__dirname, 'src/services/api.js');
  const apiServiceContent = fs.readFileSync(apiServicePath, 'utf8');
  
  // Extract baseURL with regex
  const baseUrlMatch = apiServiceContent.match(/baseURL:\s*['"]([^'"]+)['"]/);
  console.log('\nAPI Base URL Configuration:');
  if (baseUrlMatch) {
    console.log(`- Base URL: ${baseUrlMatch[1]}`);
  } else {
    console.log('- Base URL not found in api.js');
  }
  
} catch (error) {
  console.error('Error reading chart service file:', error);
}

// Suggest a manual test with curl
console.log('\nSuggested CURL Test:');
console.log('------------------');
console.log('Run this command to test the API directly:');
console.log('curl -X GET "http://localhost:8002/api/stocks/AAPL/historical/?period=1mo&interval=1d" -H "Authorization: Bearer YOUR_TOKEN_HERE" -v');
console.log('\nReplace YOUR_TOKEN_HERE with a valid access token from your browser\'s local storage.');
