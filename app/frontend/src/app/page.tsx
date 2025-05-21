'use client';
import { useState, useRef, useEffect } from 'react';
import {  Box,
  Container,
  Paper,
  Typography,
  TextField,
  IconButton,
  AppBar,
  Toolbar,
  Button,
  CircularProgress,
  useTheme,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Divider,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Tooltip,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import {
  Send as SendIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  Search as SearchIcon,
  Upload as UploadIcon,
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  KeyboardArrowDown as ScrollDownIcon,
} from '@mui/icons-material';
import { grey } from '@mui/material/colors';

interface Message {
  id: number;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  error?: boolean;
}

// Add new interfaces for upload components
interface UploadState {
  loading: boolean;
  error: string | null;
  success: string | null;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'info' | 'error' | 'success';
  }>({ open: false, message: '', severity: 'info' });
  const messageListRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [uploadState, setUploadState] = useState<UploadState>({
    loading: false,
    error: null,
    success: null,
  });
  const [uploadUrl, setUploadUrl] = useState('');
  const [showUrlDialog, setShowUrlDialog] = useState(false);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#2196f3',
      },
      background: {
        default: darkMode ? grey[900] : grey[100],
        paper: darkMode ? grey[800] : '#fff',
      },
    },
  });

  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleScroll = () => {
      if (messageListRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = messageListRef.current;
        const isBottom = scrollHeight - scrollTop - clientHeight < 100;
        setShowScrollButton(!isBottom);
      }
    };

    messageListRef.current?.addEventListener('scroll', handleScroll);
    return () => messageListRef.current?.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMessage: Message = {
      id: Date.now(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/agno_ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputMessage,
          session_id: `session-${Date.now()}`,
          user_id: 'default-user'
        }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      const assistantMessage: Message = {
        id: Date.now(),
        content: data.answer,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now(),
        content: 'Sorry, there was an error processing your request.',
        role: 'assistant',
        timestamp: new Date(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
      setNotification({
        open: true,
        message: 'Error processing your request. Please try again.',
        severity: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async (messageIndex: number) => {
    if (messageIndex < 0 || !messages[messageIndex]) return;

    const messageToRetry = messages[messageIndex];
    setMessages(messages.slice(0, messageIndex + 1));
    setIsLoading(true);

    try {
      const response = await fetch('/agno_ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: messageToRetry.content,
          session_id: `session-${Date.now()}`,
          user_id: 'default-user'
        }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      const assistantMessage: Message = {
        id: Date.now(),
        content: data.answer,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now(),
        content: 'Sorry, there was an error processing your request.',
        role: 'assistant',
        timestamp: new Date(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
      setNotification({
        open: true,
        message: 'Error retrying the message. Please try again.',
        severity: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadState({ loading: true, error: null, success: null });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/upload/file', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        setUploadState({
          loading: false,
          error: null,
          success: `File ${file.name} uploaded successfully!`
        });
        setNotification({
          open: true,
          message: data.message,
          severity: 'success'
        });
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      setUploadState({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to upload file',
        success: null
      });
      setNotification({
        open: true,
        message: error instanceof Error ? error.message : 'Failed to upload file',
        severity: 'error'
      });
    }
  };

  const handleUrlUpload = async () => {
    if (!uploadUrl) return;

    setUploadState({ loading: true, error: null, success: null });

    try {
      const response = await fetch('/upload/url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: uploadUrl }),
      });

      const data = await response.json();
      
      if (data.success) {
        setUploadState({
          loading: false,
          error: null,
          success: 'URL document added successfully!'
        });
        setNotification({
          open: true,
          message: data.message,
          severity: 'success'
        });
        setShowUrlDialog(false);
        setUploadUrl('');
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      setUploadState({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to process URL',
        success: null
      });
      setNotification({
        open: true,
        message: error instanceof Error ? error.message : 'Failed to process URL',
        severity: 'error'
      });
    }
  };

  const filteredMessages = messages.filter(message =>
    message.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100vh',
          maxWidth: '1200px', // Add max width
          margin: '0 auto', // Center the container
          width: '100%', // Take full width up to max-width
          boxShadow: '0px 0px 10px rgba(0,0,0,0.1)', // Add subtle shadow
        }}
      >
        <AppBar position="static" color="default" elevation={1}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              AgenticRAG Assistant
            </Typography>
            <Tooltip title="Search messages">
              <IconButton onClick={() => setIsSearchOpen(!isSearchOpen)}>
                <SearchIcon />
              </IconButton>
            </Tooltip>            <Tooltip title="Upload document">
              <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
                <UploadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Toggle dark mode">
              <IconButton onClick={() => setDarkMode(!darkMode)}>
                {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Tooltip>
          </Toolbar>
          {isSearchOpen && (
            <Box sx={{ p: 1, bgcolor: 'background.paper' }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search messages..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                variant="outlined"
              />
            </Box>
          )}
        </AppBar>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          <MenuItem component="label">
            Upload File
            <input
              type="file"
              hidden
              onChange={(e) => {
                setAnchorEl(null);
                handleFileUpload(e);
              }}
              accept=".pdf"
            />
          </MenuItem>
          <MenuItem onClick={() => {
            setAnchorEl(null);
            setShowUrlDialog(true);
          }}>
            Upload from URL
          </MenuItem>
        </Menu>

        <Dialog open={showUrlDialog} onClose={() => setShowUrlDialog(false)}>
          <DialogTitle>Upload Document from URL</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Enter the URL of a PDF document to add to the knowledge base.
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              label="Document URL"
              type="url"
              fullWidth
              variant="outlined"
              value={uploadUrl}
              onChange={(e) => setUploadUrl(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowUrlDialog(false)}>Cancel</Button>
            <Button
              onClick={handleUrlUpload}
              disabled={!uploadUrl || uploadState.loading}
              startIcon={uploadState.loading ? <CircularProgress size={20} /> : null}
            >
              Upload
            </Button>
          </DialogActions>
        </Dialog>

        {/* Loading indicator */}
        {uploadState.loading && (
          <Box
            sx={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 9999,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              bgcolor: 'background.paper',
              p: 3,
              borderRadius: 2,
              boxShadow: 3,
            }}
          >
            <CircularProgress />
            <Typography>Processing document...</Typography>
          </Box>
        )}        <Box
          ref={messageListRef}
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 3,
            bgcolor: 'background.default',
            mx: 'auto', // Center horizontally
            width: '100%', // Take full width
            maxWidth: '900px', // Max width for messages
          }}
        >
          {filteredMessages.length === 0 && !searchQuery && (            <Paper
              elevation={3}
              sx={{
                p: 4,
                textAlign: 'center',
                bgcolor: 'background.paper',
                borderRadius: 3,
                maxWidth: '600px',
                margin: '40px auto',
                boxShadow: theme => `0 8px 32px ${theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.1)'}`,
              }}
            >
              <Typography variant="h6">
                👋 Hi! I'm here to help you with your documents.
              </Typography>
              <Typography color="textSecondary">
                What would you like to know?
              </Typography>
            </Paper>
          )}

          {filteredMessages.map((message, index) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >              <Paper
                elevation={1}
                sx={{
                  p: 2.5,
                  maxWidth: '80%',
                  bgcolor: message.role === 'user' ? 'primary.main' : 'background.paper',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  borderRadius: 2,
                  boxShadow: 2,
                  position: 'relative',
                  '&::after': message.role === 'user' ? {
                    content: '""',
                    position: 'absolute',
                    right: '-10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    border: '10px solid transparent',
                    borderLeftColor: 'primary.main',
                  } : {
                    content: '""',
                    position: 'absolute',
                    left: '-10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    border: '10px solid transparent',
                    borderRightColor: 'background.paper',
                  },
                  ...(message.error && {
                    borderColor: 'error.main',
                    borderWidth: 1,
                    borderStyle: 'solid',
                  }),
                }}
              >
                <Typography
                  variant="body1"
                  sx={{
                    wordBreak: 'break-word',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {message.content}
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mt: 1,
                    pt: 1,
                    borderTop: 1,
                    borderColor: 'divider',
                  }}
                >
                  <Typography variant="caption" color="textSecondary">
                    {message.timestamp.toLocaleTimeString()}
                  </Typography>
                  {message.error && (
                    <Button
                      size="small"
                      onClick={() => handleRetry(index - 1)}
                      disabled={isLoading}
                      startIcon={<IconButton size="small">↻</IconButton>}
                    >
                      Retry
                    </Button>
                  )}
                </Box>
              </Paper>
            </Box>
          ))}

          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', m: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Box>

        {showScrollButton && (
          <Box sx={{ position: 'fixed', right: 24, bottom: 90 }}>
            <Tooltip title="Scroll to bottom">
              <IconButton
                onClick={scrollToBottom}
                sx={{
                  bgcolor: 'background.paper',
                  boxShadow: 2,
                  '&:hover': { bgcolor: 'action.hover' },
                }}
              >
                <ScrollDownIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}        <Paper
          component="form"
          onSubmit={handleSendMessage}
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            mx: 'auto', // Center horizontally
            width: '100%',
            maxWidth: '900px', // Match message container width
          }}
        >
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              variant="outlined"
              size="small"
              disabled={isLoading}
              multiline
              maxRows={4}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={isLoading || !inputMessage.trim()}
              sx={{ minWidth: 100 }}
              endIcon={<SendIcon />}
            >
              Send
            </Button>
          </Box>
        </Paper>

        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={() => setNotification({ ...notification, open: false })}
        >
          <Alert
            severity={notification.severity}
            onClose={() => setNotification({ ...notification, open: false })}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}
