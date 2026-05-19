import React from 'react';
import { Paper, Box, Typography, Divider } from '@mui/material';
import { styled } from '@mui/material/styles';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MessagePaper = styled(Paper)(({ theme, role }) => ({
  padding: theme.spacing(2.5),
  marginBottom: theme.spacing(2),
  maxWidth: '85%',
  backgroundColor: role === 'user' ? theme.palette.primary.main : theme.palette.background.paper,
  color: role === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
  alignSelf: role === 'user' ? 'flex-end' : 'flex-start',
  borderRadius: theme.spacing(2),
  boxShadow: role === 'user' 
    ? '0 2px 8px rgba(25, 118, 210, 0.2)' 
    : '0 2px 8px rgba(0, 0, 0, 0.08)',
  border: role === 'user' ? 'none' : `1px solid ${theme.palette.divider}`,
  '& pre': {
    margin: 0,
    padding: theme.spacing(2),
    borderRadius: theme.spacing(1),
    backgroundColor: '#2d2d2d',
    border: '1px solid rgba(0,0,0,0.1)',
  },
  '& code': {
    backgroundColor: role === 'user' ? 'rgba(255,255,255,0.2)' : theme.palette.grey[100],
    padding: '3px 6px',
    borderRadius: 4,
    color: role === 'user' ? 'inherit' : theme.palette.text.primary,
    fontFamily: 'monospace',
  },
}));

const components = {
  code({ node, inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    return !inline && match ? (
      <SyntaxHighlighter
        style={atomDark}
        language={match[1]}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    ) : (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

function Message({ message }) {
  // Check if the message has ticket information (from similar tickets)
  const isSystemWithTickets = message.role === 'system' && 
                             message.content && 
                             message.content.includes('**Similar tickets found:**');

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
      }}
    >
      <MessagePaper role={message.role} elevation={1}>
        <Typography component="div">
          <ReactMarkdown components={components}>
            {message.content}
          </ReactMarkdown>
        </Typography>

        {/* If this is a message with tickets attached, display ticket details */}
        {isSystemWithTickets && message.tickets && message.tickets.length > 0 && (
          <Box sx={{ 
            mt: 2, 
            pt: 2, 
            borderTop: '1px solid',
            borderColor: 'divider'
          }}>
            <Typography variant="subtitle2" fontWeight="600" mb={1.5} color="primary.main">
              Similar Tickets:
            </Typography>
            {message.tickets.map((ticket, idx) => {
              // Check if this is a document or ticket
              const isDocument = ticket.document_type === 'support_document';
              
              // Get ticket number (Excel column "Number" becomes "number" in lowercase after ingestion)
              const ticketNumber = ticket.number || ticket.Number;
              
              const title = ticket.short_description || ticket.title || ticket.description?.substring(0, 50) || ticket.filename || 'No Title';
              const status = ticket.state || ticket.status;
              
              return (
                <Box 
                  key={idx} 
                  sx={{ 
                    mb: 1.5, 
                    p: 1.5,
                    borderLeft: '3px solid',
                    borderColor: isDocument ? 'success.main' : 'primary.main',
                    bgcolor: isDocument ? 'rgba(46, 125, 50, 0.04)' : 'rgba(25, 118, 210, 0.04)',
                    borderRadius: 1,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    {isDocument ? (
                      <Typography variant="caption" sx={{ 
                        bgcolor: 'success.main', 
                        color: 'white', 
                        px: 1, 
                        py: 0.25, 
                        borderRadius: 0.5,
                        fontWeight: 600 
                      }}>
                        DOCUMENT
                      </Typography>
                    ) : ticketNumber && (
                      <Typography variant="caption" sx={{ 
                        bgcolor: 'primary.main', 
                        color: 'white', 
                        px: 1, 
                        py: 0.25, 
                        borderRadius: 0.5,
                        fontWeight: 600 
                      }}>
                        #{ticketNumber}
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="body2" fontWeight="600" color="text.primary">
                    {title}
                  </Typography>
                  {status && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      Status: {status}
                    </Typography>
                  )}
                </Box>
              );
            })}
          </Box>
        )}
      </MessagePaper>
    </Box>
  );
}

export default Message;
