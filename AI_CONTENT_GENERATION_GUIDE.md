# AI Content Generation System Guide

## Overview

The AI Content Generation system creates high-quality, research-driven content in multiple formats. It extracts keywords from Google Docs, conducts research, and generates content like blog posts, articles, social media content, and more as downloadable Word documents.

## Features

### Content Types Supported
- **Blog Posts**: Engaging web articles (800-2500 words)
- **In-depth Articles**: Comprehensive analysis pieces (1000-4000 words)
- **Social Media Content**: Platform-optimized posts and campaigns
- **Marketing Copy**: Conversion-focused ads and landing pages
- **Whitepapers**: Authoritative research documents
- **Email Campaigns**: Multi-email nurture sequences
- **Press Releases**: Media-ready announcements
- **Case Studies**: Business success stories

### Content Customization
- **Tone Options**: Professional, Casual, Authoritative, Conversational, Technical, Creative, Formal, Enthusiastic
- **Length Options**: Short, Medium, Long (varies by content type)
- **Target Audiences**: General, Business Professionals, Marketers, Executives, Academics, Technical Experts, Consumers, Industry Specialists
- **Additional Instructions**: Custom requirements and guidelines

### Research Integration
- Automatic keyword extraction from Google Docs
- Google Scholar research integration
- Research paper analysis and synthesis
- Marketing relevance analysis
- Citation and reference inclusion

## Setup Instructions

### Prerequisites

1. **Python Dependencies**
   ```bash
   pip install flask python-docx openai google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **Environment Variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **Google OAuth Setup** (see OAUTH_SETUP.md)
   - Set up credentials.json file
   - Configure OAuth consent screen
   - Enable Google Docs and Drive APIs

### Verification

Run the test script to verify everything is working:
```bash
python test_ai_content_generation.py
```

## How to Use

### Step 1: Prepare Your Google Doc

1. Create a Google Doc with your research topic or initial content
2. Make sure the document contains relevant keywords and topics
3. Share the document or make it accessible
4. Copy the document ID or full URL

### Step 2: Access the AI Content Generator

1. Open your browser and go to `/ai-content` route
2. You'll see the AI Content Generator form

### Step 3: Configure Content Generation

1. **Google Doc Input**: Paste your Google Doc ID or URL
2. **Content Type**: Select from 8 available content types
3. **Tone & Style**: Choose the writing style
4. **Content Length**: Select target length
5. **Target Audience**: Define your audience
6. **Additional Instructions**: Add specific requirements (optional)

### Step 4: Generate Content

1. Click "Generate AI Content" button
2. Monitor progress on the progress page
3. The system will:
   - Extract keywords from your Google Doc
   - Conduct research based on keywords
   - Analyze research for insights
   - Generate AI content based on specifications
   - Create a comprehensive Word document

### Step 5: Download Results

1. Once complete, you'll see the results page
2. Download your generated Word document
3. The document includes:
   - Generated content
   - Document metadata
   - Research keywords used
   - Research foundation
   - Generation details

## Content Generation Process

### 1. Keyword Extraction
- Advanced OpenAI-powered keyword extraction
- Primary keywords, research topics, business terms
- Marketing-focused keyword analysis

### 2. Research Phase
- Google Scholar paper search
- Research paper filtering and ranking
- PDF content extraction when available
- Academic analysis and synthesis

### 3. Content Creation
- Research-driven content generation
- Tone and audience optimization
- Structured content with proper formatting
- Citation and reference integration

### 4. Document Creation
- Professional Word document formatting
- Comprehensive metadata tables
- Multi-section document structure
- Research foundation appendix

## Content Templates

### Blog Post Structure
1. Magnetic headline
2. Compelling introduction (10%)
3. 3-4 main sections with subheadings (70%)
4. Practical action steps (15%)
5. Strong conclusion with CTA (5%)

### Article Structure
1. Compelling title
2. Executive summary
3. Detailed analysis sections
4. Data and statistics integration
5. Actionable recommendations
6. Citations and references

### Social Media Content
- Platform-specific optimization
- Engaging hooks and CTAs
- Hashtag recommendations
- Multiple post variations
- Engagement strategies

## Best Practices

### For Better Results
1. **Detailed Source Documents**: Provide comprehensive Google Docs with relevant context
2. **Specific Instructions**: Use the additional instructions field for specific requirements
3. **Appropriate Length**: Choose length that matches your content goals
4. **Target Audience**: Be specific about your audience for better targeting

### Content Quality Tips
- Include statistics and examples in your source doc
- Mention specific competitors or industry leaders
- Add real-world use cases and scenarios
- Specify calls-to-action you want included
- Include any required compliance or legal language

## Troubleshooting

### Common Issues

**"Google File ID is required"**
- Ensure you've provided a valid Google Doc URL or ID
- Check document permissions

**"OpenAI API key not configured"**
- Set the OPENAI_API_KEY environment variable
- Verify the API key is valid

**"Failed to authenticate with Google OAuth"**
- Check credentials.json file exists
- Verify OAuth setup (see OAUTH_SETUP.md)
- Ensure document is accessible

**"No content generated"**
- Check if source document has enough content
- Verify OpenAI API is responding
- Try with different content type or parameters

### Performance Tips
- Longer content takes more time to generate
- Research-heavy topics may take 5-15 minutes
- Social media content is typically fastest
- Whitepapers take the longest due to length

## File Structure

Generated documents follow this naming convention:
```
ai_generated_[content_type]_[timestamp].docx
```

Document structure:
1. Title page with content type
2. Document information table
3. Research keywords section
4. Generated content (main body)
5. Research foundation appendix
6. Generation details

## API Integration

For programmatic use, the system provides these endpoints:

- `POST /ai-content/generate` - Start content generation
- `GET /ai-content/progress/{task_id}` - Check progress
- `GET /ai-content/results/{task_id}` - View results
- `GET /api/ai-content/status/{task_id}` - Get status JSON
- `GET /download/{filename}` - Download generated document

## Advanced Features

### Research Integration
- Automatic academic paper discovery
- Citation quality scoring
- Business relevance analysis
- Marketing insight extraction

### Content Optimization
- SEO-friendly structure
- Readability optimization
- Audience-specific language
- Call-to-action integration

### Document Features
- Professional formatting
- Metadata tracking
- Research citations
- Quality metrics
- Generation audit trail

## Support

For issues or feature requests:
1. Check the troubleshooting section above
2. Run the test script to verify setup
3. Check application logs for detailed error messages
4. Ensure all dependencies are properly installed

## Changelog

### Latest Updates
- Enhanced keyword extraction with OpenAI
- Improved Word document formatting
- Added comprehensive content templates
- Research integration improvements
- Better error handling and logging 