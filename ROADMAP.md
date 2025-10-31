# Pepper Development Roadmap

This document outlines the development roadmap for Pepper, a voice-controlled AI agent for Microsoft Outlook operations. The project is divided into six major stages, each building upon the previous one to create a production-ready application.

## Current Status

**Stage 1: Backend API with Microsoft Graph Integration** - ✅ Mostly Complete
- OAuth 2.0 authentication with PKCE flow is implemented
- Microsoft Graph API wrappers for email and calendar operations are complete
- Basic testing infrastructure is in place
- Integration tests and manual testing collection still needed

---

## Stage 1: Backend API with Microsoft Graph Integration

**Goal**: Build a robust backend API service that can authenticate with Microsoft and perform Outlook operations.

### Components

#### 1.1 Project Setup ✅
- [x] Initialize Python with FastAPI project using UV package manager
- [x] Install core dependencies (msgraph-core, azure-identity, msal)
- [x] Configure environment variables for Azure AD
- [x] Create basic server with health check endpoint
- [x] Set up unit testing infrastructure

#### 1.2 OAuth 2.0 Implementation ✅
- [x] Implement OAuth controller with login, callback, refresh, and logout routes
- [x] Implement PKCE (Proof Key for Code Exchange) flow for secure authentication
- [x] Securely store and manage access/refresh tokens
- [x] Test authentication flow with Microsoft test tenant

#### 1.3 Microsoft Graph API Wrappers ✅
- [x] Create authenticated GraphClient wrapper class
- [x] Implement email operations (write, send, search, read)
- [x] Implement calendar operations (scheduling assistant, schedule meeting)
- [x] Add error handling with exponential backoff retries
- [x] Add comprehensive request/response logging

#### 1.4 Testing 🚧
- [x] Write unit tests for API wrappers with mocked Graph API
- [ ] Create integration tests with real Microsoft account
- [ ] Test error scenarios (expired tokens, rate limits, invalid input)
- [ ] Create API testing collection (Postman/Thunder Client)

**Deliverable**: Backend API service that can authenticate and perform Outlook operations

---

## Stage 2: LLM Agent with Tool Calling

**Goal**: Build an intelligent agent that translates natural language into Outlook operations using Claude's tool calling capabilities.

### Components

#### 2.1 Agent Infrastructure
- [ ] Install Anthropic SDK
- [ ] Create agent controller module
- [ ] Define tool schemas for all Outlook operations in Claude format
- [ ] Create system prompt with operational constraints and safety guidelines

#### 2.2 Tool Execution Layer
- [ ] Create tool registry (whitelist of allowed tools)
- [ ] Implement tool validator with parameter checking and input sanitization
- [ ] Create tool executor to map tool calls to Graph API wrappers
- [ ] Implement confirmation system for destructive actions (send email, schedule meeting)

#### 2.3 Agent Controller
- [ ] Implement conversation management with message history
- [ ] Create main agent loop for processing user requests
- [ ] Parse and execute tool calls from Claude responses
- [ ] Add error handling for LLM failures

#### 2.4 CLI Interface for Testing
- [ ] Create command-line interface for agent interaction
- [ ] Display agent responses and tool calls
- [ ] Implement confirmation prompts (yes/no)
- [ ] Add debugging mode for development

#### 2.5 Testing
- [ ] Test each tool individually via CLI
- [ ] Test multi-turn conversations
- [ ] Validate security (whitelist enforcement, confirmation bypass prevention)
- [ ] Test error handling scenarios

**Deliverable**: CLI-based agent that performs Outlook operations via natural language

---

## Stage 3: Voice Interface (Desktop Prototype)

**Goal**: Create a desktop application with voice input/output for rapid prototyping and user testing.

### Components

#### 3.1 Desktop App Setup
- [ ] Initialize Electron project
- [ ] Create UI with microphone button, transcript display, and status indicators
- [ ] Set up basic window management

#### 3.2 Speech-to-Text Integration
- [ ] Choose and integrate STT service (Web Speech API, Whisper, or Google Cloud)
- [ ] Implement audio capture and speech recognition
- [ ] Add silence detection and interim results display
- [ ] Handle microphone permissions and errors

#### 3.3 Text-to-Speech Integration
- [ ] Choose and integrate TTS service (Web Speech API, OpenAI TTS, or Google Cloud)
- [ ] Implement speech synthesis for agent responses
- [ ] Add playback controls and visual indicators

#### 3.4 Backend Integration
- [ ] Connect to Stage 2 agent backend
- [ ] Display conversation history
- [ ] Implement authentication UI
- [ ] Handle voice-based confirmations

#### 3.5 Testing
- [ ] Test across operating systems (Windows, Mac, Linux)
- [ ] Measure voice recognition accuracy and latency
- [ ] Test confirmation flow via voice commands
- [ ] Test interruption handling

**Deliverable**: Desktop app with voice input/output for agent interaction

---

## Stage 4: Mobile App Foundation

**Goal**: Build native iOS and Android apps with authentication and basic functionality.

### Components

#### 4.1 iOS App Setup
- [ ] Create Xcode project with SwiftUI
- [ ] Configure app capabilities (microphone, network)
- [ ] Set up Keychain for secure token storage
- [ ] Create basic UI screens (main, settings, login)

