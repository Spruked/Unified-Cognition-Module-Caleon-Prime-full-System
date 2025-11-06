# Unified Cognition System Frontend

A modern, responsive web interface for interacting with the unified cognition system.

## Features

🧠 **Cognitive Query Interface**
- Submit natural language queries to the cognition system
- Adjustable priority levels (low, medium, high)
- Custom context JSON support

🎯 **Real-time System Monitoring**
- Live health status of all cognitive modules
- Visual indicators for system components

🔍 **Detailed Response Visualization**
- Harmonized final response display
- Individual module response breakdown
- Color-coded status indicators

📊 **Trace Logging**
- Real-time trace log of system activities
- Timestamped entries with status levels
- Scrollable log viewer with 50-entry history

## Architecture

The frontend communicates directly with the cerebral cortex API (`http://localhost:8000`) and provides:

- **Input Processing**: Converts user queries into structured API requests
- **Response Rendering**: Displays harmonized responses and module breakdowns
- **Health Monitoring**: Polls module health endpoints every 30 seconds
- **Trace Management**: Maintains client-side activity logs

## Usage

1. **Access the Interface**: Open `http://localhost:8080` in your browser
2. **Monitor System Health**: Check the status cards at the top
3. **Submit Queries**: Enter your cognitive query and click "Process Query"
4. **View Results**: See harmonized responses and individual module outputs
5. **Track Activity**: Monitor the trace log for system activities

## API Integration

The frontend expects the cerebral cortex to provide:

```javascript
// Request format
{
  "input_data": "What is unified cognition?",
  "context": {"source": "frontend", "user_id": "demo"},
  "priority": "high"
}

// Response format
{
  "input": "What is unified cognition?",
  "active_modules": ["echostack", "resonator", "gyro-harmonizer"],
  "module_responses": {
    "echostack": { /* module response */ },
    "resonator": { /* module response */ },
    "gyro-harmonizer": { /* harmonized response */ }
  },
  "harmonized_response": "Final harmonized answer..."
}
```

## Development

To modify the frontend:

1. Edit `frontend/index.html` for UI changes
2. Update the `API_BASE` constant for different endpoints
3. Modify CSS styles for visual customization
4. Add new features using the existing JavaScript framework

## Deployment

The frontend is served via Nginx in a Docker container and automatically mounts the local `frontend/` directory for live development.