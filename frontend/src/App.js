import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
  AppBar,
  Toolbar,
  Drawer,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import AddIcon from '@mui/icons-material/Add';
import ChatIcon from '@mui/icons-material/Chat';
import DescriptionIcon from '@mui/icons-material/Description';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import { styled } from '@mui/material/styles';
import Message from './components/Message';
import Documents from './components/Documents';
import { chatService } from './services/api';
import theme from './theme';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

// Styled components
const ChatContainer = styled(Paper)(({ theme }) => ({
  height: 'calc(100vh - 140px)',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
}));

const MessagesArea = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: theme.palette.background.default,
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: theme.palette.divider,
    borderRadius: '4px',
  },
}));

const InputArea = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderTop: `1px solid ${theme.palette.divider}`,
  boxShadow: '0 -2px 4px rgba(0,0,0,0.05)',
}));

// Sidebar width
const DRAWER_WIDTH = 280;

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [conversations, setConversations] = useState([
    { id: 1, title: 'New Conversation', active: true, messages: [] }
  ]);
  const [activeConversationId, setActiveConversationId] = useState(1);
  const messagesEndRef = useRef(null);
  const [currentPage, setCurrentPage] = useState('chat'); // 'chat' or 'documents'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connection on component mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await chatService.checkHealth();
        setConnectionStatus('connected');
      } catch (error) {
        console.error('Backend connection error:', error);
        setConnectionStatus('disconnected');
      }
    };

    checkConnection();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(input);
      
      // Debug: Log the debug info from backend
      if (response.debug) {
        console.log('=== BACKEND DEBUG INFO ===');
        console.log('All fields in ticket:', response.debug.all_fields);
        console.log('Has "number" field?:', response.debug.has_number);
        console.log('Number value:', response.debug.number_value);
        console.log('Sample ticket data:', response.debug.sample_ticket);
      }
      
      const assistantMessage = { role: 'assistant', content: response.response };
      
      // If there are similar tickets, add them as context
      if (response.similar_tickets && response.similar_tickets.length > 0) {
        // Extract ticket information properly
        const ticketInfoArray = response.similar_tickets.map((ticket, idx) => {
          const isDocument = ticket.document_type === 'support_document';
          const title = ticket.short_description || ticket.title || ticket.filename || 'No Description';
          
          // Get ticket number (Excel column "Number" becomes "number" in lowercase)
          const ticketNumber = ticket.number || ticket.Number;
          
          // Format display text
          if (isDocument) {
            return `Document: ${title}`;
          } else if (ticketNumber) {
            return `Ticket #${ticketNumber}: ${title}`;
          } else {
            return title;
          }
        });
        
        const contextMessage = {
          role: 'system',
          content: '**Similar tickets found:**\n' + ticketInfoArray.join('\n'),
          tickets: response.similar_tickets // Store the full ticket objects
        };
        setMessages(prev => [...prev, contextMessage]);
      }
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message || 'An error occurred while processing your request.'}`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    // Save current conversation
    saveCurrentConversation();
    
    // Create new conversation
    const newId = Math.max(...conversations.map(c => c.id)) + 1;
    const newConversation = {
      id: newId,
      title: 'New Conversation',
      active: true,
      messages: []
    };
    
    // Update conversations
    setConversations(prev => [
      newConversation,
      ...prev.map(c => ({ ...c, active: false }))
    ]);
    
    setActiveConversationId(newId);
    setMessages([]);
    setCurrentPage('chat');
  };

  const saveCurrentConversation = () => {
    if (messages.length > 0) {
      setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          // Generate title from first user message
          const firstUserMessage = messages.find(m => m.role === 'user');
          const title = firstUserMessage 
            ? firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '')
            : 'New Conversation';
          
          return { ...conv, messages: [...messages], title };
        }
        return conv;
      }));
    }
  };

  const handleConversationSwitch = (conversationId) => {
    // Save current conversation before switching
    saveCurrentConversation();
    
    // Load selected conversation
    const selectedConv = conversations.find(c => c.id === conversationId);
    if (selectedConv) {
      setMessages(selectedConv.messages || []);
      setActiveConversationId(conversationId);
      setConversations(prev => prev.map(c => ({
        ...c,
        active: c.id === conversationId
      })));
      setCurrentPage('chat');
    }
  };

  // Auto-save current conversation when messages change
  useEffect(() => {
    if (messages.length > 0) {
      const timeoutId = setTimeout(() => {
        saveCurrentConversation();
      }, 1000); // Debounce by 1 second

      return () => clearTimeout(timeoutId);
    }
  }, [messages]);

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* ChatGPT-like Sidebar */}
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              bgcolor: '#ffffff',
              borderRight: '1px solid',
              borderColor: 'divider',
              boxShadow: '2px 0 8px rgba(0,0,0,0.05)',
            },
          }}
        >
          <Box sx={{ p: 2, mt: 8 }}> {/* Add margin-top for the AppBar */}
            {/* Sidebar Header */}
            <Box 
              sx={{ 
                mb: 3, 
                pb: 2.5, 
                pt: 1,
                borderBottom: '2px solid', 
                borderColor: 'primary.main',
                background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(25, 118, 210, 0.02) 100%)',
                borderRadius: 2,
                px: 2,
                py: 2
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <Box
                  sx={{
                    width: 44,
                    height: 44,
                    borderRadius: 2.5,
                    bgcolor: 'primary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 1.5,
                    boxShadow: '0 4px 12px rgba(25, 118, 210, 0.4)',
                    background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'
                  }}
                >
                  <SupportAgentIcon sx={{ color: 'white', fontSize: '1.5rem' }} />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography 
                    sx={{ 
                      fontWeight: 700, 
                      color: 'primary.main',
                      fontSize: '1.15rem',
                      letterSpacing: '0.8px',
                      lineHeight: 1.3,
                      fontFamily: '"Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif'
                    }}
                  >
                    ASPIRE CMDB
                  </Typography>
                  <Typography 
                    sx={{ 
                      color: 'text.secondary',
                      fontWeight: 500,
                      fontSize: '0.7rem',
                      letterSpacing: '0.5px',
                      textTransform: 'uppercase',
                      mt: -0.3
                    }}
                  >
                    Support Assistant
                  </Typography>
                </Box>
              </Box>
            </Box>
            
            <Button 
              fullWidth
              startIcon={<AddIcon />}
              variant="outlined"
              sx={{
                color: 'primary.main',
                borderColor: 'primary.main',
                bgcolor: 'transparent',
                mb: 2,
                textTransform: 'none',
                justifyContent: 'flex-start',
                fontWeight: 500,
                py: 1.2,
                '&:hover': {
                  bgcolor: 'rgba(25, 118, 210, 0.08)',
                  borderColor: 'primary.main',
                }
              }}
              onClick={handleNewChat}
            >
              New chat
            </Button>
            
            <Button 
              fullWidth
              startIcon={<DescriptionIcon />}
              variant={currentPage === 'documents' ? 'contained' : 'outlined'}
              sx={{
                color: currentPage === 'documents' ? 'white' : 'primary.main',
                borderColor: 'primary.main',
                bgcolor: currentPage === 'documents' ? 'primary.main' : 'transparent',
                mb: 2,
                textTransform: 'none',
                justifyContent: 'flex-start',
                fontWeight: 500,
                py: 1.2,
                '&:hover': {
                  bgcolor: currentPage === 'documents' ? 'primary.dark' : 'rgba(25, 118, 210, 0.08)',
                  borderColor: 'primary.main',
                }
              }}
              onClick={() => setCurrentPage('documents')}
            >
              Documents
            </Button>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="overline" sx={{ px: 1, color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
              Recent Conversations
            </Typography>
            
            <List sx={{ mt: 1 }}>
              {conversations.map((conv) => (
                <ListItem 
                  key={conv.id} 
                  button 
                  selected={conv.id === activeConversationId && currentPage === 'chat'}
                  sx={{
                    mb: 1,
                    borderRadius: 2,
                    color: 'text.primary',
                    '&.Mui-selected': {
                      bgcolor: 'rgba(25, 118, 210, 0.12)',
                      color: 'primary.main',
                      '& .MuiSvgIcon-root': {
                        color: 'primary.main',
                      }
                    },
                    '&:hover': {
                      bgcolor: 'rgba(25, 118, 210, 0.08)',
                    }
                  }}
                  onClick={() => handleConversationSwitch(conv.id)}
                >
                  <ChatIcon sx={{ mr: 1.5, fontSize: '1.2rem', color: 'text.secondary' }} />
                  <ListItemText 
                    primary={conv.title} 
                    secondary={conv.messages?.length > 0 ? `${conv.messages.length} messages` : 'Empty'}
                    primaryTypographyProps={{ 
                      noWrap: true,
                      fontWeight: 500 
                    }}
                    secondaryTypographyProps={{
                      fontSize: '0.75rem',
                      color: 'text.secondary'
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <AppBar 
            position="fixed" 
            sx={{ 
              zIndex: (theme) => theme.zIndex.drawer + 1,
              bgcolor: 'primary.main',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                Aspire CMDB Support Assistant
              </Typography>
              {currentPage === 'chat' && (
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1,
                    backgroundColor: connectionStatus === 'connected' ? 'success.main' : 
                                  connectionStatus === 'checking' ? 'warning.main' : 'error.main',
                    padding: '6px 16px',
                    borderRadius: 2,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {connectionStatus === 'connected' ? 'Connected' :
                    connectionStatus === 'checking' ? 'Checking Connection...' : 'Disconnected'}
                  </Typography>
                </Box>
              )}
            </Toolbar>
          </AppBar>

          {/* Content based on current page */}
          <Box sx={{ mt: 8, p: 3, flexGrow: 1, bgcolor: 'background.default' }}>
            {currentPage === 'chat' ? (
              <ChatContainer elevation={3}>
                <MessagesArea>
                  {messages.map((message, index) => (
                    <Message 
                      key={index} 
                      message={message} 
                      tickets={message.tickets} 
                    />
                  ))}
                  {isLoading && (
                    <Box display="flex" justifyContent="center" my={2}>
                      <CircularProgress />
                    </Box>
                  )}
                  <div ref={messagesEndRef}></div>
                </MessagesArea>

                <InputArea>
                  <Box component="form" onSubmit={(e) => e.preventDefault()} sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                      fullWidth
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder={
                        connectionStatus === 'checking' 
                          ? "Checking connection..." 
                          : connectionStatus === 'disconnected' 
                          ? "Waiting for backend connection..." 
                          : "Type your message..."
                      }
                      variant="outlined"
                      size="medium"
                      disabled={connectionStatus !== 'connected' || isLoading}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                          '&:hover fieldset': {
                            borderColor: 'primary.main',
                          },
                          '&.Mui-focused fieldset': {
                            borderColor: 'primary.main',
                          },
                        },
                      }}
                    />
                    <IconButton
                      color="primary"
                      onClick={handleSend}
                      disabled={!input.trim() || isLoading || connectionStatus !== 'connected'}
                      sx={{
                        bgcolor: 'primary.main',
                        color: 'white',
                        '&:hover': {
                          bgcolor: 'primary.dark',
                        },
                        '&.Mui-disabled': {
                          bgcolor: 'action.disabledBackground',
                        },
                      }}
                    >
                      {isLoading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
                    </IconButton>
                  </Box>
                  {connectionStatus === 'disconnected' && (
                    <Typography color="error" variant="caption" sx={{ mt: 1, display: 'block' }}>
                      Unable to connect to backend server. Please ensure the server is running.
                    </Typography>
                  )}
                </InputArea>
              </ChatContainer>
            ) : (
              <Documents />
            )}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
