# Create backend project directory
- [x] Initialize Python with FastAPI project (use UV for the package manager)
- [x] Install dependencies: msgraph-core, azure-identity, msal
- [x] Set up environment variables (.env file for client ID, tenant ID, redirect URI)
- [x] Create basic server with health check endpoint
- [x] Create unit test for the health endpoint
```

### 1.2 OAuth 2.0 Implementation
```
- [x] Create OAuth controller with routes:
  - GET /auth/login → Redirect to Microsoft login
  - GET /auth/callback → Handle OAuth callback
  - POST /auth/refresh → Refresh access token
  - POST /auth/logout → Revoke tokens
- [x] Implement PKCE flow (code_challenge generation)
- [x] Store tokens securely (encrypted in database or session)
- [x] Test with Microsoft test tenant
```

### 1.3 Microsoft Graph API Wrappers
```
- [ ] Create GraphClient wrapper class with authenticated client
- [ ] Implement email operations:
  - writeEmail(to, cc, subject, body, importance) → Returns draft
  - sendEmail(draftId OR email params) → Sends email
  - searchEmails(query, folder, top, fromDate) → Returns results
  - readEmail(messageId) → Returns full email
- [ ] Implement calendar operations:
  - checkSchedulingAssistant(attendees, duration, startDate, endDate, timezone)
  - scheduleMeeting(subject, attendees, startTime, endTime, location, body, isOnline)
- [ ] Add error handling and retries (exponential backoff)
- [ ] Add request/response logging
```

### 1.4 Testing
```
- [ ] Write unit tests for each API wrapper (mock Graph API)
- [ ] Create integration tests with real Microsoft account:
  - Test OAuth flow end-to-end
  - Test token refresh
  - Test each email operation
  - Test each calendar operation
- [ ] Test error scenarios (expired token, rate limits, invalid input)
- [ ] Create Postman/Thunder collection for manual API testing
```

**Deliverable**: Backend API service that can authenticate and perform Outlook operations

---

## Stage 2: LLM Agent with Tool Calling

### 2.1 Agent Infrastructure
```
- [ ] Install Anthropic SDK
- [ ] Create agent controller module
- [ ] Define tool schemas in Claude format:
  - write_email tool definition
  - send_email tool definition
  - check_scheduling_assistant tool definition
  - schedule_meeting tool definition
  - search_emails tool definition
  - read_email tool definition
- [ ] Create system prompt with constraints and instructions
```

### 2.2 Tool Execution Layer
```
- [ ] Create tool registry (whitelist of allowed tools)
- [ ] Implement tool validator:
  - Check tool name against whitelist
  - Validate parameters against schema
  - Sanitize inputs (XSS prevention, email format validation)
- [ ] Create tool executor that maps tool calls to API wrappers
- [ ] Implement confirmation system for destructive actions:
  - Flag tools requiring confirmation (send_email, schedule_meeting)
  - Return confirmation prompt to user
  - Wait for explicit approval before executing
```

### 2.3 Agent Controller
```
- [ ] Create conversation management:
  - Initialize conversation with system prompt
  - Maintain message history
  - Handle multi-turn interactions
- [ ] Implement main agent loop:
  - Receive user input
  - Call Claude API with tools
  - Parse tool use requests
  - Execute tools via tool executor
  - Format and return response
- [ ] Add error handling for LLM failures
```

### 2.4 CLI Interface for Testing
```
- [ ] Create simple command-line interface:
  - Read user input from terminal
  - Display agent responses
  - Show tool calls and confirmations
  - Allow yes/no confirmations
- [ ] Add debugging mode (show raw tool calls, API responses)
```

### 2.5 Testing
```
- [ ] Test each tool individually via CLI:
  - "Draft an email to test@example.com about meeting"
  - "Send the email"
  - "Check availability for test@example.com tomorrow 2-3pm"
  - "Schedule a meeting with test@example.com"
  - "Search my emails for budget report"
- [ ] Test multi-turn conversations:
  - Agent asks for missing information
  - User provides info incrementally
- [ ] Test validation and security:
  - Try to call non-whitelisted tools
  - Try to bypass confirmations
  - Invalid parameters
- [ ] Test error handling (API failures, LLM timeouts)
```

**Deliverable**: CLI-based agent that can perform Outlook operations via natural language

---

## Stage 3: Voice Interface (Desktop Prototype)

### 3.1 Desktop App Setup
```
- [ ] Choose framework (Electron recommended for rapid prototyping)
- [ ] Initialize Electron project
- [ ] Create main window with basic UI:
  - Microphone button (push-to-talk)
  - Transcript display area
  - Agent response display
  - Status indicator (listening/processing/speaking)
```

### 3.2 Speech-to-Text Integration
```
- [ ] Choose STT service:
  - Option A: Web Speech API (browser-based, free, limited)
  - Option B: OpenAI Whisper API (more accurate, costs money)
  - Option C: Google Cloud Speech-to-Text
