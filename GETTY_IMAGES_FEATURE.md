# Getty Images Integration Feature

## Overview

The WordPress Blog Automation Suite now includes an option to use Getty Images editorial content instead of (or alongside) OpenAI-generated images. This feature allows users to choose between three image options:

1. **No Images** - Skip image processing entirely
2. **OpenAI DALL-E** - Generate AI images (requires API key)
3. **Getty Images Editorial** - Use professional editorial images (no API key required)

## How It Works

### Getty Images Search Process

1. **Topic Extraction**: The system extracts keywords from the article title and SEO keyphrases
2. **Image Search**: Searches Getty Images editorial collection for relevant images
3. **Content Integration**: Automatically embeds selected images using Getty's standard embed code
4. **Proper Attribution**: Maintains Getty Images' licensing and attribution requirements

### Technical Implementation

#### New Functions Added

```python
def search_getty_images(self, query: str, num_results: int = 5) -> List[Dict[str, str]]
```
- Searches Getty Images based on provided query
- Returns list of image data including IDs, titles, and embed URLs
- Handles pagination and error cases

```python
def get_getty_embed_code(self, image_id: str, title: str) -> str
```
- Generates Getty Images standard embed code
- Includes proper styling and attribution
- Returns HTML iframe embed code

```python
def add_getty_image_to_content(self, content: str, title: str, topic_keywords: List[str] = None) -> str
```
- Integrates Getty Images into article content
- Smart placement after headings or first paragraph
- Uses article keywords for relevant image selection

### GUI Changes

The settings section now includes a radio button group for image source selection:

```
Featured Images
○ No Images
○ Generate with OpenAI DALL-E
○ Getty Images Editorial
```

### Integration with Existing Workflow

The Getty Images feature seamlessly integrates with the existing article processing workflow:

1. **Step 6**: Extract keyphrases for SEO (used for image search)
2. **Step 7**: Process images based on selected source
   - If "Getty Images" selected: Search and embed Getty images into content
   - If "OpenAI" selected: Generate featured image (existing functionality)
   - If "None" selected: Skip image processing
3. **Continue**: Normal WordPress posting process

## Benefits

### For Users
- **No API Key Required**: Getty Images option doesn't need any additional API setup
- **Professional Quality**: Access to Getty's editorial image collection
- **Proper Licensing**: Uses Getty's embed system for legitimate usage
- **Automatic Integration**: Images are automatically placed in article content
- **Flexible Options**: Choose the best image source for each use case

### For Content
- **Relevant Images**: Smart keyword-based search ensures topical relevance
- **Editorial Quality**: Professional sports photography and editorial images
- **SEO Benefits**: Images with proper alt text and descriptions
- **User Engagement**: Visual content improves article appeal

## Technical Details

### Error Handling
- Graceful fallback if Getty Images search fails
- Continued processing without images if service unavailable
- Comprehensive logging for debugging

### Content Placement
- Smart insertion after first paragraph or heading
- Maintains article flow and readability
- Responsive embed code for all device types

### Search Strategy
- Uses article title as primary search query
- Incorporates SEO keyphrases for specificity
- Limits results to prevent overwhelming content

## Example Usage

For an article titled "Manchester United vs Liverpool Match Report" with keywords like "Premier League" and "football":

1. **Search Query**: "Manchester United Premier League football"
2. **Getty Search**: Finds relevant match photos, player images, or stadium shots
3. **Selection**: Chooses most relevant editorial image
4. **Integration**: Embeds image after article introduction
5. **Result**: Professional-quality image enhances article content

## Configuration

No additional configuration required for Getty Images:
- Works out of the box
- No API keys needed
- No rate limits (within reasonable usage)
- Uses public Getty Images embed system

## Future Enhancements

Potential future improvements:
- Image selection preferences (action shots, portraits, etc.)
- Multiple image insertion per article
- Custom positioning options
- Integration with Getty Images API for enhanced features

## Support

Getty Images functionality is fully integrated into the existing logging and error handling system. All actions are logged for troubleshooting and monitoring.
