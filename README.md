# SJSU King Library Finals Week Email Template

## Overview
This is a responsive, production-ready HTML email template for recruiting volunteers and donors for SJSU King Library Finals Week events. The template is designed to be reusable with personalization and easy swaps for dates, signers, and links.

## Files
- `finals_week_template.html` - Complete HTML email template with inline styles
- `finals_week_template.txt` - Plain text fallback version

## Subject Line Options

### Option 1
**Subject:** Help us bring Finals Week to life — just 4 hours makes a difference  
**Preheader:** Join us Dec 9–10 & May 12–13 at King Library.

### Option 2
**Subject:** Two evenings. Big impact for students. Are you in?  
**Preheader:** Volunteer 7–10 PM with refreshments, activities, and support.

## Audience Variants
The template is designed to work with three audience variants by adjusting the greeting and sign-off language:

1. **Faculty & Instructors** - Use "Colleague," in greeting
2. **Student Services & Staff** - Use "Team," in greeting  
3. **Deans/Department Leaders** - Use "Dean [LastName]," in greeting

## Personalization Tokens
- `[[FirstName|Colleague]]` - Greeting personalization
- `[[SignerName|Your Name]]` - Signer's name
- `[[SignerTitle|Title]]` - Signer's title

## Key Features
- **Responsive Design**: 640px max width, mobile-optimized
- **Email Client Compatibility**: Gmail, Outlook, Apple Mail, mobile clients
- **Table-based Layout**: Nested tables with inline styles only
- **VML Support**: Bulletproof buttons for Outlook compatibility
- **Accessibility**: Proper contrast, alt text, semantic roles
- **Dark Theme**: Deep navy backgrounds (#0b1220, #0e1a33) with light text

## Customization Points
All editable variables are clearly marked at the top of the HTML file:
- Organization details
- Contact information
- URLs (RSVP form, video, images)
- Dates and event details
- Signer information

## How to Use
1. Replace placeholder URLs with actual URLs
2. Update merge fields for personalization
3. Modify dates as needed for future semesters
4. Update signer information
5. Test across email clients before sending

## Technical Requirements Met
- ✅ Table-based layout with nested tables
- ✅ Inline CSS only (no external stylesheets)
- ✅ VML fallbacks for Outlook buttons
- ✅ Responsive design with mobile breakpoints
- ✅ Web-safe fonts (Arial/Helvetica)
- ✅ Proper contrast ratios for accessibility
- ✅ Alt text on all images
- ✅ Target="_blank" for external links
- ✅ Merge field syntax for personalization