- [ ] Implement audio capture (getUserMedia API)
- [ ] Implement speech recognition:
  - Start listening on button press
  - Start listening on voice command
  - Stop on button release or silence detection
  - Display interim results
  - Return final transcript
- [ ] Add error handling (no microphone, permissions denied)
```

### 3.3 Text-to-Speech Integration
```
- [ ] Choose TTS service:
  - Option A: Web Speech API (browser-based, free)
  - Option B: OpenAI TTS API
  - Option C: Google Cloud Text-to-Speech
- [ ] Implement speech synthesis:
  - Convert agent responses to speech
  - Play audio through speakers
  - Show speaking indicator
- [ ] Add controls (stop, volume adjustment)
```

### 3.4 Backend Integration
```
- [ ] Connect to Stage 2 agent backend:
  - Send transcribed text to agent
  - Receive agent responses
  - Handle confirmations via voice or button
- [ ] Display conversation history
- [ ] Add authentication UI (login with Microsoft)
```

### 3.5 Testing
```
- [ ] Test microphone functionality across OS (Windows, Mac, Linux)
- [ ] Test voice recognition accuracy:
  - Different accents
  - Background noise
  - Different microphone types
- [ ] Measure latency (speech → response → speech)
- [ ] Test confirmation flow via voice ("yes", "send it", "confirm")
- [ ] Test interruption handling (stop mid-sentence)
```

**Deliverable**: Desktop app with voice input/output for agent interaction

---

## Stage 4: Mobile App Foundation

### 4.1 iOS App Setup
```
- [ ] Create Xcode project
- [ ] Set up SwiftUI views:
  - Main screen with microphone button
  - Settings screen
  - Login screen
- [ ] Configure app capabilities:
  - Microphone access (NSMicrophoneUsageDescription in Info.plist)
  - Network access
- [ ] Set up Keychain access for token storage
```

### 4.2 Android App Setup
```
- [ ] Create Android Studio project
- [ ] Set up Jetpack Compose views:
  - Main screen with microphone button
  - Settings screen
  - Login screen
- [ ] Configure permissions in AndroidManifest.xml:
  - RECORD_AUDIO
  - INTERNET
