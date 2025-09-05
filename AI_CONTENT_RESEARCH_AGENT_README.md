# AI Content Research Agent

## Overview

The **AI Content Research Agent** is a comprehensive Python library that combines the research capabilities of the Google Scholar Research Agent with advanced AI-powered content generation. It creates high-quality, research-driven content in multiple formats and generates professional Word documents.

## 🚀 Key Features

### Research Integration
- **Google Scholar Integration**: Automatically searches and analyzes academic papers
- **Advanced Keyword Extraction**: Uses OpenAI for sophisticated keyword analysis
- **Research Synthesis**: Combines findings from multiple sources into coherent insights
- **Citation Management**: Automatically includes relevant citations and references

### Content Generation
- **8 Content Types**: Blog posts, articles, social media, marketing copy, whitepapers, email campaigns, press releases, case studies
- **Customizable Parameters**: Tone, length, target audience, and specific instructions
- **Research-Driven**: Content is based on actual research findings and academic insights
- **Quality Scoring**: Automatic quality assessment with detailed metrics

### Document Creation
- **Professional Word Documents**: Comprehensive documents with proper formatting
- **Multiple Sections**: Title page, executive summary, metadata, content, research appendix
- **Visual Elements**: Tables, headings, bullet points, and structured layouts
- **Download Ready**: Immediate download of generated documents

## 📦 Installation

### Prerequisites

```bash
# Install required Python packages
pip install openai python-docx google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Set environment variable
export OPENAI_API_KEY="your-openai-api-key"
```

### Setup

1. **Download the files**:
   - `ai_content_research_agent.py` - Main agent class
   - `google_scholar_research_agent.py` - Research capabilities (existing)
   - `test_ai_content_research_agent.py` - Test script
   - `example_ai_content_usage.py` - Usage examples

2. **Configure Google OAuth** (optional, for enhanced research):
   - Set up `credentials.json` for Google API access
   - See `OAUTH_SETUP.md` for detailed instructions

3. **Test the installation**:
   ```bash
   python test_ai_content_research_agent.py
   ```

## 🎯 Quick Start

### Basic Usage

```python
from ai_content_research_agent import AIContentResearchAgent, ContentSpecification

# Initialize the agent
agent = AIContentResearchAgent()

# Define content specifications
content_spec = ContentSpecification(
    content_type="blog_post",
    content_tone="professional", 
    content_length="medium",
    target_audience="business_professionals",
    additional_instructions="Focus on practical implementation"
)

# Run complete pipeline from Google Doc to final content
result = agent.run_complete_content_pipeline(
    google_file_id="your-google-doc-id",
    content_spec=content_spec
)

if result['success']:
    print(f"Content generated: {result['document_result']['filename']}")
else:
    print(f"Error: {result['error']}")
```

### Step-by-Step Process

```python
# 1. Extract keywords from Google Document
keywords_data = agent.extract_keywords_from_google_file("your-doc-id")

# 2. Conduct research based on keywords
papers = agent.conduct_research(keywords_data, max_papers=10)

# 3. Analyze research for content generation
research_analysis = agent.analyze_research_for_content(papers, keywords_data)

# 4. Generate AI content
content_result = agent.generate_content(keywords_data, research_analysis, content_spec)

# 5. Create comprehensive Word document
document_result = agent.create_comprehensive_document(
    content_result, keywords_data, research_analysis, content_spec
)
```

## 📝 Content Types and Specifications

### Supported Content Types

| Type | Description | Word Count Range |
|------|-------------|------------------|
| `blog_post` | SEO-optimized web articles | 800-2500 words |
| `article` | In-depth analysis pieces | 1000-4000 words |
| `social_media` | Platform-optimized content | Platform-specific |
| `marketing_copy` | Conversion-focused copy | Variable |
| `whitepaper` | Authoritative research docs | 2000-8000 words |
| `email_campaign` | Multi-email sequences | 3-7 emails |
| `press_release` | Media-ready announcements | Standard format |
| `case_study` | Business success stories | 1500-3000 words |

### Content Customization Options

**Tone Options**:
- `professional` - Business-focused
- `casual` - Friendly and approachable
- `authoritative` - Expert voice
- `conversational` - Natural dialogue
- `technical` - Detailed and precise
- `creative` - Imaginative and unique
- `formal` - Traditional business
- `enthusiastic` - Energetic and exciting

**Length Options**:
- `short` - Concise format
- `medium` - Standard length
- `long` - Comprehensive coverage

**Target Audiences**:
- `general` - Broad appeal
- `business_professionals` - Corporate focus
- `marketers` - Marketing-specific
- `executives` - Leadership level
- `academics` - Research community
- `technical_experts` - Specialized knowledge
- `consumers` - End customers
- `industry_specialists` - Sector-specific

## 🔍 Research Integration

### Google Scholar Integration

The agent automatically:
1. Extracts keywords from your source document
2. Searches Google Scholar for relevant papers
3. Filters and ranks papers by relevance
4. Downloads and analyzes full-text content when available
5. Synthesizes findings into actionable insights

