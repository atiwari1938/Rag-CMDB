import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  TextField,
  CircularProgress,
  Alert
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AttachmentIcon from '@mui/icons-material/Attachment';
import { styled } from '@mui/material/styles';

const DocumentsContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  margin: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.spacing(2),
  height: 'calc(100vh - 140px)',
  overflow: 'auto',
  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
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

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching documents from API...');
      const response = await fetch('http://localhost:5000/api/documents');
      console.log('Response status:', response.status);
      
      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.success) {
        console.log('Documents loaded:', data.documents);
        setDocuments(data.documents || []);
      } else {
        setError('Failed to load documents: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Error connecting to server: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event) => {
    setUploadFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!uploadFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      // Replace with your actual upload endpoint
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        fetchDocuments(); // Refresh the document list
        setUploadFile(null);
      } else {
        setError('Upload failed: ' + (data.message || ''));
      }
    } catch (err) {
      console.error('Error uploading document:', err);
      setError('Error uploading document');
    } finally {
      setUploading(false);
    }
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown';
    // Handle Unix timestamp (seconds) or milliseconds
    const date = new Date(timestamp > 10000000000 ? timestamp : timestamp * 1000);
    return date.toLocaleString();
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Typography 
        variant="h4" 
        component="h1" 
        gutterBottom 
        sx={{ 
          p: 2, 
          fontWeight: 600,
          color: 'text.primary'
        }}
      >
        Team Documents
      </Typography>

      <DocumentsContainer elevation={3}>
        {error && (
          <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ 
          mb: 3, 
          p: 3, 
          border: '2px dashed',
          borderColor: 'primary.light',
          borderRadius: 2,
          bgcolor: 'rgba(25, 118, 210, 0.02)'
        }}>
          <Typography variant="h6" gutterBottom fontWeight="600" color="primary.main">
            Upload New Document
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="contained"
              component="label"
              startIcon={<UploadFileIcon />}
              sx={{
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                textTransform: 'none',
                fontWeight: 500,
              }}
            >
              Select File
              <input
                type="file"
                hidden
                onChange={handleFileChange}
              />
            </Button>
            {uploadFile && (
              <Typography variant="body2" sx={{ flex: 1, color: 'text.primary' }}>
                {uploadFile.name}
              </Typography>
            )}
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={!uploadFile || uploading}
              sx={{
                textTransform: 'none',
                fontWeight: 500,
              }}
            >
              {uploading ? <CircularProgress size={24} color="inherit" /> : 'Upload'}
            </Button>
          </Box>
        </Box>

        <Typography variant="h6" gutterBottom fontWeight="600" color="text.primary">
          Available Documents {!loading && `(${documents.length})`}
        </Typography>

        {error && (
          <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : documents.length === 0 ? (
          <Box>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
              No documents available. Upload your first document above.
            </Typography>
            <Button 
              variant="text" 
              onClick={fetchDocuments}
              sx={{ mt: 2 }}
            >
              Retry Loading
            </Button>
          </Box>
        ) : (
          <List sx={{ bgcolor: 'background.default', borderRadius: 2, p: 1 }}>
            {documents.map((doc, index) => (
              <React.Fragment key={doc.id || index}>
                <ListItem 
                  button
                  sx={{
                    borderRadius: 1,
                    mb: 0.5,
                    '&:hover': {
                      bgcolor: 'rgba(25, 118, 210, 0.08)',
                    }
                  }}
                >
                  <ListItemIcon>
                    <DescriptionIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={doc.filename || doc.name || 'Unknown'}
                    secondary={
                      <>
                        {`Uploaded: ${formatDate(doc.uploaded_at || doc.created_at)}`}
                        {doc.size && ` • ${formatFileSize(doc.size)}`}
                      </>
                    }
                    primaryTypographyProps={{
                      fontWeight: 500,
                      color: 'text.primary'
                    }}
                    secondaryTypographyProps={{
                      color: 'text.secondary'
                    }}
                  />
                </ListItem>
                {index < documents.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </DocumentsContainer>
    </Box>
  );
}

export default Documents;