#### 4.2 Android App Setup
- [ ] Create Android Studio project with Jetpack Compose
- [ ] Configure permissions (RECORD_AUDIO, INTERNET)
- [ ] Set up KeyStore for secure token storage
- [ ] Create basic UI screens

#### 4.3 OAuth Mobile Implementation
- [ ] Implement iOS OAuth flow with SFSafariViewController
- [ ] Implement Android OAuth flow with Chrome Custom Tabs
- [ ] Handle OAuth redirects and token exchange
- [ ] Implement token refresh on app launch

#### 4.4 Backend API Client
- [ ] Create iOS NetworkManager with URLSession
- [ ] Create Android ApiClient with Retrofit
- [ ] Implement API calls to agent backend
- [ ] Add authentication headers and error handling

#### 4.5 Testing
- [ ] Test OAuth flow on real devices
- [ ] Verify token storage security
- [ ] Test API communication and error handling
- [ ] Test across multiple devices and OS versions

**Deliverable**: Native mobile apps with authentication and basic text chat

---

## Stage 5: Mobile Voice Integration

**Goal**: Add voice input/output capabilities to mobile apps for full voice-controlled experience.

### Components

#### 5.1 iOS Voice Implementation
- [ ] Implement Speech Recognition with AVSpeechRecognizer
- [ ] Implement Text-to-Speech with AVSpeechSynthesizer
- [ ] Add visual feedback (waveform animations, status indicators)
- [ ] Handle background audio sessions and interruptions

#### 5.2 Android Voice Implementation
- [ ] Implement Speech Recognition with SpeechRecognizer
- [ ] Implement Text-to-Speech with android.speech.tts.TextToSpeech
- [ ] Add visual feedback
- [ ] Handle audio focus changes

#### 5.3 Conversation UI
- [ ] Create conversation view/screen with message history
- [ ] Display typing/processing indicators
- [ ] Add confirmation buttons for destructive actions
- [ ] Implement local conversation history storage

#### 5.4 Settings & Account Management
- [ ] Create settings screen with account info
- [ ] Add logout functionality
- [ ] Implement voice settings (speech rate, voice selection)
- [ ] Add privacy policy and about sections

#### 5.5 Testing
- [ ] Test full voice workflow on both platforms
- [ ] Test interruption scenarios (calls, backgrounding)
- [ ] Measure battery consumption
- [ ] Test with Bluetooth headsets
- [ ] Verify accessibility features (VoiceOver, TalkBack)

**Deliverable**: Fully functional mobile apps with voice control

---

## Stage 6: Production Hardening

**Goal**: Prepare the application for public release with polish, security, and compliance.

### Components

#### 6.1 Error Handling & UX Polish
- [ ] Improve error messages and retry mechanisms
- [ ] Add loading states and empty states
- [ ] Enhance confirmation dialogs with previews
- [ ] Implement undo functionality where possible

#### 6.2 Onboarding Flow
- [ ] Create welcome screens explaining features
- [ ] Add permission request explanations
- [ ] Create interactive tutorial for first use
- [ ] Add help screen with sample commands

#### 6.3 Performance Optimization
- [ ] Profile app performance (Instruments/Profiler)
- [ ] Optimize voice recognition latency
- [ ] Reduce memory usage
- [ ] Implement caching strategies

#### 6.4 Analytics & Monitoring
- [ ] Integrate privacy-respecting analytics
- [ ] Track key metrics (success rate, usage patterns)
- [ ] Add crash reporting
- [ ] Implement debug logging

#### 6.5 Security Audit
- [ ] Review token storage implementation
- [ ] Verify HTTPS everywhere
- [ ] Test for common vulnerabilities (OWASP Mobile Top 10)
- [ ] Add certificate pinning
- [ ] Minimize app permissions

#### 6.6 Compliance & Legal
- [ ] Create privacy policy and terms of service
- [ ] Ensure GDPR compliance
- [ ] Add data deletion functionality
- [ ] Review Microsoft API usage terms

#### 6.7 App Store Preparation
- [ ] Create App Store Connect listing (iOS)
- [ ] Create Google Play Console listing (Android)
- [ ] Prepare screenshots and descriptions
- [ ] Set up beta testing (TestFlight/Play Console)
- [ ] Submit for review

#### 6.8 Beta Testing
- [ ] Recruit beta testers (10-50 users)
- [ ] Collect feedback via surveys and in-app mechanisms
- [ ] Monitor crash reports and errors
- [ ] Iterate based on feedback

#### 6.9 Documentation
- [ ] Create user documentation and FAQ
- [ ] Document API endpoints
- [ ] Create troubleshooting guide
- [ ] Write deployment guide

**Deliverable**: Production-ready mobile apps ready for public release

---

## Post-Launch Maintenance

### Ongoing Responsibilities
- Monitor error rates, crashes, and user feedback
- Regular dependency and security updates
- Microsoft Graph API version compatibility
- iOS/Android OS updates
- Feature enhancements based on user requests
- LLM prompt optimization based on usage patterns

---

## Timeline Estimates

- **Stage 1**: 2-3 weeks (mostly complete)
- **Stage 2**: 2-3 weeks
- **Stage 3**: 2-3 weeks
- **Stage 4**: 3-4 weeks
- **Stage 5**: 2-3 weeks
- **Stage 6**: 4-6 weeks

**Total estimated time**: 15-22 weeks (approximately 4-5 months)

Note: Timeline assumes a single full-time developer. Parallel work on iOS/Android could reduce overall timeline.