### Research Quality Levels

- **High**: Multiple research papers analyzed with full-text access
- **Medium**: Some papers found with abstract analysis
- **Keyword-based**: Content generated using keyword analysis and best practices

## 📄 Document Structure

Generated Word documents include:

1. **Title Page**: Professional cover with content type and generation info
2. **Executive Summary**: Key findings and content overview
3. **Content Specifications**: Detailed metadata table
4. **Research Keywords**: Primary keywords and topics used
5. **Generated Content**: Main content with proper formatting
6. **Research Foundation**: Academic analysis and paper summaries
7. **Generation Details**: Technical details and quality metrics

## 🔧 Flask Integration

### Basic Integration

```python
from flask import Flask
from flask_integration_ai_agent import integrate_with_flask_app, initialize_ai_content_agent

app = Flask(__name__)

# Initialize the agent
initialize_ai_content_agent()

# Integrate with Flask app
integrate_with_flask_app(app)
```

### Enhanced Routes

The agent adds these endpoints to your Flask app:

- `POST /ai-content/generate-enhanced` - Start enhanced content generation
- `GET /api/ai-content-enhanced/status/<task_id>` - Check generation status
- `GET /api/ai-content-agent/status` - Get agent status and capabilities

## 📊 Quality Metrics

The agent provides comprehensive quality assessment:

- **Word Count Appropriateness** (20%): Matches target length
- **Structure Quality** (30%): Headings, lists, paragraphs
- **Research Integration** (25%): Use of research findings
- **Content Richness** (25%): Vocabulary diversity and readability

## 🧪 Testing

### Run Comprehensive Tests

```bash
python test_ai_content_research_agent.py
```

Tests verify:
- Agent initialization
- Content specifications
- Keyword extraction
- Content templates
- Prompt generation
- Quality calculation
- Content generation (if OpenAI configured)

### Example Usage

```bash
python example_ai_content_usage.py
```

Shows practical examples of:
- Blog post generation
- Complete pipeline usage
- Flask integration

## 🔄 Performance

### Generation Times

- **Blog Posts**: 30-60 seconds
- **Articles**: 60-120 seconds
- **Social Media**: 15-30 seconds
- **Whitepapers**: 120-300 seconds

Times vary based on:
- Research complexity
- Content length
- Number of research papers found
- OpenAI API response time

### System Requirements

- **Python**: 3.7+
- **Memory**: 512MB+ recommended
- **Disk Space**: 100MB+ for dependencies
- **Network**: Internet connection for research and AI APIs

## 🛠️ Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional (for enhanced research)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Agent Configuration

```python
agent = AIContentResearchAgent(
    openai_api_key="your-key",  # Or use environment variable
    google_credentials_path="path/to/credentials.json",
    model_name="gpt-4o"  # OpenAI model to use
)
```

## 📈 Statistics and Monitoring

### Generation Statistics

```python
stats = agent.get_generation_statistics()
print(f"Total Generated: {stats['total_generated']}")
print(f"Success Rate: {stats['successful_generations']}/{stats['total_generated']}")
print(f"Average Time: {stats['average_generation_time']:.2f}s")
```

### System Status

```python
status = agent.get_generation_statistics()['system_status']
print(f"OpenAI Available: {status['openai_available']}")
print(f"Research Available: {status['research_agent_available']}")
print(f"Document Creation: {status['document_creation_available']}")
```

## 🚨 Troubleshooting

### Common Issues

**"OpenAI client not available"**
- Set `OPENAI_API_KEY` environment variable
- Verify API key is valid and has credits

**"Research agent not available"**
- Ensure `google_scholar_research_agent.py` is in the same directory
- Check Google OAuth setup for enhanced research

**"Document creation failed"**
- Install `python-docx`: `pip install python-docx`
- Check file permissions in working directory

**"Keyword extraction failed"**
- Verify Google Doc permissions
- Check document ID format
- Ensure OAuth credentials are configured

### Debug Mode

```python
import logging
logging.getLogger('ai_content_research_agent').setLevel(logging.DEBUG)
```

## 🤝 Contributing

### Adding New Content Types

1. Add template configuration in `_load_content_templates()`
2. Create prompt function in `_get_content_type_requirements()`
3. Add system prompt customization in `_get_system_prompt()`
4. Update documentation and tests

### Extending Research Capabilities

1. Modify `conduct_research()` for additional sources
2. Enhance `analyze_research_for_content()` for better synthesis
3. Add new analysis methods to research agent

## 📄 License

This project extends the Google Scholar Research Agent and follows the same licensing terms.

## 🆘 Support

For issues and questions:

1. **Check the troubleshooting section above**
2. **Run the test script**: `python test_ai_content_research_agent.py`
3. **Review the examples**: `python example_ai_content_usage.py`
4. **Check system logs for detailed error messages**

## 🔄 Changelog

### Version 1.0.0
- Initial release with complete research-to-content pipeline
- Support for 8 content types
- Professional Word document generation
- Flask integration capabilities
- Comprehensive quality assessment
- Full test suite and documentation 