# Live Support Assistant - AI Agent Implementation

## Overview
The Live Support Assistant has been transformed from a static chat UI into a fully functional AI Agent that connects to all system monitoring services and provides intelligent responses based on real data.

## Features

### 🤖 Intelligent Intent Detection
The AI agent can understand and respond to various types of queries:
- **System Health**: CPU, memory, disk usage, uptime
- **Error Analysis**: Recent errors from AI bot issues
- **Incident Reports**: Safety incidents and accidents
- **Security Monitoring**: Log analysis for suspicious activities
- **Weather Impact**: Current weather conditions and recommendations
- **Financial Summary**: Revenue and invoice status
- **Fleet Status**: Driver and vehicle information

### 🔗 Real Data Integration
- **System Monitor**: Real-time system metrics using psutil
- **Database Queries**: Direct queries to PostgreSQL for issues, incidents, invoices
- **Log Analysis**: Pattern-based security log analysis
- **Weather API**: OpenWeatherMap integration
- **Bot Coordination**: Connects with other AI bots in the system

### 💬 Interactive Features
- **Quick Action Buttons**: Pre-defined queries for common tasks
- **Conversation History**: Persistent chat sessions
- **Real-time Responses**: Async processing with typing indicators
- **Session Management**: Automatic session handling and storage

## API Endpoints

### POST /api/v1/support/chat
Send a message to the live support AI agent.

**Request Body:**
```json
{
  "message": "Show system health",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "success": true,
  "response": "📊 **System Health Report**\n\n**Status:** healthy...",
  "intent": "system_health",
  "session_id": "session_1234567890.123456",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### GET /api/v1/support/health
Check the health status of the live support service.

**Response:**
```json
{
  "status": "online",
  "service": "Live Support Assistant",
  "version": "2.0",
  "features": ["system_health", "error_analysis", "security", "weather", "finance"]
}
```

### GET /api/v1/support/conversation/{session_id}
Retrieve conversation history for a specific session.

**Response:**
```json
{
  "session_id": "session_1234567890.123456",
  "history": [
    {
      "user_id": "user123",
      "message": "Show system health",
      "response": "📊 **System Health Report**...",
      "timestamp": "2024-01-15T10:30:00.000000"
    }
  ],
  "total": 1
}
```

## Usage Examples

### System Health Check
```
User: "Show system health"
AI: 📊 **System Health Report**

**Status:** healthy
**CPU Usage:** 15.2%
**Memory Usage:** 45.8%
**Disk Usage:** 67.3%
**Uptime:** 2 days, 4:23:15.123456

All systems are operational. No critical issues detected.
```

### Error Analysis
```
User: "Any recent errors?"
AI: 🔧 **Recent Errors**

  • Database connection timeout (Status: resolved)
  • API rate limit exceeded (Status: in_progress)
  • Memory usage spike (Status: open)

**Total:** 3 errors in the last 24 hours.
Would you like me to investigate any specific error?
```

### Security Monitoring
```
User: "Security status"
AI: 🛡️ **Security Alert**

Detected 2 suspicious events in the last 24 hours:

  • Failed login attempt - 192.168.1.100
  • Unauthorized API access - 10.0.0.50

**Recommendation:** Review authentication logs for details
```

## Technical Implementation

### Backend Services
- **LiveSupportService**: Main AI agent logic and intent processing
- **SystemMonitor**: Real-time system metrics collection
- **LogAnalysisService**: Security log pattern analysis
- **WeatherService**: External weather API integration

### Database Models
- **AIBotIssue**: AI bot error tracking
- **SafetyIncident**: Safety incident reports
- **Invoice**: Financial transaction records

### Frontend Component
- **LiveSupportChat.jsx**: React component with real-time chat interface
- **Quick Actions**: Pre-defined query buttons
- **Session Persistence**: Local storage for conversation continuity

## Configuration

### Environment Variables
Ensure the following environment variables are set for full functionality:
- `OPENWEATHERMAP_API_KEY`: For weather data
- Database connection settings for PostgreSQL

### Dependencies
The implementation uses existing project dependencies:
- FastAPI for API endpoints
- SQLAlchemy for database operations
- psutil for system monitoring
- aiohttp for async HTTP requests

## Integration Points

### With Other AI Bots
The Live Support Assistant can coordinate with:
- **Safety Manager**: Incident data and safety reports
- **Operations Manager**: System status and performance
- **Finance Bot**: Revenue and invoice summaries
- **Weather Service**: Environmental impact analysis

### Real-time Monitoring
- System metrics updated every request
- Database queries for latest incident/error data
- Log analysis with configurable time windows
- Weather data cached and refreshed appropriately

## Future Enhancements

### Planned Features
- **Voice Integration**: Speech-to-text and text-to-speech
- **Multi-language Support**: Arabic and other languages
- **Advanced Analytics**: Trend analysis and predictive insights
- **Integration APIs**: Webhooks for external system notifications
- **Custom Commands**: User-defined automation scripts

### Scalability Improvements
- **Caching Layer**: Redis for frequently accessed data
- **Load Balancing**: Multiple instances support
- **Rate Limiting**: API protection and fair usage
- **Audit Logging**: Comprehensive conversation logging

## Testing

### Manual Testing
1. Start the backend server: `python -m uvicorn backend.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to the Live Support chat interface
4. Test various queries using quick action buttons
5. Verify responses contain real data from the system

### API Testing
```bash
# Health check
curl http://localhost:8000/api/v1/support/health

# Send message
curl -X POST http://localhost:8000/api/v1/support/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show system health"}'
```

## Troubleshooting

### Common Issues
1. **Service Offline**: Check backend server status and logs
2. **No Data Responses**: Verify database connections and API keys
3. **Import Errors**: Ensure all required models and services exist
4. **Weather API Errors**: Check OpenWeatherMap API key configuration

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in environment variables.

## Conclusion

The Live Support Assistant is now a fully functional AI agent that provides intelligent, data-driven responses based on real system monitoring and database queries. It serves as a central hub for system operations, connecting users with relevant information and coordinating with other AI services in the platform.