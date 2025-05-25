# Mini-RAG App Enhancements

## Recent Enhancements

### 1. Document Source Verification
- Added source information display in chat responses
- Implemented toggle buttons to show/hide source information
- Special detection for STC.pdf document references

### 2. Dynamic Chart Generation
- Added financial data extraction from AI responses
- Implemented intelligent chart type selection based on data patterns
- Support for currency values, percentages, and time series data
- Multiple chart types: bar, line, pie, and doughnut

### 3. Document Management
- Added document deletion functionality
- Confirmation dialogs to prevent accidental deletion
- Visual feedback during document operations
- API endpoints for document management

### 4. Mobile Responsiveness
- Improved responsive layout for mobile devices
- Added mobile sidebar toggle
- Optimized chart panel for smaller screens
- Better touch interactions for mobile users

## How to Use

### Source Verification
When the AI responds with information from documents, you'll see a "Show Sources" button. Click it to view the source information.

### Dynamic Charts
1. Chat with the AI about financial data, especially from documents like STC.pdf
2. When financial data is detected, charts will automatically appear
3. Use the chart toggle button to show/hide charts
4. Try different chart types using the chart selector

### Document Management
1. Upload documents using the upload button
2. View your documents in the document panel
3. Click on a document to focus on it for questions
4. Delete documents using the delete button when needed

### Mobile Usage
1. Use the menu toggle (☰) to access the sidebar on mobile
2. Charts will appear at the bottom of the screen
3. Portrait mode is optimized for better reading

## Testing
To verify STC.pdf document focus is working correctly:
1. Upload the STC.pdf document
2. Focus on it by clicking in the document list
3. Ask specific questions about STC company financials
4. Check if the responses include source information buttons
5. Verify that charts are generated with accurate financial data

## Future Improvements
- Add document comparison functionality
- Support for multiple document focus
- Enhanced data visualization options
- Export chart data to CSV/Excel 