- [ ] Set up KeyStore for token storage
```

### 4.3 OAuth Mobile Implementation

**iOS:**
```
- [ ] Configure URL scheme for OAuth redirect (e.g., msalapp://auth)
- [ ] Implement OAuth flow:
  - Open SFSafariViewController for Microsoft login
  - Handle redirect back to app
  - Exchange code for tokens
- [ ] Store tokens in Keychain
- [ ] Implement token refresh on app launch
```

**Android:**
```
- [ ] Configure app link for OAuth redirect
- [ ] Implement OAuth flow:
  - Open Chrome Custom Tab for Microsoft login
  - Handle redirect via deep link
  - Exchange code for tokens
- [ ] Store tokens in EncryptedSharedPreferences
- [ ] Implement token refresh on app launch
```

### 4.4 Backend API Client

**iOS:**
```
- [ ] Create NetworkManager with URLSession
- [ ] Implement API calls:
  - POST /agent/chat (send user message)
  - POST /auth/refresh (refresh token)
- [ ] Add authentication headers (Bearer token)
- [ ] Handle errors and retries
```

**Android:**
```
- [ ] Create ApiClient with Retrofit
- [ ] Implement API calls:
  - POST /agent/chat (send user message)
  - POST /auth/refresh (refresh token)
- [ ] Add authentication interceptor
- [ ] Handle errors and retries
```

### 4.5 Testing
```
- [ ] Test OAuth flow on real iOS device
- [ ] Test OAuth flow on real Android device
- [ ] Verify token storage security (cannot be read by other apps)
- [ ] Test token refresh mechanism
- [ ] Test API communication (send text message, receive response)
- [ ] Test network error handling (airplane mode, slow connection)
- [ ] Test on multiple device sizes and OS versions
```

**Deliverable**: Native mobile apps with authentication and basic text chat

---

## Stage 5: Mobile Voice Integration

### 5.1 iOS Voice Implementation
```
- [ ] Request microphone permission
- [ ] Implement Speech Recognition (AVSpeechRecognizer):
  - Create SFSpeechRecognizer instance
  - Set up audio engine
  - Start recognition on voice command
  - Stop on button release
  - Display interim and final results
- [ ] Implement Text-to-Speech (AVSpeechSynthesizer):
  - Create synthesizer
  - Convert agent responses to speech
  - Play audio
  - Handle interruptions
- [ ] Add visual feedback (waveform animation, status indicators)
- [ ] Handle background audio sessions
```

### 5.2 Android Voice Implementation
```
- [ ] Request RECORD_AUDIO permission
- [ ] Implement Speech Recognition (SpeechRecognizer):
  - Create RecognizerIntent
  - Start listening on button press
  - Stop on button release
  - Parse results
- [ ] Implement Text-to-Speech (android.speech.tts.TextToSpeech):
  - Initialize TTS engine
  - Convert agent responses to speech
  - Play audio
- [ ] Add visual feedback (waveform animation, status indicators)
- [ ] Handle audio focus changes
```

### 5.3 Conversation UI
```
iOS:
- [ ] Create ConversationView (List of messages)
- [ ] Display user messages and agent responses
- [ ] Show typing/processing indicator
- [ ] Add confirmation buttons for send/schedule actions
- [ ] Store conversation history locally (CoreData or UserDefaults)

Android:
- [ ] Create ConversationScreen (LazyColumn of messages)
- [ ] Display user messages and agent responses
- [ ] Show loading indicator
- [ ] Add confirmation buttons for destructive actions
- [ ] Store conversation history locally (Room database)
```

### 5.4 Settings & Account Management
```
iOS:
- [ ] Create SettingsView:
  - Account info display
  - Logout button
  - Voice settings (speech rate, voice selection)
  - Privacy policy link
  - About section

Android:
- [ ] Create SettingsScreen:
  - Account info display
  - Logout button
  - Voice settings
  - Privacy policy link
  - About section
```

### 5.5 Testing
```
- [ ] Full voice workflow testing on iOS:
  - Voice command → transcription → agent → Outlook action → voice response
- [ ] Full voice workflow testing on Android:
  - Voice command → transcription → agent → Outlook action → voice response
- [ ] Test interruption scenarios:
  - Incoming call during voice interaction
  - App backgrounded during processing
  - Audio from other apps
- [ ] Test battery consumption (voice recognition is power-intensive)
- [ ] Test with Bluetooth headsets (AirPods, etc.)
- [ ] Test accessibility features:
  - VoiceOver on iOS
  - TalkBack on Android
- [ ] Test on various devices and OS versions
```

**Deliverable**: Fully functional mobile apps with voice control

---

## Stage 6: Production Hardening

### 6.1 Error Handling & UX Polish
```
- [ ] Improve error messages (user-friendly, actionable)
- [ ] Add retry mechanisms with user feedback
- [ ] Implement loading states for all operations
- [ ] Add empty states (no conversations, not logged in)
- [ ] Improve confirmation dialogs (show email preview before sending)
- [ ] Add undo functionality for sent emails (if possible)
```

### 6.2 Onboarding Flow
```
- [ ] Create welcome screens explaining features
- [ ] Add permission request explanations (why microphone is needed)
- [ ] Create tutorial for first voice command
- [ ] Add sample commands help screen
```

### 6.3 Performance Optimization
```
- [ ] Profile app performance (Instruments on iOS, Profiler on Android)
- [ ] Optimize voice recognition latency
- [ ] Reduce memory usage
- [ ] Implement image and resource optimization
- [ ] Add response caching where appropriate
```

### 6.4 Analytics & Monitoring
```
- [ ] Integrate privacy-respecting analytics (e.g., TelemetryDeck, PostHog)
- [ ] Track key metrics:
  - Voice command success rate
  - Tool usage frequency
  - Error rates
  - Session duration
- [ ] Add crash reporting (Sentry or Crashlytics)
- [ ] Implement logging for debugging
```

### 6.5 Security Audit
```
- [ ] Review token storage implementation
- [ ] Check for API key exposure
- [ ] Verify HTTPS everywhere
- [ ] Test for common vulnerabilities (OWASP Mobile Top 10)
- [ ] Review permissions (minimize to essential only)
- [ ] Add certificate pinning
```

### 6.6 Compliance & Legal
```
- [ ] Create privacy policy
- [ ] Create terms of service
- [ ] Ensure GDPR compliance (if applicable)
- [ ] Add data deletion functionality
- [ ] Review Microsoft API usage terms
```

### 6.7 App Store Preparation

**iOS:**
```
- [ ] Create App Store Connect listing
- [ ] Prepare screenshots (all device sizes)
- [ ] Write app description
- [ ] Create app icon (all sizes)
- [ ] Set up TestFlight for beta testing
- [ ] Submit for App Review
```

**Android:**
```
- [ ] Create Google Play Console listing
- [ ] Prepare screenshots (phone, tablet)
- [ ] Write app description
- [ ] Create app icon and feature graphic
- [ ] Set up internal testing track
- [ ] Submit for review
```

### 6.8 Beta Testing
```
- [ ] Recruit beta testers (10-50 users)
- [ ] Distribute via TestFlight (iOS) and Play Console (Android)
- [ ] Collect feedback via survey and in-app mechanism
- [ ] Monitor crash reports and errors
- [ ] Iterate based on feedback
```

### 6.9 Documentation
```
- [ ] Create user documentation/FAQ
- [ ] Create developer documentation for backend
- [ ] Document API endpoints
- [ ] Create troubleshooting guide
- [ ] Write deployment guide
```

**Deliverable**: Production-ready mobile apps ready for public release

---

## Post-Launch Maintenance

### Ongoing Tasks
```
- [ ] Monitor error rates and crashes
- [ ] Respond to user feedback and reviews
- [ ] Regular dependency updates (security patches)
- [ ] Microsoft Graph API version updates
- [ ] iOS/Android OS compatibility updates
- [ ] Add new features based on user requests
- [ ] Improve LLM prompts based on usage patterns