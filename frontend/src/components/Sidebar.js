import React, { useState, useEffect } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Box,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  Description as DocumentIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';

const DRAWER_WIDTH = 280;

function Sidebar({ documents = [] }) {
  const [isDocsOpen, setIsDocsOpen] = useState(true);
  const [uploadedDocs, setUploadedDocs] = useState([]);

  useEffect(() => {
    // Fetch the list of uploaded documents
    const fetchDocuments = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/documents');
        const data = await response.json();
        setUploadedDocs(data.documents);
      } catch (error) {
        console.error('Error fetching documents:', error);
      }
    };

    fetchDocuments();
  }, []);

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      <Box sx={{ overflow: 'auto', mt: 8 }}>
        <List>
          <ListItem button onClick={() => setIsDocsOpen(!isDocsOpen)}>
            <ListItemIcon>
              <DocumentIcon />
            </ListItemIcon>
            <ListItemText primary="Uploaded Documents" />
            {isDocsOpen ? <ExpandLess /> : <ExpandMore />}
          </ListItem>
          <Collapse in={isDocsOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {uploadedDocs.map((doc, index) => (
                <ListItem button key={index} sx={{ pl: 4 }}>
                  <ListItemIcon>
                    <DocumentIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={doc.filename}
                    secondary={`Uploaded: ${new Date(doc.uploaded_at).toLocaleDateString()}`}
                  />
                </ListItem>
              ))}
              {uploadedDocs.length === 0 && (
                <ListItem sx={{ pl: 4 }}>
                  <ListItemText
                    secondary="No documents uploaded yet"
                    sx={{ color: 'text.secondary' }}
                  />
                </ListItem>
              )}
            </List>
          </Collapse>
        </List>
        <Divider />
      </Box>
    </Drawer>
  );
}

export default Sidebar;